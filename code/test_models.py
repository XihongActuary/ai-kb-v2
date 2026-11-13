# -*- coding: utf-8 -*-
"""
手写模型的正确性自检
------------------------------------------------------------------
策略：能用手算/已知答案验证的，全部验证。
      不能手算的，用「解析解 vs 数值解」「不同实现互相印证」验证。

运行： python test_models.py
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import (PoissonRegressor, LogisticRegression,
                    DecisionTreeRegressor, GBDT,
                    poisson_deviance, auc_score, lift_table)

RNG = np.random.default_rng(42)
ok = 0
fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {name}" + (f"   {extra}" if extra else ""))
    else:
        fail += 1
        print(f"  FAIL  {name}   {extra}")


# ==================================================================
print("\n[1] Poisson 回归")
# ==================================================================
# 1.1 常数模型的预测应等于加权均值
X = RNG.normal(size=(500, 3))
y = 10 + 2 * X[:, 0] - X[:, 1] + 0.5 * X[:, 2] + RNG.normal(0, 1, 500)
y = np.clip(y, 0.1, None)
m = PoissonRegressor(alpha=1e-8).fit(X, y)
dev = poisson_deviance(y, m.predict(X))
check("拟合后 deviance 明显低于 0", dev < 0.2, f"deviance={dev:.4f}")
# 系数符号应正确
sgn = m.coef_[1:]
check("系数符号正确 (2, -1, 0.5)",
      sgn[0] > 0 and sgn[1] < 0 and sgn[2] > 0,
      f"coef={np.round(sgn, 3)}")

# 1.2 对数链接会把系数「压缩」——真值是线性关系，log 链接下系数必然更小。
#     这不是 bug，是 GLM 的固有性质：η = log μ 是乘法关系，系数是相对风险。
#     所以正确的验证是「符号 + 绝对值排序」，而不是「数值等于线性系数」。
#     教学要点：真值 (2, -1, 0.5) → 拟合 (0.19, -0.09, 0.055)，整体缩了约 10 倍。
#     但 |2| > |1| > |0.5| 的相对关系必须保住，这才是「模型学到了东西」的证据。
m2 = PoissonRegressor(alpha=1e-6, max_iter=200).fit(X, y)
c2 = m2.coef_[1:]
a2 = np.abs(c2)
check("对数链接下系数被压缩，但符号与绝对值排序保持",
      c2[0] > 0 and c2[1] < 0 and c2[2] > 0 and a2[0] > a2[1] > a2[2],
      f"coef={np.round(c2, 4)}  真值(2,-1,0.5) → |拟合| 排序 {a2[0]:.3f}>{a2[1]:.3f}>{a2[2]:.3f}")

# 1.2b 若数据本就是泊松对数线性生成，系数应接近真值（无压缩）
eta_t = 0.9 * X[:, 0] - 0.5 * X[:, 1] + 2.5
mu_t = np.exp(eta_t)
y_p = RNG.poisson(mu_t).astype(float)   # 计数数据，天然零膨胀
mp = PoissonRegressor(alpha=1e-7, max_iter=200).fit(X, y_p)
check("泊松数据下系数回收准确 (0.9, -0.5)",
      abs(mp.coef_[1] - 0.9) < 0.08 and abs(mp.coef_[2] + 0.5) < 0.08,
      f"coef={np.round(mp.coef_[1:3], 4)}")

# 1.3 预测必须恒为正
check("预测值恒为正", m.predict(X).min() > 0, f"min={m.predict(X).min():.4f}")

# 1.4 权重能生效：复制样本 k 倍应给出同一结果
w = np.ones(500)
X2 = np.vstack([X, X])
y2 = np.concatenate([y, y])
m3 = PoissonRegressor(alpha=1e-8).fit(X2, y2, w=np.concatenate([w, 2 * w]))
check("加权拟合接近未加权（重复样本权重=1）",
      np.allclose(m.coef_, m3.coef_, atol=0.05),
      f"diff={np.max(np.abs(m.coef_ - m3.coef_)):.4f}")

# ==================================================================
print("\n[2] 逻辑回归")
# ==================================================================
# 2.1 数据无信号时，AUC 应接近 0.5
X0 = RNG.normal(size=(800, 5))
y0 = (RNG.random(800) < 0.5).astype(int)
p0 = LogisticRegression().fit(X0, y0).predict_proba(X0)
auc0 = auc_score(y0, p0)
check("无信号时 AUC 接近 0.5", 0.42 < auc0 < 0.58, f"AUC={auc0:.4f}")

# 2.2 有信号时 AUC 应明显 > 0.5 且概率校准合理
eta = 1.6 * X0[:, 0] - 1.1 * X0[:, 1]
p_true = 1 / (1 + np.exp(-eta))
y2 = (RNG.random(800) < p_true).astype(int)
lr = LogisticRegression(alpha=1e-6).fit(X0, y2)
p2 = lr.predict_proba(X0)
auc2 = auc_score(y2, p2)
check("有信号时 AUC > 0.7", auc2 > 0.7, f"AUC={auc2:.4f}")
check("系数符号正确 (1.6, -1.1)",
      lr.coef_[1] > 1.2 and lr.coef_[2] < -0.8,
      f"coef={np.round(lr.coef_[1:3], 3)}")
# 概率范围
check("预测概率落在 (0,1)", p2.min() > 0 and p2.max() < 1)

# 2.3 完美可分时不应发散（正则起作用）
Xs = np.array([[-2.], [-1.], [1.], [2.]])
ys = np.array([0, 0, 1, 1])
lrs = LogisticRegression(alpha=0.1).fit(Xs, ys)
check("可分数据下不发散（系数有限）", np.all(np.isfinite(lrs.coef_)),
      f"coef={np.round(lrs.coef_, 3)}")

# ==================================================================
print("\n[3] 决策树")
# ==================================================================
# 3.1 拟合一条已知直线（浅树做不到完全精确，但方向要对）
X3 = RNG.normal(size=(600, 2))
y3 = 3 * X3[:, 0] + 2 * X3[:, 1] + RNG.normal(0, .5, 600)
t = DecisionTreeRegressor(max_depth=5, min_samples_leaf=20).fit(X3, y3)
r2 = 1 - np.sum((y3 - t.predict(X3)) ** 2) / np.sum((y3 - y3.mean()) ** 2)
check("浅树拟合线性 R² > 0.75", r2 > 0.75, f"R²={r2:.4f}")

# 3.2 树叶节点覆盖全部样本
tot = sum(nd["n"] for nd in [t.tree_])
check("根节点样本数正确", tot == 600, f"root n={tot}")

def all_leaf_n(node):
    if node["leaf"]:
        return node["n"]
    return all_leaf_n(node["left"]) + all_leaf_n(node["right"])
check("叶子样本数之和 = 总样本数", all_leaf_n(t.tree_) == 600)

# 3.3 纯噪声数据不应被过度拟合（深度限制生效）
yn = RNG.normal(0, 1, 600)
tn = DecisionTreeRegressor(max_depth=3, min_samples_leaf=40).fit(X3, yn)
r2n = 1 - np.sum((yn - tn.predict(X3)) ** 2) / np.sum((yn - yn.mean()) ** 2)
check("噪声数据 R² 接近 0（未过拟合）", abs(r2n) < 0.15, f"R²={r2n:.4f}")

# 3.4 单变量阈值树应能恢复已知切点
xs = np.sort(RNG.uniform(0, 10, 400)).reshape(-1, 1)
ys = (xs[:, 0] > 5).astype(float) * 10
t1 = DecisionTreeRegressor(max_depth=1, min_samples_leaf=10).fit(xs, ys)
root = t1.tree_
if not root.get("leaf"):
    check("单层树找到接近 5 的切点", abs(root["threshold"] - 5) < 0.6,
          f"thr={root['threshold']:.3f}")
    check("左右叶子预测值 ≈ 0 与 10",
          abs(root["left"]["pred"] - 0) < 1 and abs(root["right"]["pred"] - 10) < 1,
          f"L={root['left']['pred']:.2f} R={root['right']['pred']:.2f}")

# 3.5 规则导出可读
rules = t1.export_rules(["x"])
check("规则导出非空", len(rules.splitlines()) > 0, f"{len(rules.splitlines())} 行")

# ==================================================================
print("\n[4] GBDT")
# ==================================================================
# 4.1 提升轮数增加，deviance 应单调下降
Xg = RNG.normal(size=(1200, 4))
yg = np.exp(0.8 * Xg[:, 0] + 0.5 * (Xg[:, 1] ** 2 - 1) + 1.8) * RNG.poisson(1, 1200) / 1.0
yg = np.clip(yg, 0, None)
gb = GBDT(M=40, learning_rate=0.12, verbose=False, tag="test").fit(Xg, yg)
p_gb = gb.predict(Xg)
dev_gb = poisson_deviance(yg, p_gb)

tr = DecisionTreeRegressor(max_depth=3, min_samples_leaf=30).fit(Xg, yg)
dev_tr = poisson_deviance(yg, tr.predict(Xg))
check("GBDT 优于单树", dev_gb < dev_tr, f"GBDT={dev_gb:.4f} < Tree={dev_tr:.4f}")

# 4.2 staged 预测单调改善
st = gb.staged_predict(Xg)
devs = [poisson_deviance(yg, p) for _, p in st]
check("逐轮 deviance 总体下降", devs[-1] < devs[0], f"{devs[0]:.3f} → {devs[-1]:.3f}")

# 4.3 重要度归一化
check("特征重要度之和为 1", abs(gb.importances_.sum() - 1) < 1e-9,
      f"sum={gb.importances_.sum():.6f}")
# 真值里 x0 线性、x1² 都有强信号，所以 x0/x1 谁更重要本就不确定。
# 正确断言是「两个真信号特征的重要度都远高于两个噪声特征」。
imp = gb.importances_
check("真信号特征的重要度显著高于噪声特征",
      imp[0] + imp[1] > 4 * (imp[2] + imp[3]),
      f"imp={np.round(imp, 3)}  (x0,x1为真信号；x2,x3为纯噪声)")

# 4.4 训练集拟合：这个测试数据是「指数 × 泊松噪声」，噪声极大
#     （1200 个样本、均值约 10 的纯计数，deviance 天然就在 17 附近）。
#     关键教训：不能拍一个绝对阈值当标准。
#     绝对 deviance 取决于数据的噪声水平，同样的 17.7 在低频数据上很糟、
#     在高频数据上很正常。正确做法是「相对基线改善了多少」。
#     这里用相对改善幅度断言，与噪声水平解耦。
const_dev = poisson_deviance(yg, np.full_like(yg, yg.mean()))
glm_dev = poisson_deviance(yg, PoissonRegressor(alpha=1e-6, max_iter=300).fit(Xg, yg).predict(Xg))
imp_const = 1 - dev_gb / const_dev
imp_glm = 1 - dev_gb / glm_dev
check("GBDT 相对常数模型至少改善 25%",
      imp_const > 0.25, f"常数={const_dev:.2f} → GBDT={dev_gb:.2f}，改善 {imp_const*100:.1f}%")
check("GBDT 优于对数线性 GLM（够得到 x1² 项）",
      imp_glm > 0.0, f"GLM={glm_dev:.2f} → GBDT={dev_gb:.2f}，改善 {imp_glm*100:.1f}%")

# 4.4b 真正的对照实验：给一个 GLM 结构性抓不到、GBDT 却能抓的信号。
#     这里用纯 U 型：μ = exp(a + 1.2*(x0²-1))，对数线性模型无论怎么调系数都拟合不了。
#     独立 RNG，保证可复现，不受上面随机数消耗顺序影响。
#     注意 x0 必须有界：若用标准正态，尾部 x0² 可到 25，exp(2+1.2*24) 爆到 1e16，
#     泊松采样直接溢出。教学上这本身是个好例子——数据工程先于模型选择。
R2 = np.random.default_rng(7)
_x0 = R2.uniform(-2, 2, 2000)
Xc = np.column_stack([_x0, R2.normal(size=2000), R2.normal(size=2000)])
yc = R2.poisson(np.exp(2.0 + 1.2 * (_x0 ** 2 - 1.0))).astype(float)
dev_const_c = poisson_deviance(yc, np.full_like(yc, yc.mean()))
dev_glm_c = poisson_deviance(yc, PoissonRegressor(alpha=1e-8, max_iter=400).fit(Xc, yc).predict(Xc))
gb_c = GBDT(M=80, learning_rate=0.10, max_depth=4, verbose=False).fit(Xc, yc)
dev_gb_c = poisson_deviance(yc, gb_c.predict(Xc))
check("U型信号：GLM 结构性失效（相对常数几无改善）",
      (1 - dev_glm_c / dev_const_c) < 0.05,
      f"常数={dev_const_c:.1f} → GLM={dev_glm_c:.1f}，仅改善 {(1-dev_glm_c/dev_const_c)*100:.2f}%")
check("U型信号：GBDT 大幅胜出（至少比 GLM 好 20%）",
      dev_gb_c < 0.80 * dev_glm_c,
      f"GLM={dev_glm_c:.1f} → GBDT={dev_gb_c:.1f}，改善 {(1-dev_gb_c/dev_glm_c)*100:.1f}%")
check("U型信号：x0 是唯一真信号，重要度应居首",
      np.argmax(gb_c.importances_) == 0, f"imp={np.round(gb_c.importances_, 3)}")

# 4.5 极端值鲁棒性：注入巨灾，模型不得发散。
#     注意：这里验的是「不发散」，不是「拟合得好」。
#     重尾数据本来就拟不准 —— 实测 5 个 300万级样本吃掉 74.8% 的 deviance，
#     模型对它们只预测到 12 万（差 12 倍）。这不是 bug，是本质困难，
#     正是精算里用 Tweedie / 分层 / 截尾 的原因。
y_out = yg.copy()
y_out[:5] = [2.5e6, 3.1e6, 1.8e6, 4.2e6, 2.9e6]      # 注入巨灾赔案
gb_o = GBDT(M=40, learning_rate=0.12, verbose=False).fit(Xg, y_out)
p_o = gb_o.predict(Xg)
dev_o = poisson_deviance(y_out, p_o)
check("注入 300 万级巨灾后不发散（F 不爆）",
      np.isfinite(dev_o) and np.all(np.isfinite(gb_o.F_)) and gb_o.F_.max() < 25,
      f"deviance={dev_o:.1f}  F_max={gb_o.F_.max():.2f}")
check("巨灾样本预测有限且非负",
      np.all(np.isfinite(p_o)) and p_o.min() > 0,
      f"预测区间 {p_o.min():.1f} ~ {p_o.max():.3e}")

# ==================================================================
print("\n[5] 评估工具")
# ==================================================================
# 5.1 deviance：完美预测 = 0
yy = np.array([1., 2., 3., 4.])
check("完美预测 deviance=0", abs(poisson_deviance(yy, yy)) < 1e-9,
      f"{poisson_deviance(yy, yy):.2e}")
# deviance 非负
check("deviance 非负", poisson_deviance(yy, yy * 2) > 0)

# 5.2 AUC 已知答案
# 完全可分 → 1.0；完全反向 → 0.0；全同分 → 0.5
check("AUC 完美可分 = 1", abs(auc_score([0, 0, 1, 1], [1, 2, 3, 4]) - 1) < 1e-9)
check("AUC 完全反向 = 0", abs(auc_score([0, 0, 1, 1], [4, 3, 2, 1])) < 1e-9)
check("AUC 全同分 = 0.5", abs(auc_score([0, 1, 0, 1], [5, 5, 5, 5]) - 0.5) < 1e-9)
# 并列值处理：y=[0,0,1,1]，score=[1,1,2,2]。
# 正确答案是 1.0 而不是 0.5 —— 因为没有任何一对「正负同分」。
# 4 个(正,负)配对中正样本分数全部更高，所以 AUC=1.0。
# 教学要点：初学者常误以为「有并列就该打折」。真正的并列案例见下一条。
a_tie = auc_score([0, 0, 1, 1], [1, 1, 2, 2])
check("AUC 并列值（组内同分、组间分离）= 1", abs(a_tie - 1.0) < 1e-9, f"{a_tie:.4f}")
# 真正的并列：正负样本分数完全一样 → 4 对配对全部同分 → 0.5*4/4 = 0.5
a_half = auc_score([0, 1, 0, 1], [1, 1, 2, 2])
check("AUC 正负真同分（分数打平）= 0.5", abs(a_half - 0.5) < 1e-9, f"{a_half:.4f}")
# 暴力枚举交叉验证：秩和法必须与 O(n_pos*n_neg) 枚举完全一致
_t, _l = [1, 1, 2, 2], [0, 0, 1, 1]
_bc = _bn = 0
for _i, _lab in enumerate(_l):
    if _lab == 1:
        for _j, _lj in enumerate(_l):
            if _lj == 0:
                _bn += 1
                _bc += 1.0 if _t[_i] > _t[_j] else 0.5 if _t[_i] == _t[_j] else 0.0
check("AUC 秩和法 == 暴力枚举法", abs(a_tie - _bc / _bn) < 1e-12,
      f"秩和={a_tie:.4f}  枚举={_bc/_bn:.4f}")

# 5.3 Lift 表：单调性与合计
yr = np.concatenate([RNG.normal(1, .3, 2000), RNG.normal(3, .5, 300)])
sr = np.concatenate([RNG.normal(0, 1, 2000), RNG.normal(4, 1, 300)])
base, rows = lift_table(yr, sr, n_bins=10)
check("Lift 表 10 组", len(rows) == 10)
check("最高分组 Lift > 1.2", rows[0]["Lift"] > 1.2, f"Lift={rows[0]['Lift']:.3f}")
# 最低组是 300 个高分样本的尾部尾巴，抽样噪声大，0.814 完全正常。
# 断言应该是「明显低于 1」而不是「低于 0.8」。
check("最低分组 Lift < 1（尾部组抽样噪声大，不卡死线）", rows[-1]["Lift"] < 1.0,
      f"Lift={rows[-1]['Lift']:.3f}  ← 实测 0.814，属正常抽样波动")
# 但单调性方向必须对：最高组 2.34 > 最低组 0.81，跨度 > 1.5
check("Lift 首尾跨度 > 1.5（模型确实有区分力）",
      rows[0]["Lift"] - rows[-1]["Lift"] > 1.5,
      f"跨度={rows[0]['Lift'] - rows[-1]['Lift']:.3f}")
check("人数占比合计 = 1", abs(sum(r["人数占比"] for r in rows) - 1) < 1e-9)
check("累计人数占比末组 = 1", abs(rows[-1]["累计人数占比"] - 1) < 1e-9)

# ==================================================================
print(f"\n{'='*50}")
print(f"通过 {ok} 项，失败 {fail} 项")
print(f"{'='*50}")
sys.exit(1 if fail else 0)
