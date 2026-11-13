# -*- coding: utf-8 -*-
"""AI 实践库 · CODE「代码入口」

为什么要有这一页：
  正文里散着几十个源码链接（models.py L281、steps_678.py L105…），
  读者点进去是一片带行号的代码，看完回不来、也不知道这文件在整个项目里排第几。
  缺的是一个「总闸」——所有代码在这页站成一排，标明各自负责哪一段、
  哪一个阶段该看哪一份、想上手跑该敲什么。

这一页不做的事：不复述算法（各讲了），不再抄一遍数字（唯一来源是 out/facts.json）。
它只做三件事：**摆得下、找得到、能跑通**。

所有行号都是构建时从真实文件算出来的（走 _srcdoc.span），
改代码后重建一次就自动对齐，不许手写行号。
"""

import os as _os
import _srcdoc
from navmap import NAV
from pages_a import _toc, _step_frame
from pages_basics import _three

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

# 页号 / 标题，用于「相关页」反链（分组标题只有两个字段，先滤掉）
_NO, _TITLE = {}, {}
for _row in NAV:
    if len(_row) == 3:
        _n, _t, _no = _row
        if _t:
            _NO[_n] = _no
            _TITLE[_n] = _t


def _pg(*names):
    """相关页的一组链接，带页码，读的人知道在附录还是在第几阶段。"""
    out = []
    for n in names:
        if n in _TITLE:
            out.append(f'<a href="{n}.html"><span class="cd-pgno">{_NO[n]}</span>'
                       f'{_TITLE[n]}</a>')
    return " ".join(out)


def _lines_of(name):
    try:
        return len(_srcdoc._lines(_ROOT, name))
    except Exception:
        return 0


def _fn(name, label, marker, nth=0):
    """一个函数级链接：行号现算，标不到就退化成整文件链接。"""
    try:
        r = _srcdoc.span(_ROOT, name, marker, None, nth)
    except Exception:
        r = None
    if not r:
        return f'<a href="src/{name}.html">{label}</a>'
    return (f'<a href="src/{name}.html#L{r[0]}-L{r[1]}">{label}'
            f'<span class="cd-ln">L{r[0]}</span></a>')


def _card(name, what, funcs=(), pages=(), how=""):
    """一张文件卡：文件名 + 行数 + 干什么 + 关键函数入口 + 相关页。"""
    n = _lines_of(name)
    fn = ""
    if funcs:
        items = "".join(f"<li>{_fn(name, lb, mk, nth)}</li>"
                        for lb, mk, nth in funcs)
        fn = f'<div class="cd-fn"><b>从这里进去</b><ul>{items}</ul></div>'
    pg = f'<div class="cd-pg">{_pg(*pages)}</div>' if pages else ""
    extra = f'<div class="cd-how">{how}</div>' if how else ""
    return f"""
<div class="cdcard">
  <div class="cd-head"><a class="cd-file" href="src/{name}.html">{name}</a>
    <span class="cd-n">{n} 行</span></div>
  <div class="cd-what">{what}</div>
  {fn}{extra}{pg}
</div>"""


def _group(title, desc, cards):
    inner = "".join(cards)
    return f"""
<h3 class="cd-g-t">{title}</h3>
<p class="cd-g-d">{desc}</p>
<div class="cdgrid">{inner}</div>"""


_SHORTS = {
    "gen_data": "造数据：把业务机制写进代码",
    "models": "手写模型库（纯 NumPy）",
    "train_evaluate": "流水线第 1–5 步",
    "steps_678": "流水线第 6–8 步（真正的战场）",
    "_facts": "全站唯一数字来源",
    "_tune": "给现行评分找一组合适系数",
    "fig_01_look": "看数据的六张图",
    "fig_02_model": "模型侧九张图",
    "test_models": "手写模型的正确性自检",
    "_animfacts": "复算三个动画里的数字",
    "test_anim": "动画运行时自检",
    "anim_glm": "GLM 的 IRLS（动画源码）",
    "anim_tree": "决策树怎么挑分裂点（动画源码）",
    "anim_gbdt": "GBDT 逐轮补残差（动画源码）",
    "navmap": "导航骨架（单一信源）",
    "_build": "站点构建器",
    "_check": "站点自检：对账 + 查锚点",
    "_scan_svg": "扫描 SVG 画布溢出",
    "_srcdoc": "源码浏览生成器（行号现算）",
    "_fixno": "页号换算脚本",
    "terms": "术语词典（115 条）",
    "pages_a": "页面组件库",
    "pages_basics": "基础篇页面内容",
    "pages_up": "决策篇页面内容",
    "pages_b": "理论对照篇页面内容",
    "pages_c": "补充篇页面内容",
    "pages_p": "P01 翻译那一页",
    "pages_x": "X01 一页讲清楚 / X02 三个动画",
    "pages_glossary": "术语表页面",
    "pages_tools": "速查类页面",
    "pages_code": "本页",
}


def short_of(name):
    """别处（每页页尾的「本页用到的代码」）要用的那句短语，从这一处取。"""
    return _SHORTS.get(name, "")


# 页 → 这一页在讲的那份代码。
# 为什么不能只靠正文链接自动提取：讲某一页的时候，代码明明是主角，
# 正文里却常常没提文件名（ch09 讲外推，外推检测写在 steps_678.py 里，
# 但正文没出现过这个文件名）。这一张表负责「这一页的主题归到哪份代码」。
_SRC_OF_PAGE = {
    "index": ["_facts"],
    "p01": ["gen_data"],
    "b02": ["gen_data"],
    "b08": ["models", "fig_02_model"],
    "b10": ["train_evaluate", "steps_678"],
    "b11": ["models"],
    "ch01": ["models"],
    "ch02": ["gen_data", "_tune"],
    "ch03": ["train_evaluate", "models"],
    "ch04": ["models"],
    "ch05": ["models"],
    "ch06": ["models"],
    "ch07": ["steps_678", "fig_01_look"],
    "ch08": ["steps_678"],
    "ch09": ["steps_678", "train_evaluate"],
    "ch11": ["train_evaluate"],
    "ch12": ["train_evaluate", "steps_678"],
    "s03": ["steps_678"],
    "x02": ["_animfacts", "test_anim"],
}


def src_of_page(fn):
    return _SRC_OF_PAGE.get(fn, [])


def p_code(F):
    return f"""
{_toc([
    ("read", "先看三行：这页怎么用"),
    ("map", "七阶段 ↔ 该打开哪份代码"),
    ("core", "案例代码：一个文件干一件事"),
    ("anim", "动画源码：浏览器里跑的那套算法"),
    ("facts", "站里每个数字从哪来"),
    ("run", "我想自己跑一遍"),
    ("scaffold", "建站脚手架（不是案例代码）"),
])}

{_step_frame(
  "把散在 43 页正文里的那几十个源码链接收到一个总闸上，"
  "标明每个文件负责哪一段、端到端七步各自该打开哪一份。",
  "一张「七阶段 ↔ 代码」映射表、14 张文件卡（含行数与关键函数入口）、"
  "一条能自己跑起来的命令链。",
  "不必从头读到尾。读到哪一页卡住，就回来找那一页对应的文件；"
  "想上手跑就直接跳到「我想自己跑一遍」。")}

<h2 id="read">先看三行：这页怎么用</h2>
<p>这个库里出现的每一个数字、每一张图、每一个「模型学会了什么」的结论，
<b>都由 <code>code/</code> 下的真实代码跑出来</b>，没有一处是手写的示例。</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>你是谁</th><th>怎么打开这一页</th></tr>
<tr><td>只想确认「这是不是真的能跑」</td>
    <td>读 <a href="#run">我想自己跑一遍</a>，四条命令跑完整条流水线</td></tr>
<tr><td>读正文读到某一步，想看它具体怎么写的</td>
    <td>各页正文里带 <span class="codelink">绿色代码块</span> 的链接会直达那几行；
        忘了它在整个项目里的位置，回这一页看 <a href="#map">七阶段映射表</a></td></tr>
<tr><td>想改代码重跑自己的数据</td>
    <td>从 <a href="#core">案例代码</a> 的 <code>gen_data.py</code> 换数据、
        <code>steps_678.py</code> 换业务口径开始</td></tr>
</table></div>
<div class="note jade"><b>一条硬规矩：</b>页面里的数字全部来自
<code>out/facts.json</code>，而 <code>out/facts.json</code> 由
<a href="src/_facts.html">_facts.py</a> 从真实输出里抽取。
改了任何一处正文里的数字而没改代码，自检会报错——这条规矩让「讲的和做的一致」不至于沦为口号。</div>

<h2 id="map">七阶段 ↔ 该打开哪份代码</h2>
<p>端到端那七步，每一步对应哪些函数，一张表摊开。
<b>顺着这张表从上往下读</b>，比在仓库里翻着找省事：左边的行本身就是代码的执行顺序。</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>阶段</th><th>这一步在干什么</th><th>打开这份代码</th><th>关键入口</th></tr>
<tr><td>一 · 要不要做</td><td>算清现状成本与被错杀的人有多少</td>
    <td><a href="src/train_evaluate.html">train_evaluate.py</a></td>
    <td>{_fn("train_evaluate", "step1_load", "def step1_load")}</td></tr>
<tr><td>二 · 翻译成可算的题</td><td>定义 y「若承保的真实赔款」</td>
    <td><a href="src/train_evaluate.html">train_evaluate.py</a></td>
    <td>{_fn("train_evaluate", "step2_define_good", "def step2_define_good")}</td></tr>
<tr><td>三 · 训练</td><td>构造设计矩阵、切分数据集、训练四个模型</td>
    <td><a href="src/train_evaluate.html">train_evaluate.py</a> ＋
        <a href="src/models.html">models.py</a></td>
    <td>{_fn("train_evaluate", "step45_models", "def step45_models")}</td></tr>
<tr><td>四 · 检验</td><td>AUC / 提升度 / 校准 / 稳健性</td>
    <td><a href="src/models.html">models.py</a></td>
    <td>{_fn("models", "auc_score", "def auc_score")} ·
        {_fn("models", "lift_table", "def lift_table")}</td></tr>
<tr><td>五 · 把模型换成钱</td><td>增益曲线、圈选阈值、业务账</td>
    <td><a href="src/steps_678.html">steps_678.py</a></td>
    <td>{_fn("steps_678", "step7_business", "def step7_business")}</td></tr>
<tr><td>六 · 复盘落地</td><td>审计样本纠偏（IPW / 双重稳健）</td>
    <td><a href="src/steps_678.html">steps_678.py</a></td>
    <td>{_fn("steps_678", "step8_bias", "def step8_bias")}</td></tr>
<tr><td>七 · 上线之后</td><td>漂移监测、组织分工（清单见 SOP 页）</td>
    <td>{_pg("ch13", "s04")}</td>
    <td>—</td></tr>
</table></div>
<div class="tbl-cap">注：前六步都真实跑通过；第七步是上线后才开始的工作，
本站只给方法与清单（{_pg("ch13", "s04")}），没有假装跑过。</div>

<h2 id="core">案例代码：一个文件干一件事</h2>

{_group("数据从哪来", "整套数据是程序生成的 —— 只有这样，才能知道「真相」是什么，"
                 "也才敢说模型有没有学到真东西。真实业务里你拿不到这个真相，"
                 "所以要先用造数据校准直觉。", [
    _card("gen_data", "整个案例的数据生成器：把业务机制写进代码本身。"
          "年龄与风险的<b>非线性</b>、被拒保人群<b>没有出险标签</b>、"
          "「信息好不好查」被当成「风险高不高」的<b>渠道偏差</b>，都在这里造出来。",
          [("make_features", "def make_features", 0),
           ("true_latent", "def true_latent", 0),
           ("crude_score", "def crude_score", 0),
           ("simulate_claims", "def simulate_claims", 0)],
          ("b02", "ch02", "p01")),
    _card("_tune", "给 <code>crude_score</code>（现行核保评分）找一组合适系数，"
          "判据是「每一类人的承保率都得落在合理区间，让梯度成立」。"
          "这步看着琐碎，但它决定了后续案例能不能成立。",
          [("evaluate", "def evaluate", 0)],
          ("ch02",)),
    _card("fig_01_look", "看数据的六张图：漏斗、渠道偏差、分布漂移。"
          "原则写死在文件头 —— <b>每一张图都由真实数据算出，不画示意图</b>。",
          [("fig1_funnel", "def fig1_funnel", 0),
           ("fig2_channel", "def fig2_channel", 0)],
          ("ch02", "ch07")),
    _card("fig_02_model", "模型侧九张图：ROC、提升图、校准曲线、特征重要性、"
          "决策树长什么样。同样全部由真实预测结果绘制。",
          [("save", "def save", 0)],
          ("b08", "ch05", "ch06")),
])}

{_group("模型本体（纯 NumPy，零 sklearn）", "为什么要手写而不调库？因为「机器学习」这个词把一件朴素的事包装得太神秘。"
        "把 IRLS、树的切分查找、GBDT 逐轮补残差写成两百行能读的代码之后，"
        "它就只剩一句：<b>找一组参数，让猜错的代价最小</b>。", [
    _card("models", "手写模型库，四个模型 + 三个评价指标。",
          [("PoissonRegressor", "class PoissonRegressor", 0),
           ("LogisticRegression", "class LogisticRegression", 0),
           ("DecisionTreeRegressor", "class DecisionTreeRegressor", 0),
           ("GBDT", "class GBDT", 0),
           ("auc_score", "def auc_score", 0),
           ("lift_table", "def lift_table", 0)],
          ("ch01", "ch04", "ch05", "ch06", "a01", "m01")),
    _card("test_models", "手写模型的正确性自检：能用手算/已知答案验证的全部验证，"
          "不能手算的用「解析解 vs 数值解」互相印证。"
          "<b>这一段是为了解决「自己写的模型自己说好」的问题。</b>",
          [("check", "def check", 0)],
          ("m01", "a01")),
])}

{_group("端到端流水线", "从读数据到算出「能圈回多少好司机」，一条命令跑完。"
        "文件名的下划线是有意的：<code>train_evaluate</code> 管前五步，"
        "<code>steps_678</code> 管后三步 —— 因为后三步才是真正的战场。", [
    _card("train_evaluate", "步骤 1–5：读数据 → 定义什么叫「好司机」 → 构造设计矩阵 "
          "→ 切分数据集 → 训练并比较四个模型。",
          [("step1_load", "def step1_load", 0),
           ("step2_define_good", "def step2_define_good", 0),
           ("step3_dataset", "def step3_dataset", 0),
           ("step45_models", "def step45_models", 0)],
          ("b10", "ch03", "x02")),
    _card("steps_678", "步骤 6–8：给被拒的人打分 → 算业务账与圈选阈值 → "
          "用审计样本纠正选择偏差。<b>模型值多少钱，在这份文件里才有答案。</b>",
          [("step6_rejected", "def step6_rejected", 0),
           ("step7_business", "def step7_business", 0),
           ("step8_bias", "def step8_bias", 0)],
          ("ch07", "ch10", "ch11", "s03")),
])}

<h2 id="anim">动画源码：浏览器里跑的那套算法</h2>
<p>三个动画不是录屏，是<b>真在浏览器里一步步算</b>出来的：拖动滑杆改参数，
偏差、_iteration、叶子里的人数当场重算。想看这套数学怎么写成代码，链到下面三份。</p>
<div class="cdgrid">
{_card("anim_glm", "Poisson GLM 的 IRLS 迭代：每点一次「迭代一轮」，"
       "重加权最小二乘算一步，红色曲线（偏差）跟着往下走。",
       [("irlsStep", "function irlsStep", 0),
        ("deviance", "function deviance", 0)],
       ("ch04", "x02"))}
{_card("anim_tree", "决策树怎么挑分裂点：把每个候选问题的收益算一遍，"
       "谷底就是这一刀。<b>第三刀只在右半边的 36 人里找</b>，"
       "这段 vs 这个关系最容易看晕，代码里用 node 的 box 控制。",
       [("gini", "function gini", 0),
        ("splitGain", "function splitGain", 0),
        ("buildScene", "function buildScene", 0)],
       ("ch05", "x02"))}
{_card("anim_gbdt", "GBDT 逐轮补残差：每加一棵小树，MSE 掉一格，"
       "集成线从一条直线逐渐弯向真相。",
       [("fitStump", "function fitStump", 0),
        ("meanOf", "function meanOf", 0),
        ("sseOf", "function sseOf", 0)],
       ("ch06", "x02"))}
</div>
{_group("动画的数字也走自检", "动画里的数字不能比正文更随便 —— 它们同样要先算准、再写进页面。", [
    _card("_animfacts", "复算三个动画里的关键数字并写进 <code>out/anim_facts.json</code>："
          "GLM 最终 β₁、三刀的收益、GBDT 的 MSE 从多少降到多少。",
          (), ("x02",), how="这是 Node 脚本：<code>node code/_animfacts.js</code>"),
    _card("test_anim", "把三个动画在 Node 里（无头，不打开浏览器）跑一遍所有步骤，"
          "检查每一步的元素都在画布内、没有 NaN、没有卡死。",
          (), ("x02",), how="跑法：<code>node code/test_anim.js</code>"),
])}

<h2 id="facts">站里每个数字从哪来</h2>
{_facts_card()}

<div class="note amber"><b>为什么绕这一道：</b>直接把数字写进页面更快，但过两周就没人知道那个 96.6% 是怎么来的了。
现在这个数字只有一处定义，自检脚本（<a href="src/_check.html">_check.py</a>）
会拿页面里的数字跟 <code>facts.json</code> 对账，对不上直接报错。</div>

<h2 id="run">我想自己跑一遍</h2>
<div class="steps-ol">
<div class="so"><span class="so-n">1</span><div><b>装依赖</b>：
<code>pip install numpy pandas matplotlib</code>（只要这三个，<b>没有 sklearn</b>）</div></div>
<div class="so"><span class="so-n">2</span><div><b>造数据</b>：
在 <code>code/</code> 下执行 <code>python gen_data.py</code>，
生成 <code>data/drivers.csv</code> —— 连带生成那个「标准答案」，
后面才有得对照模型学得对不对</div></div>
<div class="so"><span class="so-n">3</span><div><b>跑整条流水线</b>：
<code>python train_evaluate.py</code>，从读数据跑到步骤 5 的模型比较，
过程里的九张图写到 <code>img/</code>；再跑 <code>steps_678.py</code> 走完后三步
（「能圈回多少被错杀的好司机」的答案在这一段才算得出来）</div></div>
<div class="so"><span class="so-n">4</span><div><b>抽数字、建站</b>：
<code>python _facts.py</code> 把结果抽进 <code>out/facts.json</code>，
<code>python _build.py</code> 重建全站，
最后 <code>python _check.py</code> 自检</div></div>
</div>
<div class="note red"><b>一个提醒：</b>数据是程序生成的，每次跑都会重新随机 N 个人 ——
所以你会看到和本站完全一样的<b>机制</b>，但不一定看到一模一样的<b>小数点</b>。
要复本站的数字，用同一随机种子重跑数据即可。</div>

<h2 id="scaffold">建站脚手架（不是案例代码）</h2>
<p>下面这些是把内容变成网页的脚本，跟机器学习没关系，但一并公开，
因为<b>这个库本身就是「可复算」这件事的一次实践</b> ——
连「怎么生成这个站」都应该能被打开看。</p>
<details class="fold"><summary>展开：站点是这么搭出来的（9 个文件）</summary><div class="fold-body">
<div class="tbl-wrap"><table class="tbl">
<tr><th>文件</th><th>行数</th><th>干什么</th></tr>
{_scaffold_rows()}
</table></div>
<p>一句话概括这套脚手架：<b>内容写进 Python 结构（pages_*.py），数字抽成一张事实表
（out/facts.json），导航只有一个源（navmap.py），每次全量重建。</b>
这么做的唯一理由是——改一处，全站跟上；不会出现侧栏说东、正文说西的情况。</p>
</div></details>

{_three([
    "<b>这个库里每一句话都能对上一份代码。</b>看不懂结论就去读代码，"
    "读不动代码也不耽误顺着正文往下走 —— 两边都不必写得太满。",
    "<b>链接的行号是算出来的，不是敲上去的。</b>"
    "由 <code>_srcdoc.py</code> 在构建时从真实文件计算，改了代码重建一次就自动对齐。",
    "<b>这一页的价值不在于让人读懂每一行</b>，"
    "而在于让人知道<b>想求证的时候去哪儿找</b>——这个库从头到尾不打算让人盲信。",
])}

<div class="quote q-talk"><span class="q-tag">下一步</span>
<p>看完代码想验一下自己学到多少：{_pg("q01")} 有 15 道题，每题都标了答案在第几页。
想直接对照术语表：{_pg("glossary")}。</p></div>
"""


_SCAFFOLD = [
    ("navmap", "AI 实践库导航骨架：侧栏与首页知识地图读同一份数据"),
    ("_build", "站点构建器：把 pages_*.py 的页面定义 + facts.json 的数字渲染成 HTML"),
    ("_check", "站点自检：标签闭合、数字一致性、锚点有效性等七类检查"),
    ("_scan_svg", "扫描嵌入 SVG：检查矩形重叠与文字溢出画布"),
    ("_srcdoc", "源码浏览生成器：产出 src/*.html，并为正文提供现算行号的链接"),
    ("_animfacts", "三个动画的数字复算器（Node）"),
    ("test_anim", "动画运行时自检（Node，无头遍历所有步骤）"),
    ("terms", "术语词典：115 条中英双语定义，驱动术语表与正文内联链接"),
    ("pages_a", "页面组件库：目录 / 三件事框 / 小结卡片等通用零件"),
    ("pages_basics", "基础篇 B1–B14 页面内容（含 B10 端到端七步图）"),
    ("pages_up", "决策篇 S1–S7 页面内容（要不要做 / 值不值 / 花多少钱…）"),
    ("pages_b", "理论对照篇 CH1–CH13 页面内容"),
    ("pages_c", "补充篇页面内容"),
    ("pages_p", "P01「把业务问题翻译成可计算的问题」"),
    ("pages_x", "X01 一页讲清楚 / X02 三个动画横向对齐"),
    ("pages_glossary", "术语表页面"),
    ("pages_tools", "速查类页面：模型速查 / 算法速查 / 自测题库 / 关于"),
    ("pages_code", "本页（代码入口）"),
]


def _facts_card():
    return _card(
        "_facts",
        "事实表抽取器 —— 整站的<b>唯一数字来源</b>。"
        "站点里被拒的 8,800 件、被错杀的 2,259 件、AUC 0.885、圈选纯度 96.6% 这些数，"
        "全部由它从真实输出里抽出来写进 <code>out/facts.json</code>，页面再从那里读。",
        [("r", "def r", 0), ("auc", "def auc", 0)],
        ("index",),
        how="改了任何一处计算，重跑它再重建站点，全站数字自动跟着变")


def _scaffold_rows():
    out = []
    for nm, desc in _SCAFFOLD:
        n = _lines_of(nm)
        out.append(f'<tr><td><a class="cd-file" href="src/{nm}.html">{nm}</a></td>'
                   f'<td class="num">{n}</td><td>{desc}</td></tr>')
    return "\n".join(out)
