# -*- coding: utf-8 -*-
"""AI 实践库 · 工具页 M01 / A01：常见模型速查 + 常见算法速查

和正文页的区别：正文是「带你走一遍」，工具页是「回头查一下」。
所以每张卡片固定六块，顺序永远一样，找东西不用重新适应：
    是什么 → 什么时候用 → 怎么用 → 数学表达 → 图像表达 → Python 代码

代码默认折叠（<details>），因为工具页第一任务是「扫一眼就找到」，
一上来铺 12 段代码会把人赶走；想抄的时候再点开。
"""

from pages_basics import INK, GREY, RED, JADE, AMBER, LINE, _cl
from pages_a import _toc

W, H = 300, 132          # 每张小图统一画布，视觉上才齐


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _mini(inner, cap):
    return (f'<div class="mini"><svg viewBox="0 0 {W} {H}" '
            f'xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:340px;'
            f'height:auto">{inner}</svg>'
            f'<div class="fig-cap">{cap}</div></div>')


def _fold(summary, code, note=""):
    return (f'<details class="fold"><summary>{summary}</summary>'
            f'<div class="fold-body">{note}'
            f'<pre><code>{_esc(code)}</code></pre></div></details>')


def _kv(k, v):
    return f'<div class="kv"><span class="k">{k}</span><span class="v">{v}</span></div>'


# ------------------------------------------------------------------ 本案例对照
# 每张卡片底部那条「本案例」横条：能链到真实代码的就链代码，
# 本案例确实没用到的，就写清为什么没用——比硬凑一个链接诚实。
_L = {
    "glm":    _cl("models", "class PoissonRegressor", label="models.py · PoissonRegressor"),
    "irls":   _cl("models", "def fit(self, X, y, w=None):", label="PoissonRegressor.fit", nth=0),
    "logi":   _cl("models", "class LogisticRegression", label="models.py · LogisticRegression"),
    "tree":   _cl("models", "class DecisionTreeRegressor", label="models.py · DecisionTreeRegressor"),
    "cart":   _cl("models", "def _best_split", label="DecisionTree._best_split"),
    "gbdt":   _cl("models", "class GBDT", label="models.py · GBDT"),
    "boost":  _cl("models", "def fit(self, X, y, w=None):", label="GBDT.fit", nth=3),
    "newton": _cl("models", "def _set_leaf_values", label="GBDT 的牛顿步长"),
    "tune":   _cl("_tune", "def main", label="_tune.py · 扫参数"),
    "step45": _cl("train_evaluate", "def step45_models", label="step45 四模型对垒"),
    "step3":  _cl("train_evaluate", "def step3_dataset", label="step3 切训练/测试"),
    "step6":  _cl("steps_678", "def step6_rejected", label="step6 给拒保人打分"),
    "stop":   _cl("models", "def fit(self, X, y, w=None):", label="IRLS 的收敛判据", nth=0),
    "logitest": _cl("test_models", label="test_models.py"),
}

CASE = {
    # ---------------- 模型
    "lin":  (False, "目标变量是<b>出险次数与金额</b>，不是正态分布的连续值，"
                    "所以本案例走的是它的推广——GLM：{glm}"),
    "logi": (False, "本库手写了它，但<b>只在正确性自检里跑</b>（解析解 vs 数值解互印），"
                    "主流水线没走这条路——因为「好司机」这条线最后是<b>排序＋圈选</b>，"
                    "概率只是副产品，不是决策依据。实现见 {logi}，自检见 {logitest}"),
    "glm":  (True,  "<b>本案例的主模型之一</b>。频率建模就是它，IRLS 手写实现：{glm}"),
    "twe":  (False, "<b>本库明确没实现</b>，在第 25 页写成了诚实声明："
                    "<a href=\"ch03.html#tweedie\">03 页 · Tweedie 留作练习</a>。"
                    "案例改用「频率 × 案均」两步拆解达到同一目的。"),
    "tree": (True,  "单树用来产出<b>能给核保看的规则</b>：{tree}"),
    "rf":   (False, "没用。案例要<b>能落成核保规则的单一路径</b>，几百棵树投票说不清；"
                    "精度上也被 GBDT 压过，见 <a href=\"ch06.html\">第 28 页</a>。"),
    "gbdt": (True,  "<b>本案例精度最高的模型</b>，且要跟 GLM 对垒看谁更能往外走：{gbdt} · {step45}"),
    "knn":  (False, "没用。KNN 给不出<b>系数或规则</b>，核保要能解释为什么拒；"
                    "而且十几个特征里有类别型，距离本身没意义。"),
    "svm":  (False, "没用。同样卡在<b>可解释性</b>上——强监管下「算不出来为什么」就等于不能用。"),
    "km":   (False, "没用。本案例<b>标签是算出来的</b>（真实纯保费是否低于 1,063 元），"
                    "不是要机器自己分组，见 <a href=\"ch02.html#label\">第 24 页 · 标签从哪来</a>。"),
    "pca":  (False, "没用。特征只有十几个，<b>每一个都要能在核保规则里点名</b>，"
                    "降维之后就说不清是谁在起作用了。"),
    "mlp":  (False, "没用。样本 1.1 万条、特征十几个，这个量级上树模型更稳；"
                    "且神经网络的可解释成本在保险核保里太高，见 <a href=\"ch06.html\">第 28 页</a>。"),
    # ---------------- 算法
    "ols":  (False, "用不上。<b>GLM 没有闭式解</b>，只能迭代——这正是它比线性回归难一点的原因：{irls}"),
    "gd":   (True,  "GBDT 的「梯度」提升，本质就是<b>在函数空间里做梯度下降</b>：{boost}"),
    "sgd":  (False, "没用。样本才 1.1 万，一次全装进内存；而且 IRLS / 牛顿步更稳、更少调参：{irls}"),
    "cd":   (False, "没用。GLM 的系数之间相关性强，坐标下降收敛慢，不如整体解一步。"),
    "newton": (True, "<b>IRLS 就是牛顿法</b>（泊松对数连接下两者等价）；GBDT 每棵树的叶子值也用了二阶信息：{newton}"),
    "irls": (True,  "<b>本案例训练 GLM 的那套迭代</b>，手写实现、带收敛判据：{irls}"),
    "cart": (True,  "单树挑切点用的就是它，带权重版本：{cart}"),
    "boost": (True, "<b>本案例精度最高的那套</b>，80 轮逐轮补差：{boost}"),
    "bag":  (False, "没用。没做随机森林——理由同随机森林那条：要单一可解释路径，不要投票。"),
    "lloyd": (False, "没用。本案例不做聚类（标签是算出来的，不是分组出来的）。"),
    "cv":   (False, "<b>刻意没用。</b>本案例真正的风险不是「随机折上的波动」，"
                    "而是<b>模型从「见过的人」走到「没见过的人」</b>——K 折会把这个坑盖住。"
                    "见 <a href=\"ch09.html#gap\">第 31 页 · 外推落差</a>，"
                    "切分见 {step3}。"),
    "tune": (True,  "<b>本案例真跑过</b>：扫参数反推一套「梯度成立」的核保规则系数：{tune}"),
    "stop": (True,  "IRLS 每轮比偏差，<code>delta &lt; tol</code> 就停——这就是提前停止：{stop}"),
}


def _casebox(anchor):
    """卡片底部那条「本案例」横条。用过的给代码链接，没用过的说清为什么。"""
    c = CASE.get(anchor)
    if not c:
        return ""
    used, tpl = c
    try:
        txt = tpl.format(**_L)
    except KeyError:
        txt = tpl
    cls = "cbox" if used else "cbox no"
    k = "本案例" if used else "本案例没用"
    return (f'<div class="{cls}"><span class="cb-k">{k}</span>'
            f'<span class="cb-v">{txt}</span></div>')



def card(anchor, name, en, what, when, how, math, fig, cap, code,
         codelabel="Python 代码（点击展开）", codenote=""):
    return f"""
<div class="mdl">
<h3 id="{anchor}">{name}<span class="en">{en}</span></h3>
{_kv('是什么', what)}
{_kv('何时用', when)}
{_kv('怎么用', how)}
{_kv('数学表达', f'<div class="fx">{math}</div>')}
{_mini(fig, cap)}
{_casebox(anchor)}
{_fold(codelabel, code, codenote)}
</div>"""


LIB = """
<div class="tbl-wrap"><table class="tbl">
<tr><th>库</th><th>装法</th><th>许可证</th><th>文档</th><th>本页用到</th></tr>
<tr><td>NumPy</td><td><code>pip install numpy</code></td><td>BSD-3-Clause</td>
<td>numpy.org</td><td>手写实现、造数据</td></tr>
<tr><td>scikit-learn</td><td><code>pip install scikit-learn</code></td><td>BSD-3-Clause</td>
<td>scikit-learn.org</td><td>回归/树/聚类/降维/交叉验证</td></tr>
<tr><td>statsmodels</td><td><code>pip install statsmodels</code></td><td>BSD-3-Clause</td>
<td>statsmodels.org</td><td>GLM（泊松、Tweedie）</td></tr>
<tr><td>XGBoost</td><td><code>pip install xgboost</code></td><td>Apache-2.0</td>
<td>xgboost.readthedocs.io</td><td>GBDT 的工业实现</td></tr>
</table></div>
<p class="tbl-cap">以上均为长期维护的主流库，API 稳定；版本号以各官方文档为准。
本库自己的模型是 <b>手写的</b>（见 <code>code/models.py</code>），
用这些库只是为了让示例能直接粘到你的环境里跑。</p>
"""


# ================================================================ M01
def p_m01(F):
    s = []
    s.append("""
<p class="lead">12 个常见模型，每个讲六件事：<b>是什么 · 什么时候用 · 怎么用 · 数学表达 · 图像 · 可折叠的 Python 代码</b>。
每张卡片下面都挂一条「本案例用没用过」——用过的是绿的，能点进真实源码；没用的是灰的，并说清为什么没用。</p>""")
    s.append(_toc([("use", "这一页怎么用"), ("pick", "三十秒选定模型"),
                   ("lin", "线性回归"), ("logi", "逻辑回归"),
                   ("glm", "GLM 与泊松回归"), ("twe", "Tweedie 回归"),
                   ("tree", "决策树"), ("rf", "随机森林"),
                   ("gbdt", "GBDT / XGBoost"),
                   ("knn", "KNN"), ("svm", "SVM"),
                   ("km", "K-Means"), ("pca", "PCA"),
                   ("mlp", "神经网络 MLP"), ("no", "什么时候别上大模型")]))

    s.append("""
<h2 id="use">这一页怎么用</h2>
<p>正文（B1–B14、第 01–13 章）是<b>顺着读的</b>；这一页是<b>回头查的</b>。
每张卡片顺序固定：是什么 → 什么时候用 → 怎么用 → 数学表达 → 图像表达 → Python 代码。
代码默认收起来，想抄的时候再点开，不挡视线。</p>""" + LIB)

    s.append("""
<h2 id="pick">三十秒选定模型</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>你的情况</th><th>先用这个</th><th>为什么</th></tr>
<tr><td>要预测一个数字，关系大致是直的</td><td>线性回归 / GLM</td>
    <td>系数能直接念给人听，出事好解释</td></tr>
<tr><td>要预测「会不会」（0/1）</td><td>逻辑回归</td>
    <td>输出就是概率，天然能排序、能设阈值</td></tr>
<tr><td>要预测次数、金额，且大部分是 0</td><td>泊松 / Tweedie</td>
    <td>专门为正数、零膨胀、长尾设计</td></tr>
<tr><td>表格数据，想要精度，也要看变量重要性</td><td>GBDT / XGBoost</td>
    <td>表格数据上的常胜将军</td></tr>
<tr><td>要写成「如果…就…」给人审核</td><td>决策树（浅一点）</td>
    <td>规则能原样导出成文字</td></tr>
<tr><td>没有标签，只想把人分堆</td><td>K-Means</td>
    <td>快、结果看得懂</td></tr>
<tr><td>特征太多、彼此相关</td><td>PCA</td>
    <td>压成几个互不相关的新变量</td></tr>
<tr><td>图像 / 文本 / 语音</td><td>神经网络</td>
    <td>这些任务上传统模型打不过它</td></tr>
</table></div>
<div class="note">表格数据（一行一个客户、几十个字段）上，
<b>GBDT 类通常打过深度学习</b>，而且训练快、好解释。
别因为「深度学习听起来更高级」就先上它。</div>""")

    # ---------------- 线性回归
    s.append(card(
        "lin", "线性回归", "Linear Regression",
        "找一条直线（或超平面），让所有点到它的竖直距离平方和最小。",
        "要预测的是<b>连续数字</b>，且相信各项影响可以相加：保费 = 基础 + 车龄×a + 驾龄×b …",
        "先看残差图有没有弯曲；有弯就加平方项或换模型。系数正负要和业务常识对得上。",
        "ŷ = β₀ + β₁x₁ + β₂x₂ + … + βₚxₚ &nbsp;&nbsp;·&nbsp;&nbsp; 目标：min Σ(yᵢ − ŷᵢ)²",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="112" x2="284" y2="112" stroke="{LINE}"/>'
        f'<line x1="26" y1="14" x2="26" y2="112" stroke="{LINE}"/>'
        + "".join(f'<circle cx="{46+i*22}" cy="{104-int((0.16*i+0.4)*72)}" r="3.4" fill="{JADE}" fill-opacity=".75"/>'
                  for i in range(11))
        + f'<line x1="30" y1="96" x2="280" y2="24" stroke="{RED}" stroke-width="2.4"/>'
        + "".join(f'<line x1="{46+i*22}" y1="{104-int((0.16*i+0.4)*72)}" x2="{46+i*22}" y2="{96-int(i*7.2*0.98)}" stroke="{GREY}" stroke-dasharray="3 3"/>'
                  for i in range(11))
        + f'<text x="150" y="128" font-size="11" fill="{GREY}" text-anchor="middle">虚线是残差，直线要让它们平方和最小</text>',
        "红线是拟合出来的直线，每个点到线的竖直虚线就是误差",
        """import numpy as np

# 造点数据：y = 3 + 2x + 噪声
rng = np.random.default_rng(0)
X = rng.uniform(0, 10, size=200)
y = 3 + 2 * X + rng.normal(0, 1.5, size=200)

# 加一列 1，用来吸收截距
A = np.column_stack([np.ones(len(X)), X])

# 闭式解（正规方程）：一步算出系数
beta = np.linalg.solve(A.T @ A, A.T @ y)
print("截距=%.2f  斜率=%.2f" % (beta[0], beta[1]))   # ≈ 3.0, 2.0

# 预测 + 评估
pred = A @ beta
print("RMSE = %.3f" % np.sqrt(np.mean((y - pred) ** 2)))""",
    ))

    # ---------------- 逻辑回归
    s.append(card(
        "logi", "逻辑回归", "Logistic Regression",
        "名字里有「回归」，干的是<b>分类</b>：先算线性得分，再用 S 形函数压成 0–1 之间的概率。",
        "要判断「属不属于某一类」，而且<b>想要概率而不只是结论</b>——比如要按概率排序再圈人。",
        "输出是概率，阈值你自己定；调阈值就是调「宁可错杀还是宁可放过」。别只看准确率。",
        "p = 1 / (1 + e^(−(β₀ + β₁x₁ + …))) &nbsp;&nbsp;·&nbsp;&nbsp; 训练：最大化对数似然 Σ[y·ln p + (1−y)·ln(1−p)]",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="112" x2="284" y2="112" stroke="{LINE}"/>'
        f'<line x1="150" y1="10" x2="150" y2="112" stroke="{LINE}" stroke-dasharray="4 3"/>'
        f'<path d="M28,104 C80,102 120,86 150,62 C180,38 220,22 280,18" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        + "".join(f'<circle cx="{34+i*13}" cy="{108-i*1.2}" r="3" fill="{JADE}"/>' for i in range(9))
        + "".join(f'<circle cx="{180+i*13}" cy="{24+i*1.0}" r="3" fill="{AMBER}"/>' for i in range(8))
        + f'<line x1="150" y1="14" x2="150" y2="112" stroke="{INK}" stroke-dasharray="4 3"/>'
        + f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">竖线以上是「判为 1」，以下是「判为 0」，阈值可左右挪</text>',
        "S 曲线把得分压成概率；中间那条竖线是判定阈值",
        """import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(0)
X = rng.normal(size=(600, 3))
y = (X @ np.array([1.2, -0.8, 0.5]) + rng.normal(0, .6, 600) > 0).astype(int)

m = LogisticRegression(penalty="l2", C=1.0, max_iter=1000)
m.fit(X, y)

p = m.predict_proba(X)[:, 1]          # 要概率，不要硬结论
print("AUC = %.3f" % roc_auc_score(y, p))

# 阈值不是非得 0.5：想少漏人就调低，想少误伤就调高
for t in (0.3, 0.5, 0.7):
    pred = (p >= t).astype(int)
    print("阈值 %.1f → 圈出 %d 人，命中 %d 人" % (t, pred.sum(), (pred & y).sum()))""",
    ))

    # ---------------- GLM / 泊松
    s.append(card(
        "glm", "GLM 与泊松回归", "Generalized Linear Model / Poisson",
        "线性回归的推广：允许结果不是正态分布。泊松回归专为<b>计数</b>（出险次数）设计，"
        "用对数连接把「线性得分」变成「正的期望值」。",
        "要预测<b>次数、件数、频率</b>这类非负整数；精算里的索赔频率建模就是它。",
        "看偏差（deviance）是否收敛；检查预测均值与实际的比值（校准比）。有过度离散要考虑负二项。",
        "ln μ = β₀ + β₁x₁ + … &nbsp;→&nbsp; μ = e^(β₀ + β₁x₁ + …) &nbsp;&nbsp;·&nbsp;&nbsp; y ~ Poisson(μ)，权重用暴露数",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="112" x2="284" y2="112" stroke="{LINE}"/>'
        f'<line x1="26" y1="14" x2="26" y2="112" stroke="{LINE}"/>'
        f'<path d="M30,106 C90,100 140,84 180,58 C215,36 250,24 282,20" fill="none" stroke="{RED}" stroke-width="2.6"/>'
        + "".join(f'<circle cx="{40+i*24}" cy="{104-int(3.2*(1.32**i))}" r="3.2" fill="{JADE}" fill-opacity=".8"/>' for i in range(9))
        + f'<text x="34" y="24" font-size="11" fill="{GREY}">μ（期望次数）</text>'
        f'<text x="150" y="128" font-size="11" fill="{GREY}" text-anchor="middle">曲线只会往上、不会到 0 以下，这正适合计数</text>',
        "指数曲线保证预测值永远是正数",
        """import numpy as np, statsmodels.api as sm

rng = np.random.default_rng(0)
n = 2000
x = rng.normal(size=n)
exposure = rng.uniform(0.4, 1.0, size=n)        # 暴露数：保了多久
mu = np.exp(0.3 + 0.6 * x) * exposure           # 真正的期望次数
y = rng.poisson(mu)

# 泊松 GLM：对数连接 + 暴露数作 offset
m = sm.GLM(y, sm.add_constant(x), family=sm.families.Poisson(),
           offset=np.log(exposure)).fit()
print(m.summary())
print("偏差 deviance = %.1f，自由度 df = %d" % (m.deviance, m.df_resid))
print("系数 =", np.round(m.params, 3))          # ≈ [0.3, 0.6]""",
        codenote="<p>本库的 <code>PoissonRegressor</code> 是手写的（IRLS 迭代），见 "
                 + _cl("models", "class PoissonRegressor", label="models.py") + "。</p>",
    ))

    # ---------------- Tweedie
    s.append(card(
        "twe", "Tweedie 回归", "Tweedie Regression",
        "专门对付「<b>一大堆 0 ＋ 少数巨额</b>」的金额：把「会不会出险」和「出险赔多少」"
        "揉进一个分布里一次建模。",
        "直接预测<b>纯保费（金额）</b>：大多数人一年赔 0 元，极少数赔到几十万。"
        "本案例最后就是这么干的。",
        "调 power 参数 p（1&lt;p&lt;2，1.5 常用）。别用 MSE 当主指标，零太多会把它压得没有意义。",
        "Var(μ) = φ·μ^p，p ∈ (1, 2) &nbsp;&nbsp;·&nbsp;&nbsp; 纯保费 = 频率 × 案均 = μ_freq × μ_sev",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="112" x2="284" y2="112" stroke="{LINE}"/>'
        + "".join(f'<rect x="{30+i*22}" y="{112-h}" width="15" height="{h}" fill="{JADE if i<7 else RED}" fill-opacity=".8"/>'
                  for i, h in enumerate([78, 20, 9, 5, 3, 2, 1, 1, 1, 0.8, 0.6]))
        + f'<text x="34" y="24" font-size="11" fill="{RED}">大量 0</text>'
        f'<text x="250" y="60" font-size="11" fill="{GREY}">长尾</text>'
        f'<text x="150" y="128" font-size="11" fill="{GREY}" text-anchor="middle">柱子越往右越少但越长——这就是重尾，普通回归会被它带偏</text>',
        "第一根柱子是「赔 0 元」的人，右边那几根是巨额赔案",
        """import numpy as np, statsmodels.api as sm

rng = np.random.default_rng(0)
n = 3000
x = rng.normal(size=n)
mu = np.exp(0.5 + 0.4 * x)

# Tweedie 造数（简化）：先抽次数，再抽伽马金额
cnt = rng.poisson(mu * 0.25)
sev = rng.gamma(shape=2.0, scale=3000, size=n)
y = cnt * sev                                   # 大多数是 0

# power=1.5 是纯保费建模的常用档位
m = sm.GLM(y, sm.add_constant(x),
           family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log())
           ).fit()
print("power=1.5 时的系数 =", np.round(m.params, 3))

# 别忘了：零占比高时，先看「预测均值 / 实际均值」
print("校准比 = %.3f" % (m.fittedvalues.mean() / y.mean()))""",
    ))

    # ---------------- 决策树
    s.append(card(
        "tree", "决策树", "Decision Tree (CART)",
        "一串「是非题」：先问最能分清好坏的那个问题，把人劈成两半，两半里再各自问。",
        "要的是<b>能念给人听的规则</b>；或者数据里有明显的分段（比如 25 岁以下一个价、以上另一个价）。",
        "限深度（3–6 层）和叶子里最少样本数，否则一个叶子一个人，等于背答案。",
        "回归树：叶子里取均值 &nbsp;·&nbsp; 分裂准则：min [ n_L·Var_L + n_R·Var_R ]；分类树改用基尼或熵",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="150" y1="26" x2="80" y2="60" stroke="{LINE}"/>'
        f'<line x1="150" y1="26" x2="220" y2="60" stroke="{LINE}"/>'
        f'<line x1="80" y1="76" x2="50" y2="104" stroke="{LINE}"/>'
        f'<line x1="80" y1="76" x2="112" y2="104" stroke="{LINE}"/>'
        f'<line x1="220" y1="76" x2="192" y2="104" stroke="{LINE}"/>'
        f'<line x1="220" y1="76" x2="252" y2="104" stroke="{LINE}"/>'
        + f'<rect x="118" y="10" width="64" height="20" rx="5" fill="{INK}"/>'
        f'<text x="150" y="24" font-size="10.5" fill="#f5f1e6" text-anchor="middle">车龄&gt;8?</text>'
        + f'<rect x="52" y="60" width="56" height="20" rx="5" fill="#fff" stroke="{LINE}"/>'
        f'<text x="80" y="74" font-size="10.5" fill="{INK}" text-anchor="middle">里程&gt;2万?</text>'
        + f'<rect x="192" y="60" width="56" height="20" rx="5" fill="#fff" stroke="{LINE}"/>'
        f'<text x="220" y="74" font-size="10.5" fill="{INK}" text-anchor="middle">营运车?</text>'
        + "".join(f'<rect x="{x}" y="104" width="36" height="18" rx="5" fill="{c}" fill-opacity="{o}"/>'
                  f'<text x="{x+18}" y="117" font-size="10" fill="#f5f1e6" text-anchor="middle">{t}</text>'
                  for x, c, o, t in [(32, JADE, ".85", "低"),
                                     (94, RED, ".85", "高"),
                                     (174, JADE, ".85", "低"),
                                     (234, RED, ".85", "高")])
        + f'<text x="150" y="129" font-size="11" fill="{GREY}" text-anchor="middle">叶子就是最终结论：落到哪片叶子，就是哪类人</text>',
        "一层一层问下去，叶子是结论",
        """from sklearn.tree import DecisionTreeRegressor, export_text

# 关键旋钮就是这两个：别让它长得太深、叶子别太小
m = DecisionTreeRegressor(max_depth=4, min_samples_leaf=40, random_state=0)
m.fit(X, y)

print("叶子数 =", m.get_n_leaves(), " 深度 =", m.get_depth())
# 规则可以直接念给业务听
print(export_text(m, feature_names=["车龄", "车值", "里程"], max_depth=3))

# 用它预测
print(m.predict(X[:5]))""",
        codenote="<p>手写版（含「怎么挑最佳切点」）见 "
                 + _cl("models", "class DecisionTreeRegressor",
                       label="models.py · DecisionTreeRegressor") + "。</p>",
    ))

    # ---------------- 随机森林
    s.append(card(
        "rf", "随机森林", "Random Forest",
        "一堆树各看一部分数据、各看一部分特征，最后<b>投票/取平均</b>。单棵树容易走偏，一群树的平均就稳了。",
        "要<b>稳</b>、不想调参、又想要非线性。是「先跑一个不丢人」的基线模型。",
        "树数 300–500 够了，再加收益很小。想提速可以砍 max_depth。它给不了「公式」，但能给特征重要性。",
        "ŷ = (1/B) Σ f_b(x) &nbsp;&nbsp;·&nbsp;&nbsp; 每棵树：样本自助抽样 + 每次分裂只看随机 m 个特征",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<g transform="translate({26+i*88},14)">'
                  f'<rect x="18" y="0" width="34" height="18" rx="4" fill="#fff" stroke="{LINE}"/>'
                  f'<text x="35" y="13" font-size="10" fill="{INK}" text-anchor="middle">树{i+1}</text>'
                  f'<line x1="35" y1="18" x2="18" y2="42" stroke="{LINE}"/>'
                  f'<line x1="35" y1="18" x2="52" y2="42" stroke="{LINE}"/>'
                  f'<rect x="2" y="42" width="32" height="17" rx="4" fill="{JADE}" fill-opacity=".3"/>'
                  f'<rect x="36" y="42" width="32" height="17" rx="4" fill="{JADE}" fill-opacity=".3"/>'
                  + f'<text x="18" y="55" font-size="9.5" fill="{INK}" text-anchor="middle">{"12" if i%2 else "9"}</text>'
                  + f'<text x="52" y="55" font-size="9.5" fill="{INK}" text-anchor="middle">{"15" if i%2 else "11"}</text>'
                  + f'<line x1="18" y1="59" x2="35" y2="80" stroke="{GREY}"/>'
                  + f'<line x1="52" y1="59" x2="35" y2="80" stroke="{GREY}"/>'
                  + "</g>" for i in range(3))
        + f'<rect x="112" y="98" width="76" height="22" rx="6" fill="{AMBER}" fill-opacity=".18" stroke="{AMBER}"/>'
        f'<text x="150" y="113" font-size="11" fill="{INK}" text-anchor="middle">取平均 → 11.7</text>'
        f'<text x="150" y="129" font-size="11" fill="{GREY}" text-anchor="middle">每棵树看得不一样，误差互相抵消</text>',
        "三棵树各自给个数，平均一下就是最终答案",
        """from sklearn.ensemble import RandomForestRegressor

m = RandomForestRegressor(n_estimators=400,      # 树数：300~500 够用
                          max_depth=6,           # 不限深会又慢又容易过拟合
                          min_samples_leaf=30,
                          n_jobs=-1, random_state=0)
m.fit(X, y)

# 谁最重要？做特征筛选、跟业务解释都靠它
imp = sorted(zip(m.feature_importances_, names), reverse=True)
for v, n_ in imp[:5]:
    print("%-10s %.3f" % (n_, v))""",
    ))

    # ---------------- GBDT
    s.append(card(
        "gbdt", "GBDT / XGBoost", "Gradient Boosting Decision Trees",
        "<b>一棵接一棵地补</b>：第一棵树粗粗预测，第二棵专补第一棵的残差，第三棵再补剩下的……最后加起来。",
        "表格数据要精度时的第一选择。kaggle 和精算实务里最常见的赢家。",
        "三个旋钮：树数（配 early_stopping）、学习率（0.05–0.1）、树深（3–6）。"
        "学习率调小就要多加树。别忘留验证集做提前停止。",
        "F_m(x) = F_{m−1}(x) + η·h_m(x)，其中 h_m 去拟合残差 −∂L/∂F",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="112" x2="284" y2="112" stroke="{LINE}"/>'
        f'<line x1="26" y1="106" x2="284" y2="106" stroke="{LINE}" stroke-dasharray="3 3"/>'
        + "".join(f'<rect x="{30+i*40}" y="{106-h}" width="30" height="{h}" fill="{JADE}" fill-opacity="{.28+.14*i:.2f}"/>'
                  for i, h in enumerate([52, 26, 13, 7, 4, 2]))
        + f'<text x="45" y="98" font-size="10" fill="{INK}" text-anchor="middle">第1棵</text>'
        f'<text x="205" y="98" font-size="10" fill="{INK}" text-anchor="middle">…</text>'
        f'<path d="M30,54 C80,46 150,32 280,26" fill="none" stroke="{RED}" stroke-width="2"/>'
        f'<text x="150" y="129" font-size="11" fill="{GREY}" text-anchor="middle">每棵树只补「还差的那一点」，越往后补得越少</text>',
        "柱子一根比一根矮：后面的树只补剩下的残差",
        """from sklearn.ensemble import HistGradientBoostingRegressor
# 或：import xgboost as xgb

m = HistGradientBoostingRegressor(
    max_iter=500, learning_rate=0.06, max_depth=5,
    min_samples_leaf=30,
    early_stopping=True, validation_fraction=0.15,   # 到点就停，别死跑
    random_state=0)
m.fit(X, y)
print("实际用了", m.n_iter_, "棵树")

# XGBoost 写法几乎一样
# m = xgb.XGBRegressor(n_estimators=500, learning_rate=0.06,
#                      max_depth=5, subsample=0.8, colsample_bytree=0.8,
#                      early_stopping_rounds=40, eval_set=[(Xv, yv)])""",
        codenote="<p>手写版（含「叶子值怎么算、残差怎么补」）见 "
                 + _cl("models", "class GBDT", label="models.py · GBDT") + "。</p>",
    ))

    # ---------------- KNN
    s.append(card(
        "knn", "KNN", "K-Nearest Neighbors",
        "不训练，只记住所有人；来一个新人，就找跟他最像的 K 个邻居，看邻居们怎么样。",
        "样本不大、特征不多、想做个<b>直观的对照基线</b>。也常用于填补缺失值。",
        "<b>必须标准化</b>，否则量纲大的特征会一个人说了算。K 太小会抖，太大会抹平边界。样本一大就慢。",
        "ŷ(x) = (1/K) Σ_{i ∈ N_K(x)} y_i &nbsp;&nbsp;·&nbsp;&nbsp; 距离常用欧氏：d = √Σ(x_i − x_j)²",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<circle cx="150" cy="66" r="46" fill="none" stroke="{AMBER}" stroke-dasharray="4 3"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{c}"/>'
                  for cx, cy, c in [(120, 50, JADE), (168, 46, JADE), (176, 86, JADE),
                                    (132, 92, RED), (196, 62, RED), (86, 78, RED),
                                    (214, 96, RED), (74, 40, RED)])
        + f'<rect x="144" y="60" width="12" height="12" fill="{INK}"/>'
        f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">圈内 4 个邻居：3 绿 1 红 → 判为绿</text>',
        "虚线圈住最近的 K 个邻居，少数服从多数",
        """from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# KNN 对量纲极度敏感：标准化必须做，且要放进 pipeline 防泄漏
m = make_pipeline(StandardScaler(),
                  KNeighborsRegressor(n_neighbors=15, weights="distance"))
m.fit(X, y)

print("预测 =", m.predict(X[:3]))
# weights="distance"：越近的邻居说话越算数""",
    ))

    # ---------------- SVM
    s.append(card(
        "svm", "SVM", "Support Vector Machine",
        "不光找一条分界线，还要找一条<b>离两边都最远</b>的分界线。只有边界上那几个点（支持向量）说了算。",
        "样本不算大、特征维度高、边界清晰；文本分类的经典选择。",
        "先标准化。核函数选 rbf 时，C 和 gamma 要调。样本上万就慢了，而且<b>不直接给概率</b>。",
        "min ‖w‖²/2 + C·Σξ_i，约束 y_i(wᵀx_i + b) ≥ 1 − ξ_i &nbsp;&nbsp;·&nbsp;&nbsp; 核技巧：k(x, x′) = exp(−γ‖x−x′‖²)",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<path d="M40,100 L260,32" fill="none" stroke="{RED}" stroke-width="2.4"/>'
        f'<path d="M34,116 L254,48" fill="none" stroke="{GREY}" stroke-dasharray="4 3"/>'
        f'<path d="M46,84 L266,16" fill="none" stroke="{GREY}" stroke-dasharray="4 3"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{c}"/>'
                  for cx, cy, c in [(60, 100, JADE), (92, 88, JADE), (120, 76, JADE),
                                    (150, 66, JADE), (92, 108, JADE),
                                    (180, 52, AMBER), (208, 40, AMBER), (238, 28, AMBER),
                                    (210, 60, AMBER), (250, 44, AMBER)])
        + f'<circle cx="108" cy="82" r="6.5" fill="none" stroke="{INK}" stroke-width="1.4"/>'
        f'<circle cx="188" cy="48" r="6.5" fill="none" stroke="{INK}" stroke-width="1.4"/>'
        f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">中间实线是分界，两侧虚线是间隔；圈住的是支持向量</text>',
        "SVM 要的是「最宽的马路」，不是随便一条线",
        """from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

clf = make_pipeline(StandardScaler(),
                    SVC(kernel="rbf", C=1.0, gamma="scale",
                        probability=True))      # 想要概率得显式打开，代价是更慢
clf.fit(X, y)

print("支持向量个数 =", len(clf[-1].support_))
print("概率 =", clf.predict_proba(X[:3])[:, 1].round(3))""",
    ))

    # ---------------- K-Means
    s.append(card(
        "km", "K-Means", "K-Means Clustering",
        "<b>没有答案</b>也要分组：先随便定 K 个中心，把每个人派给最近的中心，再把中心挪到队员的均值处，反复到不动。",
        "想把客户分成几类却说不清标准；或者做探索，看看数据里是不是天然有几堆。",
        "先标准化。K 要自己定（常用肘部法或多试几个看业务能不能解释）。多跑几个随机起点取最优。",
        "目标：min Σ_{k} Σ_{x ∈ C_k} ‖x − μ_k‖² &nbsp;&nbsp;·&nbsp;&nbsp; μ_k = C_k 里所有点的均值",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="{JADE}" fill-opacity=".8"/>'
                  for cx, cy in [(56, 44), (70, 62), (48, 74), (84, 50), (66, 90), (96, 68)])
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="{AMBER}" fill-opacity=".85"/>'
                  for cx, cy in [(206, 44), (222, 62), (196, 76), (232, 54), (214, 90), (244, 74)])
        + f'<rect x="62" y="58" width="12" height="12" fill="{JADE}" stroke="#fff"/>'
        f'<rect x="216" y="62" width="12" height="12" fill="{AMBER}" stroke="#fff"/>'
        f'<line x1="34" y1="30" x2="110" y2="98" stroke="{LINE}" stroke-dasharray="3 3"/>'
        f'<line x1="184" y1="30" x2="262" y2="98" stroke="{LINE}" stroke-dasharray="3 3"/>'
        f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">方块是簇中心，虚线是大致边界</text>',
        "两堆点各自围绕自己的中心",
        """from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

Xs = StandardScaler().fit_transform(X)      # 聚类前必须标准化

# 肘部法：换个 K 看「簇内紧密程度」下降的拐点
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
    print("K=%d   inertia=%.1f" % (k, km.inertia_))

km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Xs)
print("每个人被分到：", km.labels_[:20])
print("簇中心（标准化尺度）=", km.cluster_centers_.round(2))""",
    ))

    # ---------------- PCA
    s.append(card(
        "pca", "PCA", "Principal Component Analysis",
        "特征太多又互相相关时，把它们<b>重新组合</b>成少数几个互不相关的新变量，尽量不丢信息。",
        "几十上百个特征、彼此高度相关；或者想画散点图但数据是高维的。",
        "先标准化。看「累计解释方差」选保留几个（常取 80–95%）。注意：<b>主成分不好解释</b>，要解释就用原变量。",
        "找 w 使 Var(Xw) 最大，且 ‖w‖ = 1 &nbsp;&nbsp;·&nbsp;&nbsp; 即 XᵀX 的特征向量；解释比例 = λ_i / Σλ",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{GREY}" fill-opacity=".55"/>'
                  for cx, cy in [(60, 90), (76, 78), (92, 84), (108, 68), (124, 74),
                                 (140, 58), (156, 64), (172, 48), (188, 54), (204, 40),
                                 (220, 46), (236, 32), (86, 66), (116, 56), (146, 46),
                                 (176, 34), (206, 26)])
        + f'<line x1="40" y1="112" x2="250" y2="22" stroke="{RED}" stroke-width="2.4"/>'
        f'<line x1="150" y1="66" x2="186" y2="88" stroke="{JADE}" stroke-width="1.8" stroke-dasharray="4 3"/>'
        f'<text x="196" y="94" font-size="10" fill="{JADE}">第二主成分</text>'
        f'<text x="248" y="20" font-size="10" fill="{RED}" text-anchor="end">第一主成分</text>'
        f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">红线方向上的点最分散 —— 那就是「信息最多」的方向</text>',
        "点云最伸展的方向就是第一主成分",
        """from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

Xs = StandardScaler().fit_transform(X)

p = PCA(n_components=0.9)        # 直接说「保留 90% 的信息」，它会自己算要几个
Z = p.fit_transform(Xs)
print("从 %d 个特征压到 %d 个主成分" % (X.shape[1], Z.shape[1]))
print("各主成分解释比例 =", p.explained_variance_ratio_.round(3))

# 看每个主成分主要由哪些原变量构成（用来给主成分起名字）
print(pd.DataFrame(p.components_, columns=names).round(2))""",
    ))

    # ---------------- MLP
    s.append(card(
        "mlp", "神经网络 MLP", "Multi-Layer Perceptron",
        "一堆「加权求和 → 非线性扭转」的小单元层层堆叠，靠反向传播一层层把误差传回去改权重。",
        "图像、语音、文本这类<b>结构复杂</b>的数据；或者特征之间关系高度非线性且样本量极大。",
        "先标准化。层数别一上来就堆很深，先试一层 64/128 个单元。要 reproducibility 就固定随机种子。",
        "h = σ(W₁x + b₁) → ŷ = W₂h + b₂ &nbsp;&nbsp;·&nbsp;&nbsp; 反向传播：∂L/∂W = ∂L/∂ŷ · ∂ŷ/∂W（链式法则）",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<circle cx="52" cy="{28+i*34}" r="7" fill="{JADE}" fill-opacity=".8"/>' for i in range(3))
        + "".join(f'<circle cx="150" cy="{18+i*26}" r="7" fill="{AMBER}" fill-opacity=".85"/>' for i in range(5))
        + f'<circle cx="248" cy="66" r="8" fill="{RED}" fill-opacity=".85"/>'
        + "".join(f'<line x1="52" y1="{28+i*34}" x2="150" y2="{18+j*26}" stroke="{LINE}"/>'
                  for i in range(3) for j in range(5))
        + "".join(f'<line x1="150" y1="{18+j*26}" x2="248" y2="66" stroke="{LINE}"/>' for j in range(5))
        + f'<text x="52" y="14" font-size="10" fill="{GREY}" text-anchor="middle">输入</text>'
        f'<text x="150" y="10" font-size="10" fill="{GREY}" text-anchor="middle">隐藏层</text>'
        f'<text x="248" y="14" font-size="10" fill="{GREY}" text-anchor="middle">输出</text>'
        f'<text x="150" y="126" font-size="11" fill="{GREY}" text-anchor="middle">每个连接都有一个权重，训练就是不停改这些权重</text>',
        "三层全连接：线越密，参数越多，也越容易背答案",
        """from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# 先小后大：一层 64 往往就够了，堆深了只会在表格数据上过拟合
m = make_pipeline(StandardScaler(),
                  MLPRegressor(hidden_layer_sizes=(64,), activation="relu",
                               alpha=1e-3,          # L2，防止背答案
                               max_iter=800, early_stopping=True,
                               random_state=0))
m.fit(X, y)
print("迭代次数 =", m[-1].n_iter_, " 最终损失 =", round(m[-1].loss_, 4))

# PyTorch 的最小写法（隐藏层 + ReLU + MSE）
# net = torch.nn.Sequential(torch.nn.Linear(p, 64), torch.nn.ReLU(),
#                           torch.nn.Linear(64, 1))
# opt = torch.optim.Adam(net.parameters(), lr=1e-3)
# for _ in range(200):
#     loss = torch.nn.functional.mse_loss(net(Xt), yt)
#     opt.zero_grad(); loss.backward(); opt.step()""",
    ))

    s.append("""
<h2 id="no">什么时候别上大模型</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>诱惑</th><th>现实</th><th>该做的</th></tr>
<tr><td>「上深度学习才够先进」</td>
    <td>表格数据上 GBDT 通常更好、更快、更好解释</td>
    <td>先用 GBDT 做基线，赢不了再换</td></tr>
<tr><td>「树越多越好」</td>
    <td>过了一定的量，误差不再降，只是变慢、变难解释</td>
    <td>配 early_stopping，看验证曲线拐点</td></tr>
<tr><td>「特征全丢进去让它自己学」</td>
    <td>垃圾特征进来，模型只会学到噪声，还会泄漏</td>
    <td>先做业务筛选，再看重要性回删</td></tr>
<tr><td>「换个模型就能救回数据问题」</td>
    <td>数据本身歪了，什么模型都救不回来</td>
    <td>先回到第②步查数据，再看模型</td></tr>
</table></div>
<div class="quote q-talk"><span class="q-tag">说 人 话</span>
<p>选模型不是追新，是<b>够用 + 能解释 + 能落地</b>。
在保险公司，一个能被核保人听懂、被合规通过的模型，
比一个 AUC 高 0.01 但没人敢用的模型值钱得多。</p></div>""")

    return "\n".join(s)


# ================================================================ A01
def p_a01(F):
    s = []
    s.append("""
<p class="lead">13 个常见算法，每个讲六件事：<b>它在解决什么问题 · 什么时候用 · 怎么用 · 数学表达 · 图像 · 可折叠的 Python 代码</b>。
算法是把模型「算出来」的那套工艺，不是模型本身——同一个模型可以换不同算法来算。</p>""")
    s.append(_toc([("use", "这一页怎么用"), ("vs", "算法和模型不是一回事"),
                   ("ols", "闭式解：正规方程"), ("gd", "梯度下降"),
                   ("sgd", "随机 / 小批量梯度下降"), ("cd", "坐标下降"),
                   ("newton", "牛顿法"), ("irls", "IRLS"),
                   ("cart", "CART 分裂：基尼与熵"), ("boost", "Boosting 前向分步"),
                   ("bag", "Bagging 与自助抽样"), ("lloyd", "Lloyd 迭代"),
                   ("cv", "K 折交叉验证"), ("tune", "调参：网格与贝叶斯"),
                   ("stop", "提前停止")]))

    s.append("""
<h2 id="use">这一页怎么用</h2>
<p>上一页（M01）讲的是<b>模型</b>——最后拿到手的那个成品，比如「一棵树」「一条直线」。
这一页讲的是<b>算法</b>——把成品做出来的工艺，比如「怎么挪到最低点」「怎么挑这一刀」。</p>
<div class="quote q-talk"><span class="q-tag">说 人 话</span>
<p><b>模型是菜，算法是菜谱。</b>同一道菜（线性回归）可以用大火快炒（闭式解，一步算完），
也可以用小火慢炖（梯度下降，一点一点挪）。菜一样，做法不一样，适用场合也不一样。</p></div>""")

    s.append("""
<h2 id="vs">算法和模型不是一回事</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>模型（成品）</th><th>常用算法（做法）</th><th>为什么这么配</th></tr>
<tr><td>线性回归 / 逻辑回归</td><td>闭式解、梯度下降、牛顿法、IRLS</td>
    <td>式子光滑，可以一步算完，也能一步步挪</td></tr>
<tr><td>带 L1 的回归（Lasso）</td><td>坐标下降</td>
    <td>L1 有尖角不好求导，一个一个变量轮着来反而简单</td></tr>
<tr><td>决策树</td><td>CART 贪心搜索（基尼 / 熵）</td>
    <td>切点组合太多，只能一步步贪心</td></tr>
<tr><td>GBDT</td><td>前向分步 + 梯度提升</td>
    <td>每轮只补残差，串行推进</td></tr>
<tr><td>随机森林</td><td>Bagging + 自助抽样</td>
    <td>并行造多样性，最后投票</td></tr>
<tr><td>K-Means</td><td>Lloyd 迭代</td>
    <td>派点 → 挪中心，两步交替必然收敛</td></tr>
</table></div>""")

    # ---- 闭式解
    s.append(card(
        "ols", "闭式解：正规方程", "Normal Equation / OLS",
        "把「误差平方和最小」这个条件写成方程，<b>一步解出</b>系数，不用迭代。",
        "样本几万以内、特征几十个的线性回归。精算里的 GLM 单机建模基本都够用。",
        "注意 XᵀX 可能不可逆（特征完全共线），加一点岭回归（ridge）就稳了。样本上百万就别用了，矩阵太大。",
        "β̂ = (XᵀX)⁻¹ Xᵀ y &nbsp;&nbsp;·&nbsp;&nbsp; 复杂度 O(np² + p³)，p 是特征数",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<rect x="24" y="42" width="60" height="48" rx="6" fill="#fff" stroke="{LINE}"/>'
        f'<text x="54" y="70" font-size="13" fill="{INK}" text-anchor="middle">X, y</text>'
        f'<line x1="88" y1="66" x2="128" y2="66" stroke="{RED}" stroke-width="2"/>'
        f'<text x="108" y="56" font-size="10" fill="{RED}" text-anchor="middle">一步</text>'
        f'<rect x="132" y="42" width="72" height="48" rx="6" fill="{JADE}" fill-opacity=".16" stroke="{JADE}"/>'
        f'<text x="168" y="62" font-size="11.5" fill="{INK}" text-anchor="middle">(XᵀX)⁻¹Xᵀy</text>'
        f'<text x="168" y="80" font-size="10.5" fill="{GREY}" text-anchor="middle">直接算出 β</text>'
        f'<line x1="208" y1="66" x2="244" y2="66" stroke="{RED}" stroke-width="2"/>'
        f'<rect x="248" y="42" width="42" height="48" rx="6" fill="#fff" stroke="{LINE}"/>'
        f'<text x="269" y="70" font-size="13" fill="{INK}" text-anchor="middle">β</text>'
        f'<text x="150" y="118" font-size="11" fill="{GREY}" text-anchor="middle">没有迭代、没有学习率、没有收敛判据——算完就完事</text>',
        "一次矩阵运算直接出结果",
        """import numpy as np

def ols(X, y, ridge=1e-8):
    \"\"\"闭式解。ridge 是给对角线加的一点点，防止 XᵀX 不可逆。\"\"\"
    A = np.column_stack([np.ones(len(X)), X])
    return np.linalg.solve(A.T @ A + ridge * np.eye(A.shape[1]), A.T @ y)

beta = ols(X, y)
print("系数 =", np.round(beta, 3))""",
    ))

    # ---- 梯度下降
    s.append(card(
        "gd", "梯度下降", "Gradient Descent",
        "站在山坡上，看脚下哪边最陡就往哪边迈一小步，反复走到走不动为止。",
        "样本/特征太多、闭式解算不动时；也是所有神经网络的训练方式。",
        "学习率是最关键的旋钮：太大来回震荡甚至发散，太小慢得没边。先画损失曲线看它是不是平滑下降。",
        "θ ← θ − η·∇θ L(θ) &nbsp;&nbsp;·&nbsp;&nbsp; 每轮复杂度 O(np)，η 是学习率",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<path d="M24,20 C80,110 220,110 276,20" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
        f'<text x="150" y="124" font-size="11" fill="{GREY}" text-anchor="middle">损失 L(θ)：碗形，最低点就是最优解</text>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{RED if i==0 else JADE}" fill-opacity="{1 if i==0 else .8:.1f}"/>'
                  for i, (cx, cy) in enumerate([(62, 44), (88, 68), (112, 84), (134, 94), (152, 100)]))
        + f'<line x1="62" y1="44" x2="152" y2="100" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>'
        f'<text x="58" y="38" font-size="10" fill="{RED}" text-anchor="middle">起点</text>'
        f'<text x="150" y="112" font-size="10" fill="{JADE}" text-anchor="middle">最低点</text>'
        + "".join(f'<text x="{x}" y="{y}" font-size="9.5" fill="{GREY}">{i+1}</text>'
                  for i, (x, y) in enumerate([(72, 58), (98, 78), (122, 90), (142, 97)])),
        "每一步都朝着「更低」的方向迈，步子由学习率决定",
        """import numpy as np

def fit_gd(X, y, lr=0.05, iters=500):
    n, p = X.shape
    w = np.zeros(p); b = 0.0
    for k in range(iters):
        pred = X @ w + b
        gw = (2 / n) * X.T @ (pred - y)      # 对 w 的梯度
        gb = (2 / n) * (pred - y).sum()      # 对 b 的梯度
        w -= lr * gw                          # 朝梯度的反方向挪
        b -= lr * gb
        if k % 100 == 0:
            print(k, "loss = %.4f" % np.mean((pred - y) ** 2))
    return w, b

w, b = fit_gd(X, y)""",
    ))

    # ---- SGD / mini-batch
    s.append(card(
        "sgd", "随机 / 小批量梯度下降", "SGD / Mini-batch GD",
        "不看全部数据再挪一步，而是<b>抽一小批</b>就挪一步。方向没那么准，但快得多，还自带一点随机性，反而不容易卡在坑里。",
        "样本上十万、上百万时必用；神经网络的默认训练方式。",
        "批大小常取 32/64/128/256。 epochs 是「把全部数据过几遍」。记得每轮打乱顺序。",
        "θ ← θ − η·∇θ L(θ; B)，B 是一小批 &nbsp;&nbsp;·&nbsp;&nbsp; 一轮 = 把所有批次过一遍；一次 epoch = 看完一轮全量数据",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<path d="M24,20 C80,110 220,110 276,20" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
        f'<polyline points="64,42 84,66 96,58 112,84 124,74 138,96 150,88 158,102" '
        f'fill="none" stroke="{AMBER}" stroke-width="1.8"/>'
        f'<polyline points="64,42 100,78 132,94 158,102" fill="none" stroke="{JADE}" stroke-width="2"/>'
        f'<text x="232" y="40" font-size="10" fill="{AMBER}">小批量：路径抖</text>'
        f'<text x="232" y="56" font-size="10" fill="{JADE}">全批量：路径顺</text>'
        f'<text x="150" y="124" font-size="11" fill="{GREY}" text-anchor="middle">抖不是毛病：抖意味着它有机会跳出小坑，找到更低的谷</text>',
        "小批量路径更抖，但每一步便宜得多",
        """import numpy as np

def fit_sgd(X, y, lr=0.05, epochs=20, batch=64, seed=0):
    rng = np.random.default_rng(seed)
    n, p = X.shape
    w = np.zeros(p); b = 0.0
    for ep in range(epochs):
        idx = rng.permutation(n)               # 每轮打乱，这是必须的
        for s in range(0, n, batch):
            B = idx[s:s + batch]
            pred = X[B] @ w + b
            w -= lr * (2 / len(B)) * X[B].T @ (pred - y[B])
            b -= lr * (2 / len(B)) * (pred - y[B]).sum()
        print("epoch", ep, "loss = %.4f" % np.mean((X @ w + b - y) ** 2))
    return w, b""",
    ))

    # ---- 坐标下降
    s.append(card(
        "cd", "坐标下降", "Coordinate Descent",
        "一次只动<b>一个</b>变量，其余全锁住；轮着把所有变量都动一遍，再来第二轮。",
        "目标函数里有些部分不好求导（比如 L1 的尖角）——轮着一个一个来就绕过去了。Lasso 的默认解法。",
        "变量高度相关时收敛很慢（会来回拉扯）。先做标准化、先去掉完全共线的特征。",
        "对每个 j：β_j ← argmin_{β_j} L(β₁,…,β_j,…,β_p) &nbsp;&nbsp;·&nbsp;&nbsp; Lasso 的一步有闭式解（软阈值）",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<ellipse cx="150" cy="66" rx="{rx}" ry="{ry}" fill="none" stroke="{LINE}"/>'
                  for rx, ry in [(104, 46), (74, 33), (46, 20)])
        + f'<polyline points="40,40 40,84 96,84 96,56 130,56 130,70" fill="none" '
        f'stroke="{RED}" stroke-width="1.8"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{RED}"/>'
                  for cx, cy in [(40, 40), (40, 84), (96, 84), (96, 56), (130, 56), (130, 70)])
        + f'<circle cx="150" cy="66" r="3.4" fill="{JADE}"/>'
        f'<text x="150" y="124" font-size="11" fill="{GREY}" text-anchor="middle">每次只能横着走或竖着走，所以路是折线</text>',
        "等高线上看，坐标下降只能沿轴向拐直角",
        """import numpy as np

def lasso_cd(X, y, lam=0.1, iters=300):
    \"\"\"Lasso 的坐标下降：软阈值是关键一步。\"\"\"
    n, p = X.shape
    Xs = (X - X.mean(0)) / X.std(0)
    ys = y - y.mean()
    w = np.zeros(p)
    for _ in range(iters):
        for j in range(p):
            r = ys - Xs @ w + Xs[:, j] * w[j]      # 去掉第 j 个变量的贡献
            z = Xs[:, j] @ r / n
            w[j] = np.sign(z) * max(abs(z) - lam, 0) / (Xs[:, j] @ Xs[:, j] / n)
    return w

print("被压成 0 的变量数 =", (np.abs(lasso_cd(X, y)) < 1e-8).sum())""",
    ))

    # ---- 牛顿法
    s.append(card(
        "newton", "牛顿法", "Newton's Method",
        "不光看坡度（一阶导数），还看<b>坡度变化的速度</b>（二阶导数），所以能一步跨到接近谷底的位置。",
        "要高精度、参数不算多、目标函数光滑。GLM 的 IRLS 就是它的变体。",
        "每步要算 Hessian（p×p 矩阵），参数一多就贵。Hessian 可能不可逆，要加阻尼。",
        "θ ← θ − H⁻¹ ∇L(θ)，H = ∇²L(θ) &nbsp;&nbsp;·&nbsp;&nbsp; 每步 O(p³)，但迭代次数远少于梯度下降",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<path d="M24,20 C80,110 220,110 276,20" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="4.4" fill="{JADE}"/>'
                  for cx, cy in [(58, 40), (112, 82), (150, 100)])
        + f'<line x1="58" y1="40" x2="112" y2="82" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>'
        f'<line x1="112" y1="82" x2="150" y2="100" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>'
        f'<text x="52" y="34" font-size="10" fill="{RED}">第1步：跨很远</text>'
        f'<text x="150" y="118" font-size="10" fill="{JADE}" text-anchor="middle">两步就到</text>'
        f'<text x="150" y="128" font-size="10.5" fill="{GREY}" text-anchor="middle">步数少，但每步算得贵</text>',
        "牛顿法一步能跨很远，代价是每步更贵",
        """import numpy as np

def newton_1d(df, d2f, x0, iters=20, tol=1e-9):
    x = x0
    for k in range(iters):
        g, h = df(x), d2f(x)
        if abs(h) < 1e-12:        # Hessian 接近 0，退回梯度下降那一套
            break
        step = g / h
        x -= step
        if abs(step) < tol:
            break
    return x

# 例：最小化 f(x) = x^4 - 3x^2 + x
root = newton_1d(lambda x: 4*x**3 - 6*x + 1, lambda x: 12*x**2 - 6, x0=0.0)
print("x* =", round(root, 6))""",
    ))

    # ---- IRLS
    s.append(card(
        "irls", "IRLS", "Iteratively Reweighted Least Squares",
        "把「解不了的非线性问题」变成<b>一串能解的加权最小二乘</b>：先猜一次，按当前猜测给每个人算个权重，解一次，再猜……",
        "GLM（泊松、逻辑回归、Gamma）的标准解法。<b>本案例的 Poisson GLM 就是它</b>。",
        "看偏差（deviance）每轮下降多少，降不动了就停。权重可能爆炸，要加一点岭稳定项。",
        "β^{(t+1)} = (XᵀWX)⁻¹ XᵀW z，其中 W =  diag( (dμ/dη)² / V(μ) )，z = η + (y−μ)/(dμ/dη)",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<g transform="translate({30+i*62},52)">'
                  f'<rect x="0" y="0" width="50" height="30" rx="6" fill="{c}" fill-opacity="{o}"/>'
                  f'<text x="25" y="20" font-size="10.5" fill="{INK}" text-anchor="middle">{t}</text></g>'
                  for i, (c, o, t) in enumerate([("#8a8578", ".18", "猜 β⁰"),
                                                 (JADE, ".22", "算权重"),
                                                 (JADE, ".3", "解一次"),
                                                 (AMBER, ".32", "收敛?")]))
        + "".join(f'<line x1="{82+i*62}" y1="67" x2="{92+i*62}" y2="67" stroke="{GREY}"/>'
                  for i in range(3))
        + f'<path d="M262,40 C282,40 282,88 262,88" fill="none" stroke="{RED}" stroke-width="1.6"/>'
        f'<text x="292" y="66" font-size="11" fill="{RED}" text-anchor="middle">↺</text>'
        f'<text x="150" y="112" font-size="11" fill="{GREY}" text-anchor="middle">不收敛就带着新 β 回到「算权重」，重来</text>'
        f'<text x="150" y="126" font-size="9.5" fill="{GREY}" text-anchor="middle">本案例：IRLS 收敛了，偏差却只到常数基线的 {F["dev_wall"][1]["pct"]}%</text>',
        "IRLS 的循环：猜 → 加权 → 解 → 再看",
        """import numpy as np

def poisson_irls(X, y, offset=None, max_iter=80, tol=1e-8, ridge=1e-6):
    \"\"\"本库手写模型的核心（简化版），见 code/models.py。\"\"\"
    n, p = X.shape
    off = np.zeros(n) if offset is None else offset
    beta = np.zeros(p)
    for it in range(max_iter):
        eta = X @ beta + off
        mu = np.exp(np.clip(eta, -20, 20))          # 对数连接
        W = mu                                       # 泊松：权重就是 μ
        z = eta - off + (y - mu) / np.maximum(mu, 1e-8)
        A = X.T @ (X * W[:, None]) + ridge * np.eye(p)
        beta_new = np.linalg.solve(A, X.T @ (W * z))
        if np.max(np.abs(beta_new - beta)) < tol:
            return beta_new, it + 1
        beta = beta_new
    return beta, max_iter

beta, n_iter = poisson_irls(X, y)
print("迭代 %d 次收敛，系数 = %s" % (n_iter, np.round(beta, 3)))""",
        codenote="<p>本库实现见 "
                 + _cl("models", "def fit(self, X, y, w=None):",
                       label="models.py · PoissonRegressor.fit", nth=0) + "。</p>",
    ))

    # ---- CART 分裂
    s.append(card(
        "cart", "CART 分裂：基尼与熵", "Gini / Entropy Split",
        "把「哪个问题先问」量化：把两堆人的好坏比例代进公式，算出「混不混」，挑混得最轻的那一刀。",
        "训练决策树 / GBDT 时找最佳切点。<b>本案例的决策树动画就是它</b>。",
        "连续特征先分箱再找切点（本库分 24 箱）。叶子样本数下限一定要设，否则会切出一个人的叶子。",
        "基尼 Gini = 1 − Σp_k² &nbsp;&nbsp;·&nbsp;&nbsp; 熵 H = −Σp_k log p_k &nbsp;&nbsp;·&nbsp;&nbsp; 选使 n_L·G_L + n_R·G_R 最小的切点",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<text x="150" y="14" font-size="10.5" fill="{GREY}" text-anchor="middle">两个候选切点，哪个更「纯」？</text>'
        + "".join(f'<g transform="translate({24+i*136},26)">'
                  f'<text x="62" y="6" font-size="10" fill="{GREY}" text-anchor="middle">{t}</text>'
                  f'<rect x="0" y="12" width="124" height="30" rx="5" fill="{JADE}" fill-opacity="{o1}"/>'
                  f'<rect x="{w1}" y="12" width="{124-w1}" height="30" rx="5" fill="{RED}" fill-opacity="{o2}"/>'
                  f'<rect x="0" y="48" width="{w2}" height="30" rx="5" fill="{JADE}" fill-opacity="{o3}"/>'
                  f'<rect x="{w2}" y="48" width="{124-w2}" height="30" rx="5" fill="{RED}" fill-opacity="{o4}"/>'
                  f'<text x="62" y="92" font-size="10.5" fill="{c}" text-anchor="middle">基尼 {g}</text></g>'
                  for i, (t, w1, w2, o1, o2, o3, o4, c, g) in enumerate([
                      ("切法甲", 62, 20, ".5", ".5", ".8", ".15", GREY, "= 0.42"),
                      ("切法乙", 118, 8, ".85", ".12", ".9", ".08", RED, "= 0.11 ✓")]))
        + f'<text x="150" y="126" font-size="10.5" fill="{GREY}" text-anchor="middle">绿色越纯、红色越少 → 基尼越低 → 这一刀越好</text>',
        "右边那刀把好坏分得干净得多，就选它",
        """import numpy as np

def gini(y):
    p = np.bincount(y) / len(y)
    return 1 - np.sum(p ** 2)

def best_split(Xj, y, n_bin=24):
    \"\"\"在一个连续特征上找最佳切点：先分箱，只在箱边界试。\"\"\"
    cut = np.quantile(Xj, np.linspace(0, 1, n_bin + 1)[1:-1])
    best = (None, 1e9)
    for c in np.unique(cut):
        L, R = y[Xj <= c], y[Xj > c]
        if len(L) < 30 or len(R) < 30:     # 叶子太小不切
            continue
        g = (len(L) * gini(L) + len(R) * gini(R)) / len(y)
        if g < best[1]:
            best = (c, g)
    return best

c, g = best_split(X[:, 0], y)
print("最佳切点 %.3f，加权基尼 %.4f" % (c, g))""",
        codenote="<p>本库实现见 "
                 + _cl("models", "def _best_split", label="models.py · _best_split") + "。</p>",
    ))

    # ---- Boosting
    s.append(card(
        "boost", "Boosting 前向分步", "Forward Stagewise / Gradient Boosting",
        "一个一个地加模型：新的那个专门去补「目前还差多少」，加完一起算。每加一个，总误差就该降一点。",
        "弱模型（浅树）叠成强模型。GBDT、XGBoost、LightGBM、AdaBoost 都是这一族。",
        "学习率 η 控制每棵树的发言权；树太多会过拟合，用验证集 early_stopping 定数量。",
        "F_m(x) = F_{m−1}(x) + η·h_m(x)，h_m ≈ 残差 r = y − F_{m−1}(x)（回归）；也可用负梯度替代残差",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<g transform="translate({20+i*72},22)">'
                  f'<rect x="0" y="0" width="62" height="26" rx="5" fill="{JADE}" fill-opacity="{.2+.16*i:.2f}"/>'
                  f'<text x="31" y="17" font-size="10" fill="{INK}" text-anchor="middle">树 {i+1}</text>'
                  f'<text x="31" y="42" font-size="10" fill="{GREY}" text-anchor="middle">补 {v}</text></g>'
                  for i, v in enumerate(["+8.0", "+3.2", "+1.3", "…"]))
        + f'<line x1="20" y1="72" x2="286" y2="72" stroke="{LINE}"/>'
        f'<path d="M30,102 L90,96 L150,88 L210,84 L270,82" fill="none" stroke="{RED}" stroke-width="2"/>'
        f'<text x="150" y="122" font-size="10.5" fill="{GREY}" text-anchor="middle">合计后误差一路下降，但降幅越来越小</text>',
        "每棵树只补剩下的残差，串行累加",
        """import numpy as np

def gbdt_scratch(X, y, M=60, lr=0.08, max_depth=3):
    \"\"\"极简 GBDT：每棵树去拟合当前残差。\"\"\"
    from sklearn.tree import DecisionTreeRegressor
    pred = np.full(len(y), y.mean())
    trees = []
    for m in range(M):
        resid = y - pred                      # 还差多少
        t = DecisionTreeRegressor(max_depth=max_depth,
                                  min_samples_leaf=30, random_state=m)
        t.fit(X, resid)                       # 新树专补残差
        pred += lr * t.predict(X)             # 乘学习率后累加
        trees.append(t)
    return trees, pred

_, pred = gbdt_scratch(X, y)
print("RMSE = %.4f" % np.sqrt(np.mean((y - pred) ** 2)))""",
        codenote="<p>本库实现见 "
                 + _cl("models", "def fit(self, X, y, w=None):",
                       label="models.py · GBDT.fit", nth=3) + "。</p>",
    ))

    # ---- Bagging
    s.append(card(
        "bag", "Bagging 与自助抽样", "Bootstrap Aggregating",
        "从原数据里<b>有放回地抽</b>好几份，每份各训一个模型，最后投票/平均。抽样的随机性让模型们各不相同，误差就互相抵消了。",
        "模型本身不稳定（深树典型）、想降方差又不想改模型结构。随机森林就是「Bagging + 随机特征」。",
        "树数越多越稳，但有上限（约 300 后收益微小）。袋外样本（OOB）可以白捡一个验证集。",
        "ŷ_bag = (1/B) Σ f_b(x)&nbsp;&nbsp;·&nbsp;&nbsp; 每次抽样约 63.2% 的样本会被抽到，剩下的是袋外样本",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<rect x="112" y="10" width="76" height="24" rx="5" fill="#fff" stroke="{LINE}"/>'
        f'<text x="150" y="26" font-size="10.5" fill="{INK}" text-anchor="middle">原始数据</text>'
        + "".join(f'<line x1="{x1}" y1="34" x2="{x2}" y2="58" stroke="{LINE}"/>'
                  for x1, x2 in [(140, 60), (150, 150), (160, 240)])
        + "".join(f'<rect x="{x-32}" y="58" width="64" height="24" rx="5" fill="{AMBER}" fill-opacity=".2" stroke="{AMBER}"/>'
                  f'<text x="{x}" y="74" font-size="10" fill="{INK}" text-anchor="middle">抽样 {i+1}</text>'
                  for i, x in enumerate([60, 150, 240]))
        + "".join(f'<line x1="{x}" y1="82" x2="{x}" y2="100" stroke="{LINE}"/>' for x in [60, 150, 240])
        + "".join(f'<rect x="{x-28}" y="100" width="56" height="22" rx="5" fill="{JADE}" fill-opacity=".25"/>'
                  f'<text x="{x}" y="115" font-size="10" fill="{INK}" text-anchor="middle">模型 {i+1}</text>'
                  for i, x in enumerate([60, 150, 240]))
        + f'<line x1="60" y1="122" x2="150" y2="128" stroke="{GREY}"/>'
        f'<line x1="240" y1="122" x2="150" y2="128" stroke="{GREY}"/>'
        f'<text x="150" y="130" font-size="10" fill="{RED}" text-anchor="middle">▼ 取平均</text>',
        "有放回抽样造出多样性，最后投票",
        """import numpy as np
from sklearn.tree import DecisionTreeRegressor

def bagging(X, y, B=50, seed=0):
    rng = np.random.default_rng(seed)
    models, oob = [], []
    for b in range(B):
        idx = rng.choice(len(y), len(y), replace=True)   # 有放回
        m = DecisionTreeRegressor(max_depth=None, random_state=b).fit(X[idx], y[idx])
        models.append(m)
        oob.append(np.setdiff1d(np.arange(len(y)), np.unique(idx)))   # 袋外
    return models, oob

# 预测：所有树取平均
def predict(models, X):
    return np.mean([m.predict(X) for m in models], axis=0)""",
    ))

    # ---- Lloyd
    s.append(card(
        "lloyd", "Lloyd 迭代（K-Means 的解法）", "Lloyd's Algorithm",
        "两步交替：<b>①派点</b>（每人归到最近的中心）→ <b>②挪中心</b>（移到队员的平均位置）。两步都只会让总距离变小，所以必然停。",
        "训练 K-Means 聚类。也用于向量量化（把连续值压缩成有限档）。",
        "可能停在局部最优——多跑几个随机起点（<code>n_init=10</code>）取最好的。K 要事先定。",
        "① c_i = argmin_k ‖x_i − μ_k‖² &nbsp;&nbsp;② μ_k = mean{ x_i : c_i = k } &nbsp;&nbsp;·&nbsp;&nbsp; 每轮 O(nKp)",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{GREY}" fill-opacity=".6"/>'
                  for cx, cy in [(46, 40), (60, 56), (52, 74), (74, 48), (66, 88),
                                 (200, 42), (216, 58), (206, 78), (228, 50), (212, 92)])
        + f'<rect x="54" y="56" width="11" height="11" fill="{RED}" opacity=".35"/>'
        f'<rect x="60" y="62" width="11" height="11" fill="{RED}" opacity=".6"/>'
        f'<rect x="66" y="66" width="11" height="11" fill="{RED}"/>'
        f'<rect x="208" y="58" width="11" height="11" fill="{AMBER}" opacity=".35"/>'
        f'<rect x="206" y="64" width="11" height="11" fill="{AMBER}" opacity=".6"/>'
        f'<rect x="204" y="70" width="11" height="11" fill="{AMBER}"/>'
        f'<text x="150" y="112" font-size="10.5" fill="{GREY}" text-anchor="middle">方块从浅到深 = 中心一轮轮挪动，越挪越准</text>'
        f'<text x="150" y="126" font-size="10.5" fill="{GREY}" text-anchor="middle">派点 → 挪中心 → 再派点 …… 直到没人换队</text>',
        "中心一点点挪到位，挪到没人换队就停",
        """import numpy as np

def kmeans(X, K=3, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    mu = X[rng.choice(len(X), K, replace=False)]     # 随机起点
    for _ in range(iters):
        dist = ((X[:, None, :] - mu[None, :, :]) ** 2).sum(-1)
        lab = dist.argmin(1)                          # ①派点
        new_mu = np.array([X[lab == k].mean(0) for k in range(K)])   # ②挪中心
        if np.allclose(new_mu, mu):
            break
        mu = new_mu
    return lab, mu

lab, mu = kmeans(Xs, K=3)
print("各簇人数 =", np.bincount(lab))""",
    ))

    # ---- K 折交叉验证
    s.append(card(
        "cv", "K 折交叉验证", "K-Fold Cross Validation",
        "把数据切成 K 份，轮流拿其中 1 份当考试、其余当练习，考 K 次取平均。每个人都当过一次考生。",
        "<b>样本不多</b>、又想比较靠谱地估计「模型到了新数据上会怎样」。是调参时的标准评估法。",
        "分类问题用分层抽样（每折好坏比例一致）。<b>时间序列不能随机切</b>，要按时间切。切之前做的标准化要放进 pipeline。",
        "CV = (1/K) Σ_{k} 误差(在第 k 折上测试) &nbsp;&nbsp;·&nbsp;&nbsp; 常用 K = 5 或 10",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        + "".join(f'<g transform="translate(0,{16+i*22})">'
                  f'<text x="22" y="14" font-size="10" fill="{GREY}">第{i+1}轮</text>'
                  + "".join(f'<rect x="{52+j*40}" y="2" width="36" height="16" rx="3" '
                            f'fill="{RED if j==i else JADE}" fill-opacity="{.75 if j==i else .3}"/>'
                            for j in range(5))
                  + "</g>" for i in range(5))
        + f'<text x="150" y="128" font-size="10.5" fill="{GREY}" text-anchor="middle">红色是当次考试集，绿色是训练集 —— 每份都当过一次考题</text>',
        "五轮下来，每一份都当过一次考试集",
        """import numpy as np
from sklearn.model_selection import KFold, cross_val_score, StratifiedKFold
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

pipe = make_pipeline(StandardScaler(), HistGradientBoostingRegressor(max_iter=300))

# 回归：普通 K 折
scores = cross_val_score(pipe, X, y, cv=KFold(5, shuffle=True, random_state=0),
                         scoring="neg_root_mean_squared_error")
print("5 折 RMSE =", (-scores).round(3), " 平均 = %.3f" % -scores.mean())

# 分类要分层；时间序列改用 TimeSeriesSplit，千万别随机切""",
    ))

    # ---- 调参
    s.append(card(
        "tune", "调参：网格 / 随机 / 贝叶斯", "Grid / Random / Bayesian Search",
        "超参数是<b>人</b>定的（树深、学习率、正则强度），模型学不出来。调参就是有章法地试。",
        "模型定了、特征定了，想再抠几个点的精度。别把它当救世主——问题定义错了，调参救不回来。",
        "先粗后细：随机搜索定范围，再网格细搜。维度多（&gt;4 个）就上贝叶斯（Optuna）。<b>必须用交叉验证</b>，不能在测试集上挑。",
        "网格：穷举 ∏|Θ_i| 种组合 &nbsp;&nbsp;·&nbsp;&nbsp; 贝叶斯：用已试结果拟合「哪些区域更值得试」，再决定下一个点",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<text x="150" y="12" font-size="10.5" fill="{GREY}" text-anchor="middle">左：网格均匀铺开　右：贝叶斯越试越聚焦</text>'
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{GREY}" fill-opacity=".6"/>'
                  for cx in range(60, 145, 22) for cy in range(34, 118, 22))
        + "".join(f'<circle cx="{cx}" cy="{cy}" r="2.8" fill="{RED}" fill-opacity="{o}"/>'
                  for cx, cy, o in [(176, 108, ".25"), (196, 100, ".3"), (184, 88, ".4"),
                                    (206, 84, ".5"), (200, 72, ".62"), (216, 66, ".7"),
                                    (208, 56, ".8"), (222, 50, ".9"), (214, 44, "1"),
                                    (228, 40, "1"), (186, 96, ".3"), (198, 60, ".55")])
        + f'<circle cx="222" cy="42" r="7" fill="none" stroke="{JADE}" stroke-width="1.6"/>'
        f'<text x="238" y="40" font-size="10" fill="{JADE}">最优点</text>'
        f'<text x="150" y="128" font-size="10.5" fill="{GREY}" text-anchor="middle">同样 12 次试验，贝叶斯会把火力集中在有希望的区域</text>',
        "网格均匀铺，贝叶斯越试越聚焦",
        """from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import HistGradientBoostingRegressor
from scipy.stats import loguniform, randint

m = HistGradientBoostingRegressor(random_state=0)

# 随机搜索：先大范围摸底，便宜且常常够用
rs = RandomizedSearchCV(m, {
    "learning_rate": loguniform(1e-3, 3e-1),
    "max_depth": randint(2, 8),
    "max_iter": randint(100, 600),
}, n_iter=40, cv=5, scoring="neg_root_mean_squared_error",
   random_state=0, n_jobs=-1).fit(X, y)
print("随机搜索最优 =", rs.best_params_)

# 再在最优附近做小网格细搜
gs = GridSearchCV(m, {"learning_rate": [0.03, 0.05, 0.08],
                      "max_depth": [rs.best_params_["max_depth"]]},
                  cv=5, n_jobs=-1).fit(X, y)
print("细搜后 =", gs.best_params_, " RMSE = %.4f" % -gs.best_score_)

# 维度多就用 Optuna（pip install optuna，MIT 许可）""",
    ))

    # ---- 提前停止
    s.append(card(
        "stop", "提前停止", "Early Stopping",
        "训练时盯住验证集的表现：一旦 <b>连续若干轮不再变好</b>，就停下来，把最好的那一版留着。",
        "迭代类模型（GBDT、神经网络）几乎必配，既省时间又防过拟合。",
        "一定要留一块<b>没参与训练</b>的验证集。patience（容忍轮数）别太小，10–50 轮比较稳。",
        "若 metric(val) 连续 patience 轮未改善 → 停止，回退到最优轮次的模型",
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbf8ef"/>'
        f'<line x1="26" y1="106" x2="284" y2="106" stroke="{LINE}"/>'
        f'<line x1="26" y1="14" x2="26" y2="106" stroke="{LINE}"/>'
        + f'<polyline points="{",".join(f"{26+i*12},{104-int(v*78)}" for i, v in enumerate([.28,.42,.55,.64,.70,.74,.76,.775,.785,.79,.792,.793,.794,.7945]))}" fill="none" stroke="{JADE}" stroke-width="2"/>'
        + f'<polyline points="{",".join(f"{26+i*12},{104-int(v*78)}" for i, v in enumerate([.26,.40,.52,.60,.65,.68,.69,.685,.675,.66,.645,.63,.615,.60]))}" fill="none" stroke="{RED}" stroke-width="2"/>'
        + f'<line x1="{26+7*12}" y1="14" x2="{26+7*12}" y2="106" stroke="{AMBER}" stroke-dasharray="4 3"/>'
        f'<text x="{26+7*12}" y="12" font-size="10" fill="{AMBER}" text-anchor="middle">停在这</text>'
        f'<text x="60" y="126" font-size="10" fill="{JADE}">■ 训练集误差</text>'
        f'<text x="150" y="126" font-size="10" fill="{RED}">■ 验证集误差</text>'
        f'<text x="240" y="126" font-size="10" fill="{GREY}">越往后 →</text>',
        "训练误差还在降，验证误差已经开始抬头——就该停了",
        """import numpy as np

def early_stop(train_loss, val_loss, patience=20):
    \"\"\"返回应该停在第几轮（0-based）以及对应的最优验证损失。\"\"\"
    best = np.inf; best_i = 0; wait = 0
    for i, v in enumerate(val_loss):
        if v < best - 1e-6:
            best, best_i, wait = v, i, 0
        else:
            wait += 1
            if wait >= patience:
                return best_i, best
    return best_i, best

i, v = early_stop(tr, va)
print("停在第 %d 轮，验证损失 %.4f（继续跑到第 %d 轮只会更差）"
      % (i + 1, v, len(va)))""",
    ))

    s.append(f"""
<h2 id="stop2">算法的代价：一张复杂度速查</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>算法</th><th>单轮代价</th><th>通常轮数</th><th>什么时候不合适</th></tr>
<tr><td>闭式解</td><td>O(np² + p³)</td><td>1</td><td>p 很大（几千以上）</td></tr>
<tr><td>梯度下降（全量）</td><td>O(np)</td><td>10²–10³</td><td>n 极大时每轮太贵</td></tr>
<tr><td>小批量 GD</td><td>O(bp)</td><td>多轮 × (n/b)</td><td>几乎都能用</td></tr>
<tr><td>牛顿法 / IRLS</td><td>O(np² + p³)</td><td>5–50</td><td>p 上万时 Hessian 算不动</td></tr>
<tr><td>坐标下降</td><td>O(np)</td><td>10–10³</td><td>特征高度相关时慢</td></tr>
<tr><td>CART 找切点</td><td>O(np·bins)</td><td>每层一次</td><td>——</td></tr>
<tr><td>Lloyd（K-Means）</td><td>O(nKp)</td><td>10–100</td><td>簇形状不是圆的</td></tr>
</table></div>
<p class="tbl-cap">n = 样本数，p = 特征数，b = 批大小，K = 簇数。</p>
<div class="quote q-mgmt"><span class="q-tag">管 理 启 示</span>
<p>算法的贵，往往贵在<b>每轮要扫多少数据</b>，而不是贵在轮子数。
所以「先把数据抽样到能跑通，再全量跑」是性价比最高的一条工程经验。</p></div>""")

    return "\n".join(s)


PAGES_TOOL = [
    ("m01", "M", "常见模型速查", p_m01),
    ("a01", "A", "常见算法速查", p_a01),
]
