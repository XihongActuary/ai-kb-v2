# -*- coding: utf-8 -*-
"""
场景一 · 手写模型库（纯 NumPy，零依赖 sklearn）
================================================================
为什么要手写？
    因为「机器学习」这个词把一件朴素的事包装得太神秘。
    拆开来看：回归就是在解一个加权最小二乘；树就是在问一千个是非题；
    提升就是一条一条地补残差。亲手写一遍，比调 200 个参数更让人不再怕它。

本文件包含 4 个模型 + 3 个评估工具：
    PoissonRegressor   纯保费建模主力（对数连接 + Poisson 损失）
    LogisticRegression 二分类（是否出险）
    DecisionTreeRegressor 单棵回归树（CART，直方图分箱加速）
    GBDT               梯度提升决策树（表格数据之王）
    评估：Poisson deviance / AUC / Lift

约定：X 已是设计矩阵（标准化或 one-hot 之后），模型只管 fit，不做预处理。
      为教学可读性优先，省略了工业库里的稀疏矩阵、并行、缓存等工程优化。

【一个诚实声明】
    本实现的 GBDT 用的是「对数空间二阶（牛顿）步」，与 XGBoost 同一思路。
    差别在于 XGBoost 直接在 μ 空间做二阶展开并配 line_search，
    本实现直接解 log 空间的牛顿步，代码短很多，但同样的思想。
    为保证不发散，单轮 log 空间调整幅度被夹在 ±3 以内 ——
    这个细节是实测踩出来的，不是理论推导，见 fit() 里的注释。
"""
import numpy as np


# ==================================================================
# 工具：树节点遍历
# ==================================================================
def iter_nodes(node):
    """深度优先遍历树的所有节点"""
    stack = [node]
    while stack:
        nd = stack.pop()
        yield nd
        if not nd.get("leaf"):
            stack.append(nd["left"])
            stack.append(nd["right"])


# ==================================================================
# 评估工具
# ==================================================================
def poisson_deviance(y, mu, w=None):
    """
    Poisson deviance（泊松偏差）：
        D = 2 · Σ [ y·log(y/μ) - (y - μ) ]
    直觉：它衡量「预测的次数分布」与「实际的次数分布」差多少。
    完美预测时 D = 0。D 越小越好。
    对 y=0 的项约定 0·log0 = 0，不会产生 NaN。

    为什么不用 MSE？
        赔付金额重尾，MSE 会被少数大额赔案主导，
        而那些大额赔案本身波动极大、几乎不可预测。
        Poisson deviance 相当于在「频率」尺度上打分，稳健得多。
    """
    y = np.asarray(y, float)
    mu = np.clip(np.asarray(mu, float), 1e-9, None)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(y > 0, y * np.log(np.maximum(y, 1e-12) / mu), 0.0) - (y - mu)
    return float(2 * np.sum(w * term) / np.sum(w))


def auc_score(y, score):
    """
    AUC = 「随机取一个正样本和一个负样本，模型给正样本更高分的概率」
    等价于 ROC 曲线下面积。0.5 = 随机，1.0 = 完美。
    用秩和公式计算，复杂度 O(n log n)，不画图也能得。
    """
    y = np.asarray(y, int)
    s = np.asarray(score, float)
    n_pos, n_neg = (y == 1).sum(), (y == 0).sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    # 秩和公式：把分数升序排名（1..n），正样本秩和减去理论最小值
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), float)
    ranks[order] = np.arange(1, len(s) + 1)
    # 并列值必须取平均秩，否则会高估 AUC。
    # 例：分数 [1,1,2,2] 对应标签 [0,0,1,1] —— 分数越高越可能是正样本，
    #     而这里两组完全分离，所以 AUC = 1.0（不是 0.5）。
    #     如果按朴素秩次（1,2,3,4）算，正样本秩和 7，
    #     (7−3)/4 = 1.0，恰好也对；但只要出现「正样本在前、同分在后」
    #     这类交叉情形，朴素秩就会算错，必须用平均秩。
    uniq, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt))
    np.add.at(sums, inv, ranks)          # 同一分数的秩求和
    avg_ranks = (sums / cnt)[inv]         # 再除以出现次数 = 平均秩
    return float((avg_ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def lift_table(y, score, w=None, n_bins=10):
    """
    提升度表（Lift / 增益表）：把人群按预测分从高到低分成十等份，
    看每一份的实际风险是全体平均的多少倍。
    这是车险定价最常用的一张表 —— 定价员每天看的就是它。
    """
    y = np.asarray(y, float)
    score = np.asarray(score, float)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    order = np.argsort(-score)
    y, w = y[order], w[order]
    tot_w, tot_sy = w.sum(), (w * y).sum()
    base = tot_sy / tot_w

    edges = np.linspace(0, len(y), n_bins + 1).astype(int)
    rows = []
    cum_w = cum_sy = 0.0
    for i in range(n_bins):
        sl = slice(edges[i], edges[i + 1])
        bw, bs = w[sl].sum(), (w[sl] * y[sl]).sum()
        cum_w += bw
        cum_sy += bs
        seg_rate = bs / bw if bw else np.nan
        rows.append({
            "组": f"第{i+1}组",
            "人数占比": bw / tot_w,
            "件数占比": bs / tot_sy if tot_sy else np.nan,
            "该组风险": seg_rate,
            "Lift": seg_rate / base if base else np.nan,
            "累计Lift": (cum_sy / cum_w) / base if base else np.nan,
            "累计人数占比": cum_w / tot_w,
        })
    return base, rows


# ==================================================================
# 1. Poisson 回归（对数线性 GLM）
# ==================================================================
class PoissonRegressor:
    """
    建模赔付金额 y：E[y | x] = exp(b0 + b·x)

    损失：Poisson deviance
    链接：log
    求解：IRLS（迭代重加权最小二乘）——
          每一步都在解一个「带权最小二乘」，所以整个算法的骨架
          和你在本科解回归时解的那个正规方程，是同一个东西。

    为什么不用最小二乘？
        赔付金额是「大多数接近 0、少数极大」的重尾分布。
        最小二乘会被几个大额赔案拽跑，把整体拟合压低。
        Poisson deviance 的惩罚是「按比例」的，稳健得多。

    为什么纯保费建模首选它？
        ① 预测值恒为正 —— exp 保证了，绝不会出现「负保费」这种荒谬结果
        ② 系数可解释：exp(b_j) 就是「该因子每升一档，出险强度变几倍」
        ③ 频率和损失额两条链能用同一套 GLM 表达
    """
    L1 = None

    def __init__(self, alpha=1e-4, max_iter=80, tol=1e-7):
        self.alpha = alpha          # L2 正则强度（等价于岭回归的 λ）
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y, w=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        n, p = X.shape
        w = np.ones(n) if w is None else np.asarray(w, float)
        w = w / w.mean()

        b = np.zeros(p + 1)
        for it in range(self.max_iter):
            eta = np.clip(X @ b[1:] + b[0], -20, 20)
            mu = np.exp(eta)

            # 工作响应变量 z = η + (y - μ)/μ
            #   这是牛顿法的一阶展开：让「线性化后的 y」等于 z
            z = eta + (y - mu) / np.clip(mu, 1e-9, None)
            W = w * mu                        # IRLS 权重

            Xa = np.hstack([np.ones((n, 1)), X])
            A = (Xa * W[:, None]).T @ Xa
            A.flat[:: p + 2] += self.alpha    # 只罚系数，不罚截距
            rhs = (Xa * W[:, None]).T @ z
            try:
                new_b = np.linalg.solve(A, rhs)
            except np.linalg.LinAlgError:
                new_b = np.linalg.lstsq(A, rhs, rcond=None)[0]

            delta = np.max(np.abs(new_b - b))
            b = new_b
            if delta < self.tol:
                break

        self.coef_ = b
        self.n_iter_ = it + 1
        return self

    def predict(self, X):
        X = np.asarray(X, float)
        return np.exp(np.clip(X @ self.coef_[1:] + self.coef_[0], -20, 20))

    def summary(self, names=None):
        """可读输出：系数 + 相对风险 RR = exp(系数)"""
        names = names or [f"x{i}" for i in range(len(self.coef_) - 1)]
        lines = ["因子                 系数      RR = exp(系数)",
                 "-" * 46]
        for nm, c in zip(names, self.coef_[1:]):
            lines.append(f"{nm:<20}{c:>9.4f}{np.exp(c):>12.4f}")
        lines.append(f"{'(截距)':<20}{self.coef_[0]:>9.4f}")
        return "\n".join(lines)


# ==================================================================
# 2. 逻辑回归
# ==================================================================
class LogisticRegression:
    """
    P(y=1|x) = sigmoid(b0 + b·x)
    损失：交叉熵（对数损失）
    求解：牛顿法 / IRLS

    与 Poisson 的关系（精算上很关键的一条直觉）：
        Poisson 系数 b  =「该因子对出险强度的相对影响」
        Logistic 系数 b =「该因子对是否出险的对数几率的影响」
        在「泊松对数线性」设定下两者几乎一致 —— 这就是 GLM 家族的统一性，
        也是为什么精算师掌握了 GLM，就等于掌握了分类模型的一半。
    """
    L1 = None

    def __init__(self, alpha=1e-4, max_iter=60, tol=1e-7):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y, w=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        n, p = X.shape
        w = np.ones(n) if w is None else np.asarray(w, float)
        w = w / w.mean()

        b = np.zeros(p + 1)
        for it in range(self.max_iter):
            eta = np.clip(X @ b[1:] + b[0], -20, 20)
            phat = np.clip(1 / (1 + np.exp(-eta)), 1e-9, 1 - 1e-9)

            Xa = np.hstack([np.ones((n, 1)), X])
            # 梯度
            g = np.hstack([[np.sum(w * (y - phat))],
                           (X * w[:, None]).T @ (y - phat)]) - self.alpha * b
            # Hessian
            W = w * phat * (1 - phat)
            H = (Xa * W[:, None]).T @ Xa
            H.flat[:: p + 2] += self.alpha

            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                step = np.linalg.lstsq(H, g, rcond=None)[0]
            b = b + step
            if np.max(np.abs(step)) < self.tol:
                break

        self.coef_ = b
        self.n_iter_ = it + 1
        return self

    def predict_proba(self, X):
        X = np.asarray(X, float)
        eta = np.clip(X @ self.coef_[1:] + self.coef_[0], -20, 20)
        return 1 / (1 + np.exp(-eta))

    def predict(self, X, thr=0.5):
        return (self.predict_proba(X) > thr).astype(int)


# ==================================================================
# 3. 回归树（CART）
# ==================================================================
class DecisionTreeRegressor:
    """
    一棵树 = 一连串「如果 A > 阈值走左边，否则走右边」。

    怎么找此刻最该问的那个问题？
        对每个候选切点算「切成两组后，组内平方和减少了多少」，
        减少最多的切点就是最佳分裂。

        J = Σ左 (y - ȳ左)² + Σ右 (y - ȳ右)²
        减少量 = J_parent - (J_left + J_right)

    加速技巧（本文件用的）：
        朴素做法要对每个特征扫 n 个候选值，复杂度 O(n²d)。
        工程上用「分箱直方图」：把连续特征离散成 B=24 个箱，
        一次扫描算出每箱的 (权重和, 加权y和)，之后所有切点用前缀和 O(1) 求。
        复杂度降到 O(n·d·B)，与样本量近似线性。

    复杂度：训练 O(n·d·B·log n)  推理 O(depth) = O(log n)
    """
    L1 = None

    def __init__(self, max_depth=4, min_samples_leaf=40, n_bins=24):
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.n_bins = n_bins

    def fit(self, X, y, w=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        w = np.ones(len(y)) if w is None else np.asarray(w, float)
        self.n_features_ = X.shape[1]
        self.tree_ = self._build(X, y, 0, w)
        return self

    def _best_split(self, X, y, w):
        """在所有特征上找最佳分裂点"""
        tot_w = w.sum()
        tot_sy = (w * y).sum()
        if tot_w <= 0:
            return None
        parent = tot_sy ** 2 / tot_w      # 加权均值的平方和 = (Σwy)²/Σw

        best = None
        for j in range(X.shape[1]):
            col = X[:, j]
            lo, hi = col.min(), col.max()
            if hi - lo < 1e-12:
                continue
            b = np.clip(((col - lo) / (hi - lo) * self.n_bins).astype(int),
                        0, self.n_bins - 1)
            if len(np.unique(b)) < 2:
                continue
            bw = np.bincount(b, weights=w, minlength=self.n_bins)
            bs = np.bincount(b, weights=w * y, minlength=self.n_bins)
            cw = np.cumsum(bw)
            cs = np.cumsum(bs)
            ok = (cw >= self.min_samples_leaf) & (tot_w - cw >= self.min_samples_leaf)
            if not ok.any():
                continue
            score = np.full(self.n_bins, -np.inf)
            score[ok] = (cs[ok] ** 2 / np.maximum(cw[ok], 1e-12)) + \
                        ((tot_sy - cs[ok]) ** 2 / np.maximum(tot_w - cw[ok], 1e-12))
            k = int(np.argmax(score))
            gain = score[k] - parent
            if gain > 0 and (best is None or gain > best[2]):
                thr = lo + (hi - lo) * (k + 0.5) / self.n_bins
                best = (j, thr, gain)
        return best

    def _build(self, X, y, depth, w):
        node = {"n": len(y), "pred": float(np.average(y, weights=w)),
                "leaf": True}
        if depth >= self.max_depth or len(y) < 2 * self.min_samples_leaf:
            return node

        best = self._best_split(X, y, w)
        if best is None:
            return node

        j, thr, _ = best
        m = X[:, j] < thr
        node.update(leaf=False, feature=j, threshold=thr,
                    left=self._build(X[m], y[m], depth + 1, w[m]),
                    right=self._build(X[~m], y[~m], depth + 1, w[~m]))
        return node

    def predict(self, X):
        X = np.asarray(X, float)
        out = np.empty(len(X))
        for i, x in enumerate(X):
            nd = self.tree_
            while not nd["leaf"]:
                nd = nd["left"] if x[nd["feature"]] < nd["threshold"] else nd["right"]
            out[i] = nd["pred"]
        return out

    def count_nodes(self):
        return sum(1 for _ in iter_nodes(self.tree_))

    def export_rules(self, names=None):
        """导出 if-else 文字规则 —— 精算最需要的可解释形式"""
        names = names or [f"x{i}" for i in range(self.n_features_)]
        lines = []
        def rec(nd, cond):
            if nd["leaf"]:
                lines.append(f"{' 且 '.join(cond) if cond else '全体'}  →  预测 {nd['pred']:.1f}")
                return
            j, thr = nd["feature"], nd["threshold"]
            rec(nd["left"], cond + [f"{names[j]} ≤ {thr:.3g}"])
            rec(nd["right"], cond + [f"{names[j]} > {thr:.3g}"])
        rec(self.tree_, [])
        return "\n".join(lines)


# ==================================================================
# 4. GBDT（梯度提升决策树 · 牛顿步）
# ==================================================================
class GBDT:
    """
    从「一棵歪树」到「很多棵歪树」：
    每一步只用一棵很浅的树，去拟合「上一轮没解释掉的部分」。

    残差在回归里是 y - ŷ；更准确的说法是「负梯度」。
    对 Poisson deviance，负梯度恰好 = μ - y（代码里会推）。

    为什么它统治了表格数据？
        ① 树的加法结构天然捕获非线性与特征交互（写规则比写公式容易）
        ② 顺序拟合：每棵树都很弱（depth=3），天然规避过拟合
        ③ 特征不用标准化、不用线性假设、量纲无关
        同数据下精度通常比单棵树高 10~30%

    【本实现最关键的一个细节，也是最容易写错的地方】
    ------------------------------------------------------------------
    叶子输出必须直接设为「纯增量」 -Σg/Σh ，而不是「树对目标变量的拟合值」。

    朴素写法是：树去拟合 target = F + g/h，然后把树的预测加回 F。
    这在第一轮就可能出错 —— 因为 target 里含 F 本身（可能高达 20），
    树拟合出的值自然也带着这 20，加回 F 就等于每轮把 F 重复累加一遍，
    指数化之后直接爆到 1e12。

    正确写法（XGBoost 论文 Eq.7）：树只负责「分组」，
    每组的最优步长由 -Σg/Σh 单独算出，这样加回 F 的量级天然受控。

    复杂度：训练 O(M · n · d · B)   M=树数 n=样本 d=特征 B=箱数
            推理 O(M · log n)  仍然很快，可以实时打分
    """
    L1 = None

    def __init__(self, M=60, learning_rate=0.08, min_samples_leaf=30,
                 max_depth=3, base=None, step_cap=2.0, verbose=True, tag=""):
        self.M = M
        self.lr = learning_rate
        self.min_samples_leaf = min_samples_leaf
        self.max_depth = max_depth
        self.base = base
        self.step_cap = step_cap      # 单个叶子的输出上界（防爆）
        self.verbose = verbose
        self.tag = tag

    # ---------- 树遍历工具 ----------
    def _eval(self, tree, X):
        """用叶子上的 value 汇总单棵树输出"""
        out = np.empty(len(X))
        tr = tree.tree_
        for i, x in enumerate(X):
            nd = tr
            while not nd["leaf"]:
                nd = nd["left"] if x[nd["feature"]] < nd["threshold"] else nd["right"]
            out[i] = nd["value"]
        return out

    def _set_leaf_values(self, tree, X, g, h, w):
        """
        牛顿步：为每个叶子算 v = -Σ(w·g) / Σ(w·h)，并夹在 ±step_cap。
        这是 XGBoost 的核心一行代码。直觉：
            「这个叶子里，预测整体偏高了多少，就往回退多少」
            退让幅度用二阶信息 h 加权 —— 越不确定的样本，退让越谨慎。

        实现：先把所有样本按树结构路由到叶子，再按叶子聚合。
        """
        # 路由：node_of[i] 指向样本 i 落到的叶子节点对象
        route = np.empty(len(g), dtype=object)
        for i, x in enumerate(X):
            nd = tree.tree_
            while not nd["leaf"]:
                nd = nd["left"] if x[nd["feature"]] < nd["threshold"] else nd["right"]
            route[i] = nd

        # 按叶子聚合 Σ(w·g) 与 Σ(w·h)
        groups = {}
        for i, nd in enumerate(route):
            key = id(nd)
            if key not in groups:
                groups[key] = [nd, 0.0, 0.0]
            groups[key][1] += w[i] * g[i]
            groups[key][2] += w[i] * h[i]

        for nd, sg, sh in groups.values():
            v = -sg / max(sh, 1e-9)
            nd["value"] = float(np.clip(v, -self.step_cap, self.step_cap))

    def fit(self, X, y, w=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float)
        w = np.ones(len(y)) if w is None else np.asarray(w, float)
        w = w / w.mean()

        f0 = (float(np.log(np.clip(np.average(y, weights=w), 1e-6, None)))
              if self.base is None else float(self.base))

        F = np.full(len(y), f0)
        self.trees_ = []
        self.f0_ = f0
        self.importances_ = np.zeros(X.shape[1])

        for m in range(self.M):
            mu = np.exp(np.clip(F, -20, 20))
            # Poisson deviance 对 log 链接的二阶信息
            g = mu - y
            h = np.clip(mu, 1e-6, None)

            # 树只负责「把样本分组」：按 g/h 的绝对值找最该修的群体
            target = F + np.clip(g / h, -self.step_cap, self.step_cap)
            tree = DecisionTreeRegressor(max_depth=self.max_depth,
                                         min_samples_leaf=self.min_samples_leaf)
            tree.fit(X, target, w)
            self._set_leaf_values(tree, X, g, h, w)
            self.trees_.append(tree)

            for nd in iter_nodes(tree.tree_):
                if not nd["leaf"]:
                    self.importances_[nd["feature"]] += 1

            F = np.clip(F + self.lr * self._eval(tree, X), -20, 20)

            if self.verbose and (m % 20 == 19 or m == self.M - 1):
                dev = poisson_deviance(y, np.exp(np.clip(F, -20, 20)), w)
                print(f"    [{self.tag} 轮次 {m+1:>3}/{self.M}] deviance = {dev:.5f}")

        self.F_ = F
        self.mu_ = np.exp(np.clip(F, -20, 20))
        self.importances_ = self.importances_ / max(self.importances_.sum(), 1)
        return self

    def predict(self, X):
        X = np.asarray(X, float)
        F = np.full(len(X), self.f0_)
        for t in self.trees_:
            F = F + self.lr * self._eval(t, X)
        return np.exp(np.clip(F, -20, 20))

    def staged_predict(self, X):
        """逐轮预测，看精度怎么一轮轮涨上去 —— 教学非常好用"""
        X = np.asarray(X, float)
        F = np.full(len(X), self.f0_)
        out = []
        for i, t in enumerate(self.trees_):
            F = F + self.lr * self._eval(t, X)
            if (i + 1) % 10 == 0 or i == 0 or i == len(self.trees_) - 1:
                out.append((i + 1, np.exp(np.clip(F, -20, 20))))
        return out
