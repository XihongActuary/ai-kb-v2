# -*- coding: utf-8 -*-
"""
AI 实践库 · 基础篇 B1–B8

写这一组页面的唯一目的：让「完全没接触过机器学习的人」能从头读下来。
所以每一页都守三条规矩（改稿时勿破）：
  1. 任何术语第一次出现，必须紧跟一句大白话，不许直接甩缩写。
  2. 能用图说清的，不写三段字。
  3. 每页结尾必须有「看完你该记住的三句话」。

2026-10-03 扩充（参照「一图看懂机器学习」系列信息图）：
  4. 新增 B10 端到端七步流程（含每步对应源码文件）／B11 算法四分区／
     B12 选模型决策路径／B13 六个误区，把「概念」串成「能跑通的一条线」。
"""
import os as _os
import _srcdoc

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def _cl(fname, marker=None, end=None, label=None, nth=0):
    """指向真实源码片段的链接，点击在新窗口打开。

    行号不是写死的：构建时从 code/*.py 现算，改了代码重建就自动对齐。
    marker 省略时链到整个文件；nth 用来区分同名方法（如四个 fit）。
    """
    if marker is None:
        return (f'<a class="codelink" href="src/{fname}.html" target="_blank" '
                f'rel="noopener">{label or fname}</a>')
    return _srcdoc.link(_ROOT, fname, marker, end, label or fname, nth)


from pages_a import _toc, _step_frame

INK = "#2b2a26"
GREY = "#8a8578"
RED = "#b53d2e"
JADE = "#2f6b5a"
AMBER = "#9a6f12"
LINE = "#ddd5c2"


def _svg(w, h, inner, cap=""):
    # 宽图在手机上等比例缩小会把字压得看不见，改为横向可滑动、保底宽度
    cls = "sv wide" if w > 560 else "sv"
    s = (f'<div class="{cls}"><svg viewBox="0 0 {w} {h}" '
         f'xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto">'
         f'{inner}</svg>')
    if cap:
        s += f'<div class="fig-cap">{cap}</div>'
    return s + "</div>"


def _cmp_table(rows, head):
    h = ['<div class="tbl-wrap"><table class="tbl"><tr>']
    for x in head:
        h.append(f"<th>{x}</th>")
    h.append("</tr>")
    for r in rows:
        h.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    h.append("</table></div>")
    return "".join(h)


def _why(title, plain, formula, symbols, prove=""):
    """「为什么」公式卡：白话一句 + 一行公式 + 符号说明，默认折叠。

    不展开推导，只回答「凭什么」——给想从「是什么」走到「为什么」的人留的第二通道。
    不想看的人永远不会被它挡路，因为它收着。
    """
    sym = "".join(f"<li><code>{k}</code> — {v}</li>" for k, v in symbols)
    inner = (f'<div class="fx">{formula}</div>'
             f'<p class="explain">{plain}</p>'
             f'<ul class="sym">{sym}</ul>')
    if prove:
        inner += f'<p class="explain">{prove}</p>'
    return (f'<details class="fold why"><summary>{title}</summary>'
            f'<div class="fold-body">{inner}</div></details>')


def _quiz(q, ans, why=""):
    """一道自测题：题干 + 折叠的答案 + 为什么反直觉。"""
    body = f'<p>{ans}</p>'
    if why:
        body += f'<p class="explain">{why}</p>'
    return (f'<div class="quiz"><div class="q-h">问</div>'
            f'<div class="q-b"><p>{q}</p>'
            f'<details class="fold"><summary>看答案</summary>'
            f'<div class="fold-body">{body}</div></details></div></div>')


def _three(items):
    """「看完你该记住的三句话」"""
    h = ['<div class="note jade"><b>看完这一页，你只需要记住三句话</b><ol>']
    for x in items:
        h.append(f"<li>{x}</li>")
    h.append("</ol></div>")
    return "".join(h)


def _cycle_svg():
    """B1 用：传统编程 / 机器学习训练 / 机器学习预测，三格对照。"""
    def panel(x, title, a, b, c, note, bullets, accent):
        cx = x + 103
        f = f'font-size="11" fill="{INK}" text-anchor="middle"'
        rects = (f'<rect x="{x+8}" y="58" width="58" height="30" rx="5" fill="#fff" stroke="{LINE}"/>'
                 f'<text x="{x+37}" y="78" {f}>{a}</text>'
                 f'<text x="{x+74}" y="78" font-size="12" fill="{GREY}">＋</text>'
                 f'<rect x="{x+84}" y="58" width="60" height="30" rx="5" fill="#fff" stroke="{LINE}"/>'
                 f'<text x="{x+114}" y="78" {f}>{b}</text>'
                 f'<text x="{x+150}" y="78" font-size="12" fill="{GREY}">＝</text>'
                 f'<rect x="{x+158}" y="58" width="38" height="30" rx="5" fill="{accent}" opacity="0.14" stroke="{accent}"/>'
                 f'<text x="{x+177}" y="78" {f}>{c}</text>')
        bl = "".join(f'<text x="{x+14}" y="{y}" font-size="10.5" fill="{GREY}">{t}</text>'
                     for y, t in zip((134, 154, 174), bullets))
        return (f'<rect x="{x}" y="22" width="206" height="200" rx="10" fill="#fbf8ef" stroke="{LINE}"/>'
                f'<text x="{cx}" y="44" font-size="12.5" fill="{INK}" text-anchor="middle">{title}</text>'
                f'{rects}'
                f'<text x="{cx}" y="110" font-size="10.5" fill="{GREY}" text-anchor="middle">{note}</text>'
                f'{bl}')

    body = (panel(6, "① 传统编程（改代码）", "数据", "规则", "结果", "规则是人写的",
                  ["· 规则由人定", "· 适合逻辑明确的事", "· 规则变了要手改"], GREY)
            + panel(219, "② 机器学习 · 训练", "数据", "标签", "模型", "标签就是已知答案",
                    ["· 学的是 X→y 的映射", "· 规律让机器自己找", "· 找不到就叫欠拟合"], JADE)
            + panel(432, "③ 机器学习 · 预测", "新数据", "模型", "预测", "用已经训练好的模型",
                    ["· 输入从没见过的人", "· 输出分数 / 类别", "· 本案例给 8,800 人打分"], AMBER))
    return _svg(644, 232, body,
                "三个阶段连起来就是机器学习全部：人写规则 → 数据加标签 train 出模型 → 模型给新数据打分。")


# ============================================================ B1 机器学习在干什么
def p_b01(F):
    inner = f"""
<rect x="8" y="8" width="300" height="200" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="158" y="34" font-size="13.5" fill="{GREY}" text-anchor="middle">老办法：人写规则</text>
<rect x="40" y="50" width="236" height="30" rx="6" fill="#fff" stroke="{LINE}"/>
<text x="158" y="70" font-size="12.5" fill="{INK}" text-anchor="middle">年龄&lt;25 → 加 5 分</text>
<rect x="40" y="88" width="236" height="30" rx="6" fill="#fff" stroke="{LINE}"/>
<text x="158" y="108" font-size="12.5" fill="{INK}" text-anchor="middle">性能车 → 加 6 分</text>
<rect x="40" y="126" width="236" height="30" rx="6" fill="#fff" stroke="{LINE}"/>
<text x="158" y="146" font-size="12.5" fill="{INK}" text-anchor="middle">线上渠道 → 加 7 分</text>
<text x="158" y="176" font-size="12" fill="{RED}" text-anchor="middle">规则谁定的？人。人知道真规律吗？不一定。</text>
<text x="158" y="196" font-size="12" fill="{GREY}" text-anchor="middle">结果：{F['n_wrongly_killed']:,} 个好人被错杀</text>

<rect x="336" y="8" width="300" height="200" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="486" y="34" font-size="13.5" fill="{GREY}" text-anchor="middle">新办法：机器从例子里总结</text>
<rect x="368" y="50" width="236" height="30" rx="6" fill="#fff" stroke="{LINE}"/>
<text x="486" y="70" font-size="12.5" fill="{INK}" text-anchor="middle">{F['n_acc']:,} 个已承保的人</text>
<rect x="368" y="88" width="236" height="30" rx="6" fill="#fff" stroke="{LINE}"/>
<text x="486" y="108" font-size="12.5" fill="{INK}" text-anchor="middle">＋ 他们真实的出险记录</text>
<path d="M486 120 L486 136" stroke="{JADE}" stroke-width="2" marker-end="url(#ar)"/>
<rect x="368" y="140" width="236" height="34" rx="6" fill="{JADE}" opacity="0.12" stroke="{JADE}"/>
<text x="486" y="161" font-size="12.5" fill="{JADE}" text-anchor="middle">机器自己算出来的规律</text>
<text x="486" y="196" font-size="12" fill="{JADE}" text-anchor="middle">哪个因子真的影响风险，它说了算</text>
<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
<path d="M0,0 L8,4 L0,8 z" fill="{JADE}"/></marker></defs>
"""
    return f"""
<h1><span class="thin">基础篇 · B1</span>
机器学习到底在干什么</h1>
<p class="lead">一句话：<b>机器学习就是「用一堆过去的答案，换一套能应付新问题的规则」。</b>
它不神秘，也不聪明 —— 它只是看过更多例子，并且从不嫌烦。</p>

{_toc([("game", "先玩一个猜价格的游戏"), ("old", "老办法：人写规则"), ("new", "新办法：让机器总结"), ("three", "三样东西缺一不可")])}

<h2 id="game">先玩一个猜价格的游戏</h2>
<p>假设你被扔到一个陌生城市，要猜一套房子值多少钱。你完全不认识这个城市。</p>
<p>现在给你两个选择：</p>
<ul>
<li><b>选择一：</b>给你一本《房价评估手册》，上面写着「地铁房加 10 万、学区房加 30 万、楼层每高一层加 1 万」。</li>
<li><b>选择二：</b>不给你手册，但给你这个城市最近成交的 1,000 套房子的资料 —— 面积、楼层、离地铁多远、成交价。</li>
</ul>
<p>你会选哪个？大多数人会选二。因为手册是人写的，写手册的人可能漏了「朝南」这个关键因素；
而 1,000 条真实成交记录里，藏着这个城市真正的定价逻辑。</p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p><b>机器学习就是那个「选择二」。</b>你不教它规则，你给它例子，让它自己把规则找出来。
它找出来的规则可能长得不好看（几百个数字），但它是从真实数据里长出来的，不是拍脑袋拍出来的。</p></div>

<h2 id="old">老办法：人写规则 —— 我们的核保规则就是这么来的</h2>
{_svg(644, 216, inner, "左边是人拍脑袋写规则，右边是机器从数据里总结。本案例里，左边的规则冤枉了 2,259 个人。")}
<p>我们这个案例里，保险公司用的就是「老办法」：一套核保规则分，
年龄、车型、地区、渠道各加几分，加到阈值以上就拒保。这套规则讲得通，但它有两个致命问题：</p>
<ol>
<li><b>权重是人拍的。</b>「线上渠道加 7 分」这个 7 是哪来的？大概率是某次开会定的。</li>
<li><b>它把「信息难不难拿到」当成了「风险高不高」。</b>线上渠道的客户不是更危险，
只是资料不全 —— 结果线上渠道的错杀率是代理渠道的 {F['kill_ratio_online_vs_agent']} 倍。</li>
</ol>

<h2 id="new">新办法：让机器自己总结</h2>
<p>机器学习做的事，拆成大白话只有三步：</p>
<div class="steps">
<div class="step"><h4>第一步 · 找一批「已知答案」的人</h4>
<p>我们有 {F['n_acc']:,} 个已经承保的客户。他们有没有出险、赔了多少钱，系统里都有记录。
这就是<b>带答案的例题</b>。</p></div>
<div class="step"><h4>第二步 · 让机器反复试</h4>
<p>机器先瞎猜一条规律，算一遍发现差得远，就改一点；再算，再改。
改几百次之后，它的规律和真实记录对得上大部分了。这个过程叫<b>训练</b>。</p></div>
<div class="step"><h4>第三步 · 拿它去答新题</h4>
<p>{F['n_rej']:,} 个被拒保的人，从来没有出险记录。把他们的资料喂给训练好的机器，
它会给出每个人的<b>预测风险</b>。谁低谁就是被冤枉的人。</p></div>
</div>

<h2 id="cycle">完整的一圈：先训练出模型，再用模型答题</h2>
<p>「机器学习」这个词最容易让人以为机器在「思考」。换个看法就清爽了：
它其实是<b>两个阶段拼起来</b>——先拿过去的答案训练出一个「模型」，再拿这个模型去答新题。</p>
{_cycle_svg()}
<p>注意看中间和右边的区别：<b>训练</b>那一步，喂进去的是「数据 ＋ 已知答案」；
<b>预测</b>那一步，喂进去的是「新数据 ＋ 已经训练好的模型」。
我们这个案例里，<b>8,800 个被拒保的人，就是右边那一格「新数据」</b>——
模型没见过他们，只能靠训练时学到的规律去推。</p>

<h2 id="three">三样东西缺一不可</h2>
{_cmp_table([
    ["<b>数据</b>", "过去的例子", f"本案例的 {F['n_total']:,} 份申请 + {F['n_acc']:,} 份真实出险记录"],
    ["<b>模型</b>", "一个「输入→输出」的套路", "可以是直线（GLM），可以是一串问题（决策树）"],
    ["<b>算法</b>", "把套路里的数字找出来的方法", "反复改、一步步逼近，就是最常用的算法思路"],
], ["三要素", "大白话", "本案例里是什么"])}
<p>这三者的关系，用一句话串起来：
<b>算法拿着数据，把模型里的数字调好。</b>模型是成品，数据是原料，算法是加工工艺。</p>

{_three([
    "机器学习不是让机器「思考」，是让机器「从例子里总结规律」。",
    "它比人强的地方不是聪明，是<b>不厌其烦</b>：同一个动作它能重复几十万次而不走神。",
    "它比人弱的地方是<b>不懂因果</b>：数据里有什么规律它就学什么，包括那些假的规律。后面第 33 页会专门讲这件事。",
])}

<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>判断一件事该不该上机器学习，只需问一句：<b>你手上有没有一大批「已知答案」的历史例子？</b>
有，就可以上；没有，再高级的算法也变不出答案来。这才是立项时该问的第一个问题。</p></div>
"""


# ============================================================ B2 数据长什么样
def p_b02(F):
    inner = f"""
<rect x="10" y="10" width="624" height="34" rx="4" fill="{JADE}" opacity="0.1"/>
<text x="322" y="32" font-size="13" fill="{JADE}" text-anchor="middle">一行 = 一个人　一列 = 一个属性</text>
<text x="30" y="68" font-size="12" fill="{GREY}">driver_id</text>
<text x="130" y="68" font-size="12" fill="{GREY}">年龄</text>
<text x="210" y="68" font-size="12" fill="{GREY}">车型</text>
<text x="300" y="68" font-size="12" fill="{GREY}">车值(万)</text>
<text x="400" y="68" font-size="12" fill="{GREY}">年里程</text>
<text x="490" y="68" font-size="12" fill="{GREY}">渠道</text>
<text x="580" y="68" font-size="12.5" fill="{RED}">出险次数</text>
<line x1="20" y1="76" x2="624" y2="76" stroke="{LINE}"/>
<text x="30" y="98" font-size="12" fill="{INK}">D00001</text>
<text x="130" y="98" font-size="12" fill="{INK}">34</text>
<text x="210" y="98" font-size="12" fill="{INK}">轿车</text>
<text x="300" y="98" font-size="12" fill="{INK}">18.2</text>
<text x="400" y="98" font-size="12" fill="{INK}">15,500</text>
<text x="490" y="98" font-size="12" fill="{INK}">代理</text>
<text x="580" y="98" font-size="12.5" fill="{RED}">0</text>
<text x="30" y="124" font-size="12" fill="{INK}">D00002</text>
<text x="130" y="124" font-size="12" fill="{INK}">27</text>
<text x="210" y="124" font-size="12" fill="{INK}">SUV</text>
<text x="300" y="124" font-size="12" fill="{INK}">31.0</text>
<text x="400" y="124" font-size="12" fill="{INK}">22,800</text>
<text x="490" y="124" font-size="12" fill="{INK}">线上</text>
<text x="580" y="124" font-size="12.5" fill="{RED}">2</text>
<text x="30" y="150" font-size="12" fill="{INK}">D00003</text>
<text x="130" y="150" font-size="12" fill="{INK}">52</text>
<text x="210" y="150" font-size="12" fill="{INK}">轿车</text>
<text x="300" y="150" font-size="12" fill="{INK}">12.4</text>
<text x="400" y="150" font-size="12" fill="{INK}">8,900</text>
<text x="490" y="150" font-size="12" fill="{INK}">直销</text>
<text x="580" y="150" font-size="12.5" fill="{RED}">0</text>
<rect x="20" y="166" width="500" height="40" rx="6" fill="{JADE}" opacity="0.08" stroke="{JADE}" stroke-dasharray="4 3"/>
<rect x="544" y="166" width="76" height="40" rx="6" fill="{RED}" opacity="0.08" stroke="{RED}" stroke-dasharray="4 3"/>
<text x="270" y="191" font-size="12.5" fill="{JADE}" text-anchor="middle">← 特征 X：机器的输入</text>
<text x="582" y="191" font-size="12.5" fill="{RED}" text-anchor="middle">← 标签 y</text>
<text x="270" y="228" font-size="12" fill="{GREY}" text-anchor="middle">已知条件</text>
<text x="582" y="228" font-size="12" fill="{GREY}" text-anchor="middle">标准答案</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B2</span>
数据长什么样：一行一个人</h1>
<p class="lead">机器学习吃的不是「知识」，是一张表。
看懂这张表的结构，后面的大部分术语就自动明白了。</p>

{_toc([("table", "一张表的解剖"), ("xy", "X 和 y：已知条件和答案"), ("missing", "本案例最要命的地方：答案缺失")])}

<h2 id="table">一张表的解剖</h2>
{_svg(644, 244, inner, "左边六列是「已知条件」，右边一列是「答案」。机器学习干的事，就是学会从左边推出右边。")}

<h2 id="xy">X 和 y：已知条件和答案</h2>
<p>这张表在机器学习的语言里，被切成两半：</p>
{_cmp_table([
    ["<b>X（特征）</b>", "每个人的已知条件：年龄、车型、车值、里程、渠道", "考试时的<b>题目</b>"],
    ["<b>y（标签）</b>", "我们想知道的那个真值：这一年出了几次险、赔了多少钱", "习题册最后几页的<b>答案</b>"],
], ["符号", "本案例里是什么", "打个比方"])}
<p>有 <code>y</code> 的学习叫<b>监督学习</b>（有人对答案），没有 <code>y</code>、只把长得像的归成一堆叫<b>无监督学习</b>。
我们这个案例从头到尾都是监督学习。</p>

<h2 id="missing">本案例最要命的地方：答案缺失</h2>
<p>现在请你注意一件会毁掉整个任务的事：</p>
<div class="note red"><b>被拒保的 {F['n_rej']:,} 个人，是没有 <code>y</code> 的。</b>
他们从没被承保，所以系统里根本不存在他们的出险记录。<br><br>
在数据里，这一列被记成 <code>-1</code>。<b>请务必分清：</b>
<code>-1</code> 的意思是「这个人我们不知道」，<b>不是</b>「这个人一次险都没出过」。
如果你手滑把它当成 0，等于宣称「所有被拒保的人都是完美司机」—— 那模型会学出一个荒唐的结论。</div>
<p>这件事带来一个连锁后果，也决定了整个案例的难度：</p>
<ul>
<li>我们只能用<b>已承保的 {F['n_acc']:,} 人</b>来训练模型；</li>
<li>却要拿它去给<b>{F['n_rej']:,} 个没见过的人</b>打分；</li>
<li>而这两拨人<b>不是同一类人</b> —— 被拒的那批，恰恰是规则认为「有问题」的那批。</li>
</ul>
<p>这就是本案例真正的挑战所在。整件事的困难，不是算法难，是<b>训练数据和用它的地方不一样</b>。
后面第 31 页「外推风险」会专门讲这里翻的车。</p>

{_three([
    "数据就是一张表：<b>一行一个对象，一列一个属性</b>。",
    "表里分两半：<b>X 是已知条件，y 是标准答案</b>。学模型就是学会从 X 推 y。",
    "本案例的 <code>-1</code> 表示<b>「不知道」而不是「零」</b> —— 这一字之差会毁掉整个模型。",
])}
"""


# ============================================================ B3 模型是什么
def p_b03(F):
    inner = f"""
<rect x="8" y="8" width="308" height="216" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="162" y="32" font-size="13.5" fill="{GREY}" text-anchor="middle">模型一：一条直线（GLM 的亲戚）</text>
<line x1="34" y1="196" x2="292" y2="196" stroke="{LINE}"/>
<line x1="34" y1="52" x2="34" y2="196" stroke="{LINE}"/>
<text x="300" y="200" font-size="11" fill="{GREY}">年龄</text>
<text x="20" y="50" font-size="11" fill="{GREY}">出险</text>
<circle cx="72" cy="88" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="104" cy="112" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="136" cy="132" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="168" cy="148" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="200" cy="162" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="232" cy="176" r="4" fill="{JADE}" opacity="0.55"/>
<circle cx="264" cy="186" r="4" fill="{JADE}" opacity="0.55"/>
<line x1="44" y1="78" x2="284" y2="196" stroke="{RED}" stroke-width="2.6"/>
<text x="180" y="70" font-size="12" fill="{RED}">预测 = a + b × 年龄</text>
<text x="162" y="216" font-size="12" fill="{GREY}" text-anchor="middle">一句话：越老越安全，匀速下降</text>

<rect x="336" y="8" width="308" height="216" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="490" y="32" font-size="13.5" fill="{GREY}" text-anchor="middle">模型二：一串问题（决策树）</text>
<rect x="462" y="48" width="120" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="522" y="65" font-size="11.5" fill="{INK}" text-anchor="middle">年龄 &lt; 25 ?</text>
<line x1="490" y1="74" x2="420" y2="98" stroke="{LINE}"/>
<line x1="550" y1="74" x2="616" y2="98" stroke="{LINE}"/>
<text x="404" y="92" font-size="11" fill="{JADE}">是</text>
<text x="628" y="92" font-size="11" fill="{GREY}">否</text>
<rect x="366" y="98" width="112" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="422" y="115" font-size="11.5" fill="{INK}" text-anchor="middle">车值 &gt; 30 万?</text>
<rect x="558" y="98" width="112" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="614" y="115" font-size="11.5" fill="{INK}" text-anchor="middle">年里程?</text>
<line x1="400" y1="124" x2="376" y2="150" stroke="{LINE}"/>
<line x1="446" y1="124" x2="470" y2="150" stroke="{LINE}"/>
<rect x="330" y="150" width="88" height="28" rx="5" fill="{RED}" opacity="0.1" stroke="{RED}"/>
<text x="374" y="168" font-size="11.5" fill="{RED}" text-anchor="middle">高风险</text>
<rect x="432" y="150" width="88" height="28" rx="5" fill="{JADE}" opacity="0.1" stroke="{JADE}"/>
<text x="476" y="168" font-size="11.5" fill="{JADE}" text-anchor="middle">低风险</text>
<rect x="558" y="150" width="112" height="28" rx="5" fill="{AMBER}" opacity="0.12" stroke="{AMBER}"/>
<text x="614" y="168" font-size="11.5" fill="{AMBER}" text-anchor="middle">再看下一问</text>
<text x="490" y="206" font-size="12" fill="{GREY}" text-anchor="middle">一句话：分人群，各自给一个数</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B3</span>
模型是什么：一个会算数的套路</h1>
<p class="lead">别被这个词吓到。<b>模型就是一个「丢进去、吐出来」的固定套路</b>：
你给它一个人的资料，它还你一个数。就这么多。</p>

{_toc([("blackbox", "模型是个黑盒子吗"), ("two", "两种最常见的套路"), ("para", "学模型 = 找数字")])}

<h2 id="blackbox">模型是个黑盒子吗</h2>
<p>很多人以为模型是个神秘黑箱。其实你每天在用模型：</p>
{_cmp_table([
    ["菜谱", "放什么料、放多少", "出什么菜", "是"],
    ["体检报告评分表", "各项指标", "健康总分", "是"],
    ["我们的核保规则分", "年龄、车型、渠道", "规则分（拒/保）", "是"],
    ["银行贷款审批表", "收入、负债、征信", "贷不贷", "是"],
], ["你熟悉的东西", "输入", "输出", "它其实就是模型吗"])}
<p>看见了吗？<b>我们的核保规则分，本身就是一个模型</b> —— 只是它的数字是人拍的。
机器学习做的，是把「人拍的数字」换成「从数据里算出来的数字」。</p>

<h2 id="two">两种最常见的套路</h2>
{_svg(644, 232, inner, "左边是「一条线」型，右边是「一串问题」型。本案例两个都用了，最后把它们拼起来。")}

<h3>套路一：一条线（GLM / 线性回归）</h3>
<p>公式长这样：<b>预测值 = a + b₁×年龄 + b₂×车值 + …</b>。
每一项都乘一个系数再加起来。它最大的好处是 —— <b>每个系数都能讲出业务含义</b>。
比如算出 <code>b₁ = −0.03</code>，你就能直接说「年龄每涨一岁，出险率约降 3%」。
这正是精算师熟悉的语言，也是为什么这个库从它开始讲。</p>

<h3>套路二：一串问题（决策树）</h3>
<p>公式是一连串「是/否」问题：年龄小于 25 吗？是 → 车值大于 30 万吗？否 → …
走到最后一片叶子，就得到一个数。<b>它的好处是能表达「拐弯」的规律</b> ——
比如「年轻人才在乎车值，年长的人不在乎」。一条直线表达不了这种规律，树可以。</p>

{_cmp_table([
    ["<b>一条线（GLM）</b>", "各行其是，匀速叠加", "能，系数就是业务含义", "表达不了拐弯、交叉"],
    ["<b>一串问题（树）</b>", "分人群，各给一个数", "能，看得出走了哪条路", "边界是硬的，不够平滑"],
], ["套路", "怎么算的", "能解释吗", "短板"])}
<p>本案例最后用的，是把两者拼起来：<b>频率用一条线预测，损失用一串问题预测，然后相乘</b>。
这个思路在第 25 页会展开。</p>

<h2 id="para">学模型 = 找数字</h2>
<p>模型里那些 <code>a</code>、<code>b₁</code>、<code>b₂</code> 叫<b>参数</b>（也叫系数）。
模型刚建好的时候，这些数字是空的 —— 或者干脆全是 0。
<b>所谓的「训练模型」，就是把这些数字一个一个找出来。</b></p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>模型是空的表格，参数是表格里的空格，训练就是把空格填满。
第 26 页的动画，就是一格一格填这些空格的过程 —— 你可以亲眼看着它填。</p></div>

{_three([
    "模型 = <b>输入 → 输出</b>的固定套路，你每天都在用好几个。",
    "「一条线」能解释但不会拐弯；「一串问题」会拐弯但边界生硬。本案例两者都用。",
    "学模型 = <b>把模型里那几个空数字填上</b>，没有别的玄机。",
])}
"""


# ============================================================ B4 训练是什么
def p_b04(F):
    inner = f"""
<line x1="48" y1="26" x2="48" y2="196" stroke="{LINE}"/>
<line x1="48" y1="196" x2="596" y2="196" stroke="{LINE}"/>
<text x="20" y="34" font-size="11" fill="{GREY}">离谱</text>
<text x="20" y="196" font-size="11" fill="{GREY}">程度</text>
<text x="470" y="214" font-size="11.5" fill="{GREY}">改的次数（轮）</text>
<path d="M60 44 C 130 78, 190 108, 250 132 C 320 156, 420 176, 580 186"
      fill="none" stroke="{RED}" stroke-width="2.6"/>
<circle cx="60" cy="44" r="4.5" fill="{RED}"/>
<circle cx="150" cy="88" r="4" fill="{RED}" opacity="0.8"/>
<circle cx="250" cy="132" r="4" fill="{RED}" opacity="0.65"/>
<circle cx="380" cy="164" r="4" fill="{RED}" opacity="0.5"/>
<circle cx="580" cy="186" r="4.5" fill="{JADE}"/>
<text x="72" y="38" font-size="11.5" fill="{RED}">第 0 次：瞎猜，差得离谱</text>
<text x="300" y="120" font-size="11.5" fill="{RED}">每改一次就小一点</text>
<text x="470" y="182" font-size="11.5" fill="{JADE}">改不动了 → 停（收敛）</text>
<line x1="60" y1="44" x2="580" y2="44" stroke="{LINE}" stroke-dasharray="3 3"/>
<line x1="580" y1="186" x2="580" y2="196" stroke="{JADE}" stroke-dasharray="3 3"/>
"""
    return f"""
<h1><span class="thin">基础篇 · B4</span>
训练是什么：反复改，直到改不动</h1>
<p class="lead">训练这件事，用一句大白话讲完：
<b>先瞎猜一次，看看差多少，往对的方向挪一点，再来一遍 —— 挪到挪不动为止。</b></p>

{_toc([("loss", "先造一把尺：猜得有多离谱"), ("loop", "然后重复同一个动作"), ("stop", "什么时候停")])}

<h2 id="loss">先造一把尺：猜得有多离谱</h2>
<p>机器猜了一个数，我们怎么知道它猜得准不准？需要一把尺。这把尺叫<b>损失函数</b>
（名字很唬人，意思就是「扣分表」）。</p>
{_cmp_table([
    ["真实出了 2 次险，模型猜 0.5 次", "差 1.5 次", "扣很多分"],
    ["真实出了 2 次险，模型猜 1.8 次", "差 0.2 次", "扣一点点分"],
    ["真实出了 2 次险，模型猜 2.0 次", "差 0", "不扣分"],
], ["举个例子", "差多少", "扣分表怎么记"])}
<p>把所有人的扣分加起来，得到一个总分 —— 这就是那把尺。
<b>训练的全部目标，就是把这把尺上的读数压到最低。</b></p>
<div class="note"><b>为什么叫「损失」？</b>因为它是你为猜错付出的代价。
训练就是尽量少付代价。换个名字你就懂了：它其实就是「总分越低越好」的考试分数。</div>

<h2 id="loop">然后重复同一个动作</h2>
{_svg(644, 226, inner, "横轴是「改了多少次」，纵轴是「还差多远」。一开始降得快，后面越来越慢 —— 最后基本不动，就是收敛。")}
<p>每一次「改」都严格走这三小步，一次不差：</p>
<div class="steps">
<div class="step"><h4>① 用当前的数字算一遍</h4>
<p>把 {F['n_train']:,} 个训练样本挨个过一遍，每人得出一个预测值。</p></div>
<div class="step"><h4>② 看看差多少、往哪边差</h4>
<p>拿预测值和真实值比。谁被高估了、谁被低估了、平均差多少 —— 全算出来。</p></div>
<div class="step"><h4>③ 往对的方向挪一点</h4>
<p>高估了就往下调，低估了就往上调。<b>注意是「挪一点」，不是「一步到位」</b> ——
一次挪太猛容易走过头，来回震荡。</p></div>
</div>
<p>这三小步，机器可以在一秒钟里重复几十次。人做这件事会烦死，机器不会。
<b>这就是机器学习的全部秘密：它只是不厌其烦。</b></p>

<h2 id="stop">什么时候停</h2>
<p>看上面那张图的右端：曲线越来越平，最后几乎不动了。这叫<b>收敛</b>。
判断方法可以很朴素：<b>这一轮的改进量小到可以忽略，就停。</b></p>
<p>在本案例的 GLM 动画里（<a href="ch04.html">第 26 页</a>），你会亲眼看到这个过程：
第 1 次改动幅度巨大，第 3 次已经很像样，到第 7 次基本不动。</p>

{_three([
    "训练 = <b>猜 → 看差距 → 往对的方向挪一点</b>，然后把这三步重复很多次。",
    "「损失函数」就是那把尺，名字吓人，意思就是<b>猜错的扣分表</b>。",
    "挪到<b>挪不动</b>就叫收敛，可以停了 —— 不是算不出来，是再算也没意义。",
])}
"""


# ============================================================ B5 过拟合
def p_b05(F):
    inner = f"""
<rect x="8" y="8" width="200" height="200" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="108" y="30" font-size="12.5" fill="{GREY}" text-anchor="middle">① 学得太少：没学会</text>
<line x1="28" y1="176" x2="188" y2="176" stroke="{LINE}"/>
<circle cx="52" cy="80" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="80" cy="138" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="108" cy="68" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="136" cy="150" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="164" cy="90" r="3.5" fill="{JADE}" opacity="0.5"/>
<line x1="34" y1="112" x2="182" y2="112" stroke="{RED}" stroke-width="2.4"/>
<text x="108" y="196" font-size="11.5" fill="{GREY}" text-anchor="middle">一条平线，明显没抓住规律</text>

<rect x="222" y="8" width="200" height="200" rx="10" fill="#fbf8ef" stroke="{JADE}"/>
<text x="322" y="30" font-size="12.5" fill="{JADE}" text-anchor="middle">② 刚刚好：学会了</text>
<line x1="242" y1="176" x2="402" y2="176" stroke="{LINE}"/>
<circle cx="266" cy="80" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="294" cy="138" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="322" cy="68" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="350" cy="150" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="378" cy="90" r="3.5" fill="{JADE}" opacity="0.5"/>
<path d="M248 130 C 290 120, 320 80, 356 108 C 380 124, 396 132, 400 134"
      fill="none" stroke="{RED}" stroke-width="2.4"/>
<text x="322" y="196" font-size="11.5" fill="{JADE}" text-anchor="middle">平滑跟随，抓住了趋势</text>

<rect x="436" y="8" width="200" height="200" rx="10" fill="#fbf8ef" stroke="{RED}"/>
<text x="536" y="30" font-size="12.5" fill="{RED}" text-anchor="middle">③ 学过了：把噪声背下来了</text>
<line x1="456" y1="176" x2="616" y2="176" stroke="{LINE}"/>
<circle cx="480" cy="80" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="508" cy="138" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="536" cy="68" r="3.5" fill="{JADE}" opacity="0.5"/><circle cx="564" cy="150" r="3.5" fill="{JADE}" opacity="0.5"/>
<circle cx="592" cy="90" r="3.5" fill="{JADE}" opacity="0.5"/>
<path d="M462 132 L480 80 L494 130 L508 138 L522 96 L536 68 L550 128 L564 150 L578 100 L592 90 L610 122"
      fill="none" stroke="{RED}" stroke-width="2.2"/>
<text x="536" y="196" font-size="11.5" fill="{RED}" text-anchor="middle">每个点都穿过，但换批人就崩</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B5</span>
过拟合：背熟了习题，考砸了考试</h1>
<p class="lead">这是机器学习<b>第一号翻车原因</b>，也是最容易骗过新手的一个 ——
因为它在训练时看起来完美无缺。</p>

{_toc([("exam", "一个你一定经历过的比喻"), ("pic", "三种状态"), ("split", "怎么防：把题分成两拨"), ("case", "本案例里的实际衰减")])}

<h2 id="exam">一个你一定经历过的比喻</h2>
<p>考试前，有人刷完了全部历年真题，每道题的答案都背下来了。你问他什么他都会 ——
但那只是因为他<b>见过</b>。等考试换了数字，他就崩了。</p>
<p>另一个人没背题，而是搞懂了背后的公式。考试时题是新的，但他照样会做。</p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p><b>过拟合 = 死记硬背。</b>模型把训练数据里每一次偶然的波动都当成了规律记下来，
包括那些纯粹是运气的噪声。它以为自己学得很好，其实只是背得很好。</p></div>

<h2 id="pic">三种状态</h2>
{_svg(644, 212, inner, "同一个数据集，三种学法的区别。中间那个是对的；右边那个每个点都穿过了，但那是背下来的，不是学会的。")}

<h2 id="split">怎么防：把题分成两拨</h2>
<p>办法朴素得让人意外 —— <b>不要把全部数据都给模型看</b>。我们这样切：</p>
{_cmp_table([
    ["<b>训练集</b>", f"{F['n_train']:,} 人（{F['n_train']/F['n_acc']*100:.0f}%）", "练习题：<b>答案一起给</b>，模型照着学"],
    ["<b>验证集</b>", "工程里常另留一份", "模拟考：学的过程中用来调旋钮（树多深、走多快），但答案不算进期末考"],
    ["<b>测试集</b>", f"{F['n_test']:,} 人（{F['n_test']/F['n_acc']*100:.0f}%）", "正式考：<b>答案先藏起来</b>，学完才拿出来对，分数才算数"],
], ["数据集", "本案例规模", "作用（考试比喻）"])}
<div class="note"><b>练习题 / 模拟考 / 正式考，正好对应训练集 / 验证集 / 测试集。</b>
本案例为求简洁只用了两份；实战里建议加第三份「验证集」——
它用来在学的过程中调那些<b>人来拧的旋钮</b>（见 <a href="b06.html">B6</a>），
调好再上正式考，免得为了模拟考分数把模型改歪。三个字诀：<b>训练看题、验证调参、测试定生死。</b></div>
<p>关键规则只有一条，但必须死守：<b>测试集在训练结束之前，一次都不许看。</b>
看了，它就不叫考试了 —— 那等于提前把答案告诉考生。</p>
<p>怎么判断过拟合？看两个数：</p>
<ul>
<li><b>训练集上的分数很高</b>（它背熟了）；</li>
<li><b>测试集上的分数明显更低</b>（换题就崩）。</li>
</ul>
<p>这两个数的<b>差距</b>，就是过拟合的程度。差距越大，背得越死。</p>

<h2 id="case">本案例里的实际衰减</h2>
<p>我们把手上 {F['n_acc']:,} 个已承保客户按上面说的切成两拨，然后对比两个分数：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>模型</th><th class="num">训练集 AUC</th><th class="num">测试集 AUC</th><th class="num">衰减</th></tr>
{"".join(f'<tr><td>{c["name"]}</td><td class="num">{c["train"]:.3f}</td><td class="num">{c["test"]:.3f}</td><td class="num">{c["decay"]:+.1f}%</td></tr>' for c in F["overfit"])}
</table></div>
<div class="tbl-cap">AUC 是衡量排序能力的分数（0.5=瞎猜，1.0=完美）。衰减很小，说明这几个模型没有明显背题。</div>
<div class="note jade"><b>这次为什么没翻车？</b>因为我们给模型设了几道限制：树不许太深、
每个叶子至少要装够一定数量的人、系数不许长得太大（这叫<b>正则化</b>）。
这些限制的作用，就是不让它有本事去背下每一个偶然。</div>

{_three([
    "过拟合 = <b>背熟了训练题、换题就崩</b>。它在训练时看起来完美，所以最容易骗人。",
    "防它的办法就一招：<b>留出一份从没见过的数据当期末考</b>，考前一次都不许看。",
    "看两个数判断：<b>训练集分数高、测试集分数低、差距大</b> —— 三点凑齐就是过拟合。",
])}
"""


# ============================================================ B6 算法是什么
def p_b06(F):
    inner = f"""
<rect x="14" y="14" width="180" height="188" rx="10" fill="#fbf8ef" stroke="{LINE}"/>
<text x="104" y="40" font-size="13" fill="{GREY}" text-anchor="middle">方法一：一步算出来</text>
<rect x="40" y="58" width="128" height="30" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="104" y="77" font-size="12" fill="{INK}" text-anchor="middle">套公式</text>
<path d="M104 88 L104 106" stroke="{JADE}" stroke-width="2" marker-end="url(#a2)"/>
<rect x="40" y="108" width="128" height="30" rx="5" fill="{JADE}" opacity="0.12" stroke="{JADE}"/>
<text x="104" y="127" font-size="12" fill="{JADE}" text-anchor="middle">答案直接出来</text>
<text x="104" y="158" font-size="11.5" fill="{GREY}" text-anchor="middle">快，但要求严格</text>
<text x="104" y="176" font-size="11.5" fill="{GREY}" text-anchor="middle">只有简单模型能用</text>

<rect x="208" y="14" width="180" height="188" rx="10" fill="#fbf8ef" stroke="{RED}"/>
<text x="298" y="40" font-size="13" fill="{RED}" text-anchor="middle">方法二：慢慢挪过去</text>
<rect x="234" y="58" width="128" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="298" y="75" font-size="12" fill="{INK}" text-anchor="middle">先瞎猜</text>
<path d="M298 84 L298 98" stroke="{RED}" stroke-width="2" marker-end="url(#a2)"/>
<rect x="234" y="100" width="128" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="298" y="117" font-size="12" fill="{INK}" text-anchor="middle">看差多少 → 挪一点</text>
<path d="M298 126 L262 148" stroke="{GREY}" stroke-width="1.6"/>
<path d="M262 148 L298 142" stroke="{GREY}" stroke-width="1.6" marker-end="url(#a2)"/>
<text x="360" y="150" font-size="11.5" fill="{GREY}">回到上一步</text>
<text x="298" y="176" font-size="11.5" fill="{GREY}" text-anchor="middle">本案例的 GLM 用这个</text>

<rect x="402" y="14" width="180" height="188" rx="10" fill="#fbf8ef" stroke="{AMBER}"/>
<text x="492" y="40" font-size="13" fill="{AMBER}" text-anchor="middle">方法三：一路贪心切</text>
<rect x="428" y="58" width="128" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="492" y="75" font-size="12" fill="{INK}" text-anchor="middle">全体人站一屋</text>
<path d="M492 84 L492 98" stroke="{AMBER}" stroke-width="2" marker-end="url(#a2)"/>
<rect x="428" y="100" width="128" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="492" y="117" font-size="12" fill="{INK}" text-anchor="middle">挑一刀切成两半</text>
<path d="M492 126 L492 140" stroke="{AMBER}" stroke-width="2" marker-end="url(#a2)"/>
<rect x="428" y="142" width="128" height="26" rx="5" fill="#fff" stroke="{LINE}"/>
<text x="492" y="159" font-size="12" fill="{INK}" text-anchor="middle">各半再各自切一刀</text>
<text x="492" y="182" font-size="11.5" fill="{GREY}" text-anchor="middle">决策树用这个</text>
<defs><marker id="a2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
<path d="M0,0 L8,4 L0,8 z" fill="{GREY}"/></marker></defs>
"""
    return f"""
<h1><span class="thin">基础篇 · B6</span>
算法是什么：把数字找出来的工艺</h1>
<p class="lead">先分清两个常被混为一谈的词：
<b>模型是成品，算法是造它的工艺。</b>同一盘菜（模型），可以有不同的做法（算法）。</p>

{_toc([("mv", "模型和算法，别再搞混"), ("three", "三种找法"), ("gd", "loss 是尺，梯度下降是手"),
       ("round", "一轮、一批、一次更新"), ("knob", "人还要拧的旋钮"), ("reg", "正则化：给它设个上限")])}

<h2 id="mv">模型和算法，别再搞混</h2>
{_cmp_table([
    ["<b>模型</b>", "一个填好数字的套路", "那盘菜", "「用年龄和车值算风险」"],
    ["<b>算法</b>", "把数字填进去的步骤", "菜谱上的操作步骤", "「先猜再改，改到不动为止」"],
], ["概念", "它是什么", "打个比方", "本案例里的例子"])}
<p>所以「学模型」和「跑算法」是同一件事的两面：<b>算法跑完了，模型就填好了。</b></p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p><b>算法就是菜谱。</b>同样的食材（数据）、同样的菜（模型），换本菜谱做法就不同：
有的直接套公式一步出锅（线性回归），有的先尝一口再调味、反复到合适（IRLS），
有的把食材一层层切分归类（决策树）。<b>「上 AI」不是换了一道菜，是换了本菜谱——
食材还是那盘数据，别被「算法」两个字吓住。</b></p></div>

<h2 id="three">三种找法</h2>
{_svg(596, 210, inner, "左边一步到位，中间反复挪，右边一层层切。本案例三种都用到过。")}
<div class="tbl-wrap"><table class="tbl">
<tr><th>找法</th><th>大白话</th><th>本案例谁在用</th></tr>
<tr><td>一步算出来</td><td>有现成公式，把数代进去就出答案</td><td>最简单的线性回归</td></tr>
<tr><td>慢慢挪过去</td><td>先瞎猜，看差距，挪一点，重复到不动</td><td><b>Poisson GLM</b>（第 26 页动画）</td></tr>
<tr><td>一路贪心切</td><td>每次挑「当前最能分清好坏」的一刀切下去</td><td><b>决策树、GBDT</b>（第 05、06 页动画）</td></tr>
</table></div>

<h2 id="gd">loss 是那把尺，梯度下降是那双手</h2>
<p>「慢慢挪过去」这条路走得通，靠两样东西：<b>一把尺（损失函数）</b>告诉你现在差多少，
<b>一双手（梯度下降）</b>告诉你该往哪挪、挪多大。</p>
<p><b>损失函数</b>：一个数字，专门记录「模型当前猜得有多离谱」。训练的全部目标，就是让这个数字不断变小。
<b>梯度下降</b>：每次朝「误差下降最快的那个反方向」挪一小步。学习率就是步长。</p>
{_svg(628, 236, f"""
<text x="26" y="20" font-size="12.5" fill="{GREY}">左：雾天俯视一片山地，等高线就是「一样高的地方」</text>
<text x="352" y="20" font-size="12.5" fill="{GREY}">右：误差随挪的步数一路往下</text>
<ellipse cx="152" cy="152" rx="94" ry="64" fill="none" stroke="{LINE}"/>
<ellipse cx="152" cy="152" rx="72" ry="49" fill="none" stroke="{LINE}"/>
<ellipse cx="152" cy="152" rx="51" ry="35" fill="none" stroke="{LINE}"/>
<ellipse cx="152" cy="152" rx="33" ry="22" fill="none" stroke="{LINE}"/>
<ellipse cx="152" cy="152" rx="16" ry="11" fill="none" stroke="{LINE}"/>
<ellipse cx="256" cy="70" rx="30" ry="20" fill="none" stroke="{AMBER}"/>
<ellipse cx="256" cy="70" rx="18" ry="12" fill="none" stroke="{AMBER}"/>
<ellipse cx="256" cy="70" rx="8" ry="5" fill="none" stroke="{AMBER}"/>
<circle cx="152" cy="152" r="4" fill="{JADE}"/>
<text x="152" y="176" font-size="11" fill="{JADE}" text-anchor="middle">最深的那处（全局最优）</text>
<circle cx="256" cy="70" r="3.5" fill="{AMBER}"/>
<text x="256" y="40" font-size="11" fill="{AMBER}" text-anchor="middle">看着也到底了</text>
<text x="256" y="54" font-size="11" fill="{AMBER}" text-anchor="middle">其实是小坑（局部最优）</text>
<polyline points="58,78 94,108 118,128 134,144 148,152" fill="none" stroke="{JADE}" stroke-width="2.2"/>
<circle cx="58" cy="78" r="4.5" fill="{JADE}"/>
<circle cx="94" cy="108" r="3" fill="{JADE}"/>
<circle cx="118" cy="128" r="3" fill="{JADE}"/>
<circle cx="134" cy="144" r="3" fill="{JADE}"/>
<circle cx="148" cy="152" r="3" fill="{JADE}"/>
<text x="58" y="66" font-size="10.5" fill="{GREY}" text-anchor="middle">起点</text>
<polyline points="128,54 184,48 222,60 248,67" fill="none" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="4 3"/>
<line x1="332" y1="40" x2="332" y2="170" stroke="{LINE}"/>
<line x1="332" y1="170" x2="606" y2="170" stroke="{LINE}"/>
<polyline points="334,46 374,56 414,70 454,88 494,110 534,130 574,146" fill="none" stroke="{JADE}" stroke-width="2.2"/>
<circle cx="374" cy="56" r="3" fill="{JADE}"/><circle cx="414" cy="70" r="3" fill="{JADE}"/>
<circle cx="454" cy="88" r="3" fill="{JADE}"/><circle cx="494" cy="110" r="3" fill="{JADE}"/>
<circle cx="534" cy="130" r="3" fill="{JADE}"/>
<text x="474" y="196" font-size="11.5" fill="{GREY}" text-anchor="middle">越走越平 = 每次改进越来越小 = 收敛</text>
<text x="470" y="86" font-size="11" fill="{GREY}" text-anchor="middle">忽上忽下？</text>
<text x="470" y="102" font-size="11" fill="{RED}" text-anchor="middle">步长太大</text>
<text x="470" y="118" font-size="11" fill="{RED}" text-anchor="middle">的学习率</text>
""", "左图：山越低误差越小，球滚到最深那处就停了；右图：误差一路往下、末段压平就是收敛。")}
<div class="tbl-wrap"><table class="tbl">
<tr><th>本案例里，这三样具体是什么</th><th>对应的东西</th></tr>
<tr><td>损失函数（尺）</td><td>次数类模型的误差量，本案例用 <b>偏差 Deviance</b></td></tr>
<tr><td>参数（被挪的东西）</td><td>GLM 的各因子系数、GBDT 每棵树的位置与叶子值</td></tr>
<tr><td>学习率（步长）</td><td>GBDT 每次只补 8%，而不是把误差一次补满</td></tr>
<tr><td>起点</td><td>先给一版「所有人都一样」的常数预测</td></tr>
</table></div>

<h2 id="round">一轮、一批、一次更新</h2>
<p>新手最常被这三个词绕晕，其实一句话就够：
<b>Epoch 是「过一遍」，Batch 是「一次拿多少」，Iteration 是「更新一次」。</b></p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>词</th><th>它是啥</th><th>打个比方</th></tr>
<tr><td><b>Epoch（一轮）</b></td><td>全部训练数据完整过一遍</td><td>一届学生从开学到毕业，整套课走完</td></tr>
<tr><td><b>Batch（一批）</b></td><td>一次参数更新拿出来的那一小撮数据</td><td>一次交上来批改成的一摞作业</td></tr>
<tr><td><b>Batch Size</b></td><td>一批装几个人</td><td>一摞作业里有几份</td></tr>
<tr><td><b>Iteration（一次更新）</b></td><td>算完梯度、把参数挪一下</td><td>批改完这一摞、改一下答案</td></tr>
<tr><td><b>Epoch = 几轮 × Batch = 几次更新</b></td><td>全部数据 ÷ 一批 = 一轮里更新几次</td><td>1000 人、每批 100 人 → 10 批 → 一轮批 10 次</td></tr>
</table></div>
<p>那么用全部数据还是一条数据？三种做法各有脾气：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>做法</th><th>每次用多少数据</th><th>好处</th><th>麻烦</th></tr>
<tr><td>全量梯度下降</td><td>全部一起算</td><td>方向稳</td><td>数据一多就慢得离谱</td></tr>
<tr><td>随机梯度下降</td><td>每次 1 条</td><td>极快</td><td>一忽一忽地抖</td></tr>
<tr><td><b>小批量（32/64/128）</b></td><td>每次一小撮</td><td>又快又稳，主流选择</td><td>要多设一个 batch size</td></tr>
</table></div>
<div class="note"><b>本案例的口径：</b>{F["n_train"]:,} 条训练数据、按 {F["n_test"]:,} 条留作测试，
剩下的走 <b>训练 → 验证 → 测试</b> 三段式。<b>每动一次超参数，都是在验证集上做的；
测试集只用来做最后那一次「期末考试」。</b>拿测试集反复调，测试集就作废了 —— 这是最常见的自欺。</div>

<h2 id="knob">人还要拧的旋钮</h2>
<p>有一类数字，机器<b>学不出来，得你提前定</b>。它们叫<b>超参数</b>。
「超」的意思就是「站在参数之上、管着参数的」。</p>
{_cmp_table([
    ["树最多分几层", "分得越细越容易背题（过拟合）", "本案例：4 层"],
    ["每片叶子最少装几个人", "装太少 = 为个别人单独定制 = 背题", "本案例：最少 30 人"],
    ["每次挪多大步（学习率）", "步子太大容易走过头，太小要走很久", "本案例：0.08，即每次只补 8%"],
    ["一共加多少棵树", "树越多越强，但也越容易背题", "本案例：60 棵"],
], ["旋钮", "拧错了会怎样", "本案例的取值"])}
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>这就是为什么「上 AI」不是买个软件就完事。<b>这些旋钮需要懂业务的人来拧</b> ——
拧错了，模型会自信地给你一个错答案，而且从外面看不出来。这部分工作没法外包。</p></div>

<h2 id="reg">正则化：给它设个上限</h2>
<p><b>正则化</b>这个名字很吓人，意思特别朴素：<b>给「系数长得太大」加罚款。</b></p>
<p>为什么要罚？因为一个系数特别大，通常意味着模型在<b>死盯着某一个特征</b> ——
往往是它在迁就训练数据里某几个特殊的人。给它设个上限，逼它雨露均沾，反而更稳。</p>
<p>打个比方：给小孩零花钱设上限，不是小气，是防止他把钱全砸在一个玩具上。</p>
<p>罚款有两种罚法，差别很大：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>罚法</th><th>怎么罚</th><th>结果</th><th>什么时候用</th></tr>
<tr><td><b>L1 正则化</b></td><td>按系数的<b>绝对值</b>罚</td><td>不重要的系数会被<b>直接罚成 0</b>，等于顺手删掉这个特征</td><td>你怀疑一堆特征里大部分是凑数的，想要一个干净精简的模型</td></tr>
<tr><td><b>L2 正则化</b></td><td>按系数的<b>平方</b>罚</td><td>只把大系数往 0 拉一点，<b>不清零</b>，整体变小</td><td>你想保留全部特征，但别让任何一个说了算</td></tr>
</table></div>
<div class="note"><b>一句口诀：</b>归一化、标准化处理的是<b>喂进去的输入</b>；正则化管的是<b>模型自己的参数</b>。
两个不是一回事，别在该做正则化的地方做了标准化。</div>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>正则化就是<b>允许模型「答得没那么准」，但不许它「过于自信」</b>。
它放弃一部分训练分数，换来的是在新数据上不那么容易栽跟头 ——
<b>宁可差一点点，也不要把噪声焊进模型里。</b></p></div>

{_three([
    "<b>模型是成品，算法是工艺。</b>算法跑完，模型就填好了。",
    "找数字的三种办法：<b>一步算出来、慢慢挪过去、一路贪心切</b>。",
    "<b>loss 是尺、梯度下降是手</b>；<b>超参数是给人拧的</b>（轮次、步长、树多深），正则化是给系数设上限防背题。",
])}
"""


# ============================================================ B7 家族树
def p_b07(F):
    inner = f"""
<rect x="230" y="10" width="260" height="52" rx="8" fill="{INK}"/>
<text x="360" y="32" font-size="15" fill="#f5f1e6" text-anchor="middle">人工智能　AI</text>
<text x="360" y="51" font-size="11.5" fill="#cdc7b8" text-anchor="middle">让机器做原本只有人能做的判断</text>

<line x1="360" y1="62" x2="360" y2="76" stroke="{LINE}"/>
<line x1="190" y1="76" x2="530" y2="76" stroke="{LINE}"/>
<line x1="190" y1="76" x2="190" y2="90" stroke="{LINE}"/>
<line x1="530" y1="76" x2="530" y2="90" stroke="{LINE}"/>

<rect x="70" y="90" width="240" height="48" rx="8" fill="{JADE}"/>
<text x="190" y="111" font-size="14" fill="#fff" text-anchor="middle">机器学习　ML</text>
<text x="190" y="128" font-size="11" fill="#d8e6e0" text-anchor="middle">不写死规则，让机器从例子里总结</text>
<rect x="430" y="90" width="200" height="48" rx="8" fill="{GREY}"/>
<text x="530" y="111" font-size="14" fill="#fff" text-anchor="middle">其他：规则、搜索…</text>
<text x="530" y="128" font-size="11" fill="#efe9db" text-anchor="middle">不是本案例走的路</text>

<line x1="190" y1="138" x2="190" y2="150" stroke="{LINE}"/>
<line x1="100" y1="150" x2="364" y2="150" stroke="{LINE}"/>
<line x1="100" y1="150" x2="100" y2="164" stroke="{LINE}"/>
<line x1="232" y1="150" x2="232" y2="164" stroke="{LINE}"/>
<line x1="364" y1="150" x2="364" y2="164" stroke="{LINE}"/>

<rect x="40" y="164" width="120" height="36" rx="6" fill="{JADE}" opacity="0.14" stroke="{JADE}"/>
<text x="100" y="187" font-size="12.5" fill="{JADE}" text-anchor="middle">监督学习</text>
<rect x="172" y="164" width="120" height="36" rx="6" fill="{JADE}" opacity="0.14" stroke="{JADE}"/>
<text x="232" y="187" font-size="12.5" fill="{JADE}" text-anchor="middle">无监督学习</text>
<rect x="304" y="164" width="120" height="36" rx="6" fill="{JADE}" opacity="0.14" stroke="{JADE}"/>
<text x="364" y="187" font-size="12.5" fill="{JADE}" text-anchor="middle">强化学习</text>

<line x1="310" y1="114" x2="580" y2="114" stroke="{AMBER}" stroke-dasharray="4 3"/>
<line x1="580" y1="114" x2="580" y2="164" stroke="{AMBER}" stroke-dasharray="4 3"/>
<rect x="470" y="164" width="220" height="36" rx="6" fill="{AMBER}" opacity="0.14" stroke="{AMBER}"/>
<text x="580" y="187" font-size="12.5" fill="{AMBER}" text-anchor="middle">深度学习　DL</text>
<text x="580" y="212" font-size="11" fill="{GREY}" text-anchor="middle">擅长图像 / 语音 / 文字</text>
<text x="580" y="228" font-size="11" fill="{GREY}" text-anchor="middle">表格数据一般打不过树模型</text>

<line x1="100" y1="200" x2="100" y2="214" stroke="{RED}"/>
<rect x="40" y="214" width="120" height="42" rx="6" fill="{RED}" opacity="0.1" stroke="{RED}"/>
<text x="100" y="233" font-size="11.5" fill="{RED}" text-anchor="middle">本案例</text>
<text x="100" y="249" font-size="11.5" fill="{RED}" text-anchor="middle">全在这一支</text>

<text x="232" y="230" font-size="11" fill="{GREY}" text-anchor="middle">没有答案，</text>
<text x="232" y="246" font-size="11" fill="{GREY}" text-anchor="middle">只按像不像分组</text>
<text x="364" y="230" font-size="11" fill="{GREY}" text-anchor="middle">试错 + 奖惩</text>
<text x="364" y="246" font-size="11" fill="{GREY}" text-anchor="middle">下棋、机器人</text>

<text x="100" y="274" font-size="10.5" fill="{GREY}" text-anchor="middle">按「怎么学」分</text>
<text x="580" y="256" font-size="10.5" fill="{GREY}" text-anchor="middle">按「用什么结构」分（虚线）</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B7</span>
家族树：AI、机器学习、深度学习、强化学习</h1>
<p class="lead">这四个词天天一起出现，但<b>它们不是并列关系，是包含关系</b>。
一图看清，以后再也不会用错。</p>

{_toc([("tree", "一张关系图"), ("words", "每个词一句话"), ("types", "四大类型：按「有没有答案」分"),
       ("cmp", "传统机器学习 vs 深度学习"), ("map", "算法地图：从简单到复杂")])}

<h2 id="tree">一张关系图</h2>
{_svg(720, 286, inner, "AI 是最大的圈，机器学习在它里面；监督 / 无监督 / 强化是按「怎么学」分出来的三支，深度学习是按「用什么结构」分的另一把尺子（虚线）。我们这个案例在最左边那一支。")}

<h2 id="words">每个词一句话</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>词</th><th>一句话</th><th>你需要关心吗</th></tr>
<tr><td><b>人工智能 AI</b></td><td>最大的那个词：让机器做原本只有人能做的判断</td><td>了解即可</td></tr>
<tr><td><b>机器学习 ML</b></td><td>AI 的主力：不写死规则，让机器从例子里总结</td><td class="hl"><b>本案例全程在用</b></td></tr>
<tr><td><b>深度学习 DL</b></td><td>ML 里的一个分支，用很多层小计算器叠起来，擅长图像语音文字</td><td>表格数据一般不用它</td></tr>
<tr><td><b>强化学习 RL</b></td><td>ML 的另一个分支：不给答案，只给奖惩，让它在试错里摸索</td><td>定价场景用不上</td></tr>
<tr><td><b>监督学习</b></td><td>每个例子都带着标准答案</td><td class="hl"><b>本案例就是这一类</b></td></tr>
<tr><td><b>无监督学习</b></td><td>没有答案，只把长得像的归成堆</td><td>本案例没用</td></tr>
</table></div>
<div class="note"><b>一个实用判断：</b>如果你的数据是<b>一张表格</b>（一行一个人、一列一个属性），
深度学习通常打不过「树模型」那一家，而且更难解释。
如果你的数据是<b>图像、语音、大段文字</b>，那才轮到深度学习上场。
别因为「深度学习听着高级」就硬上 —— <b>选模型看数据长什么样，不看名字响不响。</b></div>

<h2 id="types">四大类型：按「有没有答案」分</h2>
<p>上面那张图里画了监督、无监督、强化三支，其实还有一支常被忽略 ——
<b>半监督学习</b>。四种分法的唯一标准是：<b>你手上有没有「标准答案」。</b></p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>类型</th><th>数据长什么样</th><th>它干嘛用</th><th>本案例</th></tr>
<tr><td><b>监督学习</b></td><td>每条都带答案（既给特征，也给真实赔付）</td><td>学「特征 → 答案」这条关系</td><td class="hl"><b>本案例全程</b></td></tr>
<tr><td><b>无监督学习</b></td><td>只有特征，没有答案</td><td>聚类（自动分组）、降维（把一堆特征压成少几根）、异常检测</td><td>没用，但风险分层可以借它</td></tr>
<tr><td><b>半监督学习</b></td><td>少量有答案 + 大量没答案</td><td>用廉价的无标注数据，把有标注那一小撮的用法放大</td><td>本案例的<b>审计样本</b>思路有点像它：只标了极少一批</td></tr>
<tr><td><b>强化学习</b></td><td>既没有现成答案，也没有标签；只有「做了之后的奖惩分」</td><td>在反复试错里学出一套最优动作策略</td><td>定价场景用不上</td></tr>
</table></div>
<div class="note"><b>半监督为什么重要：</b>真实业务里，标注是最贵的。
有答案的数据少得可怜，没答案的数据一大堆。
半监督就是把「少量标准答案 + 大量未标注」混起来用 ——
<b>我们这个案例其实就卡在这个坎上</b>：被拒保的人根本没有赔付记录，答案拿不到，
只能靠审计样本去估。这正是第 30 页那几条偏差数字的来源。</div>

<h2 id="cmp">传统机器学习 vs 深度学习</h2>
<p>又一个常被问错的问题：<b>深度学习是不是全面更强？</b>不是。差别在数据长什么样。</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>对比项</th><th>传统机器学习</th><th>深度学习</th></tr>
<tr><td>常见数据</td><td><b>表格、结构化的数字</b>（一行一个人、一列一个字段）</td><td>图像、语音、大段文字这类非结构化数据</td></tr>
<tr><td>特征怎么来</td><td>靠人做特征工程（算次数、做分组、编哑变量）</td><td>多层自动抽取，人管得少</td></tr>
<tr><td>要多少数据</td><td>几千条也能跑</td><td>通常要几万、几十万起步</td></tr>
<tr><td>算力成本</td><td>一台普通机器就够</td><td>显卡、集群、电费</td></tr>
<tr><td>可解释性</td><td><b>好</b>：GLM 的系数能直接讲成业务话</td><td>差：通常是个黑箱</td></tr>
<tr><td>常见选手</td><td>逻辑回归、决策树、<b>XGBoost / LightGBM</b></td><td>CNN、RNN、Transformer</td></tr>
</table></div>
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>在<b>保险定价、风控评分这种表格数据场景</b>里，逻辑回归和树模型那一家，
依然是主力选手 —— 不是因为它老，是因为<b>它既准、又能向监管和审计讲清楚为什么</b>。
要向监管解释每一分钱从哪来，这一条是硬门槛，不是加分项。</p></div>
<p><b>一句话：选模型看数据长什么样、成本多少、能不能解释，不看名字响不响。</b></p>

<h2 id="map">算法地图：从简单到复杂</h2>
<p>同样一张表格数据，可以上不同复杂度的模型。按顺序来：</p>
<div class="steps">
<div class="step"><h4>① 一条线（GLM / 线性回归）</h4>
<p>最朴素。好处是每个系数都能直接翻译成业务话，坏处是表达不了「拐弯」的规律。
<b>精算师最熟悉这一层</b> —— 你平时做的费率因子，本质上就是它。</p></div>
<div class="step"><h4>② 一串问题（决策树）</h4>
<p>能表达拐弯和交叉，画出来就是一棵树，业务一眼看懂。缺点是边界生硬、不够稳。</p></div>
<div class="step"><h4>③ 很多棵树加起来（GBDT / 随机森林）</h4>
<p>一棵树不稳，就让几十棵树接力补差。这是目前<b>表格数据的主力选手</b>，
各类比赛里长期霸榜。本案例的进阶版用的就是它。</p></div>
<div class="step"><h4>④ 多层神经网络（深度学习）</h4>
<p>表达能力最强，但需要大量数据，而且很难解释为什么。
<b>在保险定价这种要向监管解释的场景里，这是硬伤。</b></p></div>
</div>
<p>本案例的路线是 <b>① → ② → ③</b>：先让你在最熟悉的那一层站稳，再往上走。
这也是我建议你学习机器学习的顺序 —— <b>别从最炫的那层开始。</b></p>

{_three([
    "这四个词是<b>包含关系</b>：AI ⊃ 机器学习 ⊃ 深度学习；强化学习是另一支。",
    "表格数据（一行一个人）一般<b>用不到深度学习</b>，树模型那一家更强也更好解释。",
    "学习顺序建议 <b>一条线 → 一串问题 → 很多棵树</b>，别从最炫的那层开始。",
])}
"""


# ============================================================ B14 一趟下山路
def p_b14(F):
    def _gap(d):
        if d > 0.8:
            return "训练略高于测试，正常"
        if d > 0:
            return "两者几乎持平"
        return "<b>测试反超训练，泛化更好</b>"

    def lane(x, title, c, train, val, note):
        s = (f'<text x="{x+95}" y="48" font-size="12.5" fill="{c}" text-anchor="middle">{title}</text>'
             f'<line x1="{x}" y1="186" x2="{x+188}" y2="186" stroke="{LINE}"/>')
        for pts, col, dash in ((train, JADE, ""), (val, c, 'stroke-dasharray="5 3"')):
            s += (f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2" {dash}/>')
            first = pts.split()[0].split(",")
            s += f'<circle cx="{first[0]}" cy="{first[1]}" r="3" fill="{col}"/>'
        return s + f'<text x="{x+95}" y="204" font-size="10.5" fill="{GREY}" text-anchor="middle">{note}</text>'

    inner = f"""
<text x="26" y="20" font-size="12.5" fill="{GREY}">实线＝训练集误差，虚线＝验证集误差，横轴是一轮一轮往下滑</text>
{lane(14, "欠拟合", RED,
      "28,62 84,66 140,68 192,68", "28,78 84,80 140,82 192,82",
      "两条一起高 → 工具不对，不是练得不够")}
{lane(216, "正常拟合", JADE,
      "230,152 286,120 342,92 394,76", "230,158 286,134 342,106 394,90",
      "一起降，验证没掉队 → 学到真规律了")}
{lane(418, "过拟合", AMBER,
      "432,168 488,120 544,86 596,54", "432,170 488,142 544,122 596,146",
      "训练压到底，验证掉头往上 → 开始背题")}
<text x="26" y="76" font-size="10.5" fill="{GREY}">高</text>
<text x="26" y="180" font-size="10.5" fill="{GREY}">低</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B14</span>
模型是怎么被教会的一趟下山路</h1>
<p class="lead">把前面几页的知识拧成一句话：<b>训练 = 拿一把尺量误差 ＋ 顺着坡往下走 ＋ 走不动就停。</b>
这一页只讲这三件事，讲完你就能看懂每一个训练脚本在干嘛。</p>

{_toc([("loss", "第一件事：先有一把尺"), ("down", "第二件事：顺着坡走"),
       ("stop", "第三件事：什么时候停"), ("case", "本案例的三条实测曲线")])}

<h2 id="loss">第一件事：先有一把尺</h2>
<p><b>损失函数</b>（也叫 loss）就是一个数字，专门记「模型现在猜得有多离谱」。
它必须满足一件硬事：<b>模型越差，这个数越大。</b>不然机器没有方向可走。</p>
<div class="steps">
<div class="step"><h4>回归（预测一个数字）</h4>
<p>常用 <b>MSE</b>（误差平方的平均）、<b>RMSE</b>（同单位、更好讲）、<b>MAE</b>（对极端大误差不敏感）。
平方会把大的误差放大，所以 MSE 对「个别赔得极多的人」特别敏感。</p></div>
<div class="step"><h4>分类（判断属于哪一类）</h4>
<p>常用<b>交叉熵</b>（也叫 Log Loss）。它的脾气是：<b>你越自信地答错，罚得越狠。</b>
答错了还理直气壮，比含含糊糊地答错要付更大代价。</p></div>
<div class="step"><h4>次数类（出险几次）</h4>
<p>本案例用 <b>Deviance（偏差）</b>当这把尺，它是负对数似然的一种写法。</p></div>
</div>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>损失函数就是射箭的<b>环数表</b>：离靶心越远，扣得越多。
你的全部训练目标，只有一个 —— <b>把这张表上的分压到最低。</b></p></div>
<div class="note"><b>这里有个新手大坑：</b>「loss 变小了」<b>不等于</b>「模型变好了」。
loss 是在训练集上算的，它变小可能只是把训练题背熟了。
<b>真正要盯的是验证集上那把尺</b> —— 那条线不掉队，才叫真会。</div>

<h2 id="down">第二件事：顺着坡走</h2>
<p>光有尺子还不够，还得有「手」。<b>梯度下降</b>就是那只手，它做的动作永远三步、重复到停：</p>
<div class="steps">
<div class="step"><h4>① 看一眼现在的误差</h4>
<p>把当前所有参数代进去，算出 loss。</p></div>
<div class="step"><h4>② 问：往哪个方向挪，误差掉得最快？</h4>
<p>这个方向叫<b>梯度</b>。我们<b>反着走</b> —— 因为梯度指上山，我们要下山。</p></div>
<div class="step"><h4>③ 挪一小步</h4>
<p>挪多大？由<b>学习率</b>决定。然后回到 ①。</p></div>
</div>
<p>三种「拿多少数据来判断方向」的做法：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>做法</th><th>每次用多少数据</th><th>好处</th><th>麻烦</th><th>类比</th></tr>
<tr><td>全量梯度下降</td><td>全部数据一起算</td><td>方向最稳</td><td>数据一多就慢到不能忍</td><td>请全城的人一起估价</td></tr>
<tr><td>随机梯度下降</td><td>每次只看 1 条</td><td>极快</td><td>抖得厉害，一忽一忽</td><td>随便拉一个人问价</td></tr>
<tr><td><b>小批量（32/64/128）</b></td><td>每次一小撮</td><td>又快又稳，主流</td><td>要多设一个 batch size</td><td>问 30 个人，取个代表</td></tr>
</table></div>
<div class="note"><b>学习率的两种错法：</b>太大 → 一步跨过谷底，误差来回震荡甚至失控；
太小 → 慢慢爬，训一天还在山腰。<b>本案例 GBDT 取 0.08，意思是每棵新树只把误差补掉 8%，
剩下的留给后面几十棵慢慢补</b> —— 留余地，才不容易走岔。</div>

<h2 id="stop">第三件事：什么时候停</h2>
<p>三种停法，别用错：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>停法</th><th>触发条件</th><th>说明</th></tr>
<tr><td><b>收敛</b></td><td>改来改去，改进量小到可以无视</td><td>手自己停住了。本案例 GLM 的 IRLS 就是跑到这步</td></tr>
<tr><td><b>提前停止 Early Stopping</b></td><td>验证集误差连续好几轮不再变好</td><td><b>主动喊停</b>，并把那轮最好的参数保存下来。<b>它看的是验证集，不是测试集</b></td></tr>
<tr><td><b>设个上限</b></td><td>到轮数上限 / 到时间上限</td><td>兜底用的，不代表训好了</td></tr>
</table></div>
{_svg(628, 224, inner, "三种状态一眼分：两条线一起低是正常，验证线掉头往上就是背题了。")}
<p><b>三种状态的判断口诀：</b></p>
<div class="steps">
<div class="step"><h4>欠拟合：两条都高</h4>
<p>训练误差高、验证误差也高。不是练得不够，是<b>模型太简单或数据太脏</b> ——
换工具，别硬练。</p></div>
<div class="step"><h4>正常拟合：两条一起降，验证跟着降</h4>
<p>训得动，而且没记住噪声。这才是想要的。</p></div>
<div class="step"><h4>过拟合：训练很低，验证掉头往上</h4>
<p><b>越练越背。</b>该停了 —— 该加正则化、减复杂度、或者加数据。</p></div>
</div>
<p>还有第四种情况：<b>卡在坑里（局部最优）</b>。
脚下这个坑已经是最低了，但翻过前面那个山头还有一个更深的。
梯度下降本身走不出来，得靠换起点、加随机扰动、或者调学习率。
<b>精算定价场景通常不在乎这一点</b> —— 模型够用就行，也不必追那个「全局最优」。</p>

<h2 id="case">本案例的三条实测曲线</h2>
<p>这三种状态不是纸上的道理，本案例真的跑出了三条不同的曲线（指标是 AUC，越大越好）：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>方案</th><th>训练集 AUC</th><th>测试集 AUC</th><th>测试 − 训练</th><th>怎么读</th></tr>
{''.join(f'<tr><td>{c["name"]}</td><td class="num">{c["train"]:.3f}</td><td class="num">{c["test"]:.3f}</td><td class="num{" hl" if c["decay"]<0 else ""}">{c["decay"]:+.1f}</td><td>{_gap(c["decay"])}</td></tr>' for c in F["overfit"])}
</table></div>
<p>看懂这张表（最后两列是 training 与 test 的差，正 = 训练更高）：</p>
<ul>
<li><b>前两个方案：训练比测试高约 0.5 和 0.8 个百分点。</b>差距很小，几乎持平 ——
既不欠拟合，也没背题，属于「稳稳的普通」。</li>
<li><b>第三个方案：测试反而比训练高 1.6 个百分点。</b>反过来，
说明模型<b>没把训练集背下来</b>，学到的是能往外走的东西 —— 这才是这一个案例里最想要的那个模型。</li>
<li>注意第二方案（GBDT×单树）虽然用了更花哨的算法，<b>三个方案里它是最差的</b>。
所以别拿「训练分数」当目标，<b>拿测试集那根线当目标</b>。</li>
</ul>
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>新手看到「训练分数低」就慌，要调一通参数往上提。
<b>在榜单上多挣那 0.3 个点，往往是把模型往过拟合方向推了一步。</b>
真正该盯的，是<b>测试集那根线有没有跟着一起往下降</b> ——
它不动，你加再多棵树也是在给训练集做作文。</p></div>

{_three([
    "训练就三件事：<b>有尺子（loss）→ 顺着坡挪（梯度下降）→ 该停就停</b>，没有第四件。",
    "看训练集的 loss 会骗人。<b>验证集那根线掉头往上，就是过拟合的信号</b>。",
    "本案例三条曲线里最好的那条，<b>是测试集比训练集更高的那条</b> —— 别被「训练分低」吓住。",
])}
"""


# ============================================================ B8 怎么判断好不好
def p_b08(F):
    auc_inner = f"""
<text x="16" y="24" font-size="12.5" fill="{GREY}">按模型打分从「最看好」排到「最不看好」→</text>
<rect x="16" y="40" width="600" height="30" rx="4" fill="{JADE}" opacity="0.06"/>
<text x="316" y="60" font-size="12" fill="{GREY}" text-anchor="middle">左边 = 模型说风险最低的人　　右边 = 模型说风险最高的人</text>
<circle cx="46" cy="96" r="9" fill="{JADE}"/><text x="46" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="72" cy="96" r="9" fill="{JADE}"/><text x="72" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="98" cy="96" r="9" fill="{JADE}"/><text x="98" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="124" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="124" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="150" cy="96" r="9" fill="{JADE}"/><text x="150" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="176" cy="96" r="9" fill="{JADE}"/><text x="176" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="202" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="202" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="228" cy="96" r="9" fill="{JADE}"/><text x="228" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="300" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="300" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="340" cy="96" r="9" fill="{JADE}"/><text x="340" y="100" font-size="10" fill="#fff" text-anchor="middle">好</text>
<circle cx="400" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="400" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="440" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="440" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="480" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="480" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="520" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="520" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="560" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="560" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<circle cx="600" cy="96" r="9" fill="{RED}" opacity="0.5"/><text x="600" y="100" font-size="10" fill="#fff" text-anchor="middle">坏</text>
<text x="316" y="132" font-size="12" fill="{JADE}" text-anchor="middle">绿色（好人）扎堆在左边 → 排得好 → AUC 高</text>
<text x="316" y="156" font-size="11.5" fill="{GREY}" text-anchor="middle">如果绿红完全混在一起乱排，AUC 就是 0.5，等于瞎猜</text>
"""
    cm_inner = f"""
<text x="322" y="22" font-size="12.5" fill="{INK}" text-anchor="middle">把所有人按「模型圈没圈」和「真实好不好」排成 2×2</text>
<text x="360" y="44" font-size="11" fill="{GREY}" text-anchor="middle">真实是好司机</text>
<text x="540" y="44" font-size="11" fill="{GREY}" text-anchor="middle">真实是高风险</text>
<rect x="288" y="52" width="150" height="74" rx="6" fill="{JADE}" opacity="0.12" stroke="{JADE}"/>
<rect x="450" y="52" width="150" height="74" rx="6" fill="{RED}" opacity="0.10" stroke="{RED}"/>
<rect x="288" y="136" width="150" height="74" rx="6" fill="{GREY}" opacity="0.12" stroke="{GREY}"/>
<rect x="450" y="136" width="150" height="74" rx="6" fill="{AMBER}" opacity="0.14" stroke="{AMBER}"/>
<text x="363" y="86" font-size="12" fill="{JADE}" text-anchor="middle">圈出且真好</text>
<text x="363" y="104" font-size="11" fill="{INK}" text-anchor="middle">→ 精确率分子</text>
<text x="525" y="86" font-size="12" fill="{RED}" text-anchor="middle">圈出但误伤</text>
<text x="525" y="104" font-size="11" fill="{INK}" text-anchor="middle">→ 纯度掉这里</text>
<text x="363" y="170" font-size="11.5" fill="{INK}" text-anchor="middle">没圈，漏掉的好人</text>
<text x="363" y="188" font-size="11" fill="{GREY}" text-anchor="middle">→ 召回缺口</text>
<text x="525" y="170" font-size="11.5" fill="{AMBER}" text-anchor="middle">没圈，本就不该圈</text>
<text x="525" y="188" font-size="11" fill="{GREY}" text-anchor="middle">→ 放对的（多数）</text>
<text x="200" y="90" font-size="12" fill="{INK}" text-anchor="middle">模型</text>
<text x="200" y="108" font-size="12" fill="{INK}" text-anchor="middle">圈出</text>
<text x="200" y="174" font-size="12" fill="{INK}" text-anchor="middle">模型</text>
<text x="200" y="192" font-size="12" fill="{INK}" text-anchor="middle">没圈</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B8</span>
怎么判断一个模型好不好</h1>
<p class="lead">这一页最重要的一句话先说：<b>「模型好不好」不是一个问题，是三个问题。</b>
排序准不准、数字准不准、圈出来的人划不划算 —— 三把不同的尺，别混着用。</p>

{_toc([("ruler1", "第一把尺：排序准不准（AUC）"), ("ruler2", "第二把尺：数字准不准（校准）"),
       ("ruler3", "第三把尺：圈出来划不划算"), ("metric", "一张表看清常用指标"),
       ("case", "本案例的四组数字")])}

<h2 id="ruler1">第一把尺：排序准不准（AUC）</h2>
{_why("AUC 到底是个什么数？0.885 具体意味着什么？",
      "AUC <b>不是准确率</b>。它的定义是一个概率：随机抽一个好司机、一个坏司机，"
      "模型把好司机排在前面的概率有多大。0.5 就是瞎猜，1.0 是完美。",
      "AUC = P( score(好司机) &gt; score(坏司机) )",
      [("score", "模型给每个人打的分（本案例是预测纯保费，越低越好）"),
       ("P(…)", "随机抽一对好人坏人，排对的概率")],
      f'本案例内插域 AUC {F["interp"]["A"]["auc"]}，意思是「随便抽一对，'
      f'{F["interp"]["A"]["auc"]*100:.1f}% 的情况下排对了」。'
      f'<b>但它完全不告诉你分数是不是虚高</b>——那是第二把尺的事：'
      f'本案例校准比 {F["calib_A"]}，说明预测整体虚高三成。')}


<p>我们的目的不是算出「这个人精确值多少钱」，而是<b>把好人排到前面去</b>。
所以第一把尺量的是排序能力，叫 <b>AUC</b>。</p>
{_svg(632, 164, auc_inner, "绿色是真正的好司机，红色是真正的高风险。绿色越集中在左边，AUC 越高。")}
<p>严格的说法是：<b>随机抽一个好人和一个坏人，模型能把好人排得更靠前的概率。</b>
这个概率就是 AUC。</p>
{_cmp_table([
    ["<b>0.5</b>", "等于瞎猜", "闭着眼挑"],
    ["<b>0.7 左右</b>", "有点用", "能用，但别指望太高"],
    ["<b>0.85 以上</b>", "相当不错", "本案例在承保人群上达到了这个水平"],
    ["<b>1.0</b>", "完美", "出现这个数，先怀疑是不是数据漏了"],
], ["AUC 值", "意味着什么", "打个比方"])}
<div class="note red"><b>看到 1.0 别高兴，先怀疑。</b>AUC 满分通常意味着「答案泄露」——
某个特征其实直接等于答案（比如把「实际赔付金额」当特征喂进去了）。
这是新手最常犯、也最难自查的错误之一。</div>

<h2 id="ruler2">第二把尺：数字准不准（校准）</h2>
<p>排序准，<b>不代表数字准</b>。这一点非常反直觉，请务必分开看：</p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>一支体温计能正确排出「谁烧得更厉害」，这是<b>排序准</b>；
它显示 38.5 度、真实就是 38.5 度，这是<b>数字准</b>。
一支体温计可以排序很准但整体偏高 2 度 —— 排序照样有用，但那个度数不能拿去开药。</p></div>
<p>衡量数字准不准，就比两个数：<b>模型的平均预测值</b> vs <b>真实的平均值</b>。
本案例里这个比值是 <code>{F['calib_A']}</code> —— 也就是说模型整体<b>虚高了约三成</b>。
这件事在第 31 页会细讲，并直接决定了我们的落地方案：<b>只用它排序，不用它定价。</b></p>

<h2 id="ruler3">第三把尺：圈出来划不划算</h2>
<p>业务不关心 AUC，业务关心「我圈了 500 个人去复核，里面有多少真的对」。
所以还要看两个更接地气的数：</p>
{_cmp_table([
    ["<b>召回率</b>", "真正该救的人里，你救到了百分之多少", "漏掉的代价：少赚钱"],
    ["<b>精确率（纯度）</b>", "你圈出来的这批里，真正对的占多少", "圈错的代价：赔钱 + 人力白花"],
], ["指标", "大白话", "对应什么代价"])}
<p>这两个数是<b>互相拉扯</b>的：圈得越松，召回率高但纯度低；圈得越紧，纯度高但漏掉的多。
<b>没有「又全又准」的好事</b>，只有按成本算出来的平衡点。
第 32 页那张倒 U 曲线，就是在找这个平衡点。</p>
{cm_inner}
<p>一张图记住：<b>纯度</b>看「圈出来这一格」里绿色占几成（误伤越少越纯）；
<b>召回率</b>看「该救的好人格」里被你圈到了几成（漏掉的越多，召回越低）。
这两个格子此消彼长，所以才有「圈多圈少」的取舍。</p>

<h2 id="metric">一张表看清常用指标</h2>
<p>不同任务看的尺不一样，<b>选错指标，模型会顺着你的指标往坑里跑</b>——
你考核准确率，它就拼命让你猜的「是」变多；你考核召回，它就拼命多圈人。</p>
<h3 class="sub">分类模型（预测「是不是」）常看什么</h3>
{_cmp_table([
    ["<b>准确率 Accuracy</b>", "猜对的占全部的比例", "类别比较均衡时才看；<b>不均衡时它会骗你</b>"],
    ["<b>精确率 Precision</b>", "你圈出来这批人里，真的对的有多少", "圈错代价大时看（赔钱、人工白花）"],
    ["<b>召回率 Recall</b>", "该救的人里，你救到了多少", "漏掉代价大时看（少赚钱、真出事）"],
    ["<b>F1</b>", "精确率和召回率的折中分", "只想看一个简单总分时看"],
    ["<b>AUC</b>", "随机抽好坏各一人，能把好人排前面的概率", "只关心排序、不关心具体数值时看"],
    ["<b>混淆矩阵</b>", "圈对 / 圈错 / 漏掉 / 放对，四格摊开", "要跟业务解释「错在哪一格」时看"],
], ["指标", "大白话", "什么时候该看它"])}
<h3 class="sub">回归模型（预测「多少」）常看什么</h3>
{_cmp_table([
    ["<b>MAE</b> 平均绝对误差", "每次猜错平均差多少", "想看「典型错多少」时看，对大误差不太敏感"],
    ["<b>RMSE</b> 均方根误差", "错得更狠的那些被放大了", "<b>怕大偏差时看</b>（极端个案代价更高）"],
    ["<b>R²</b> 决定系数", "模型解释掉了多少波动", "想跟人说「模型解释了多少」时看"],
    ["<b>真实值 vs 预测值</b>", "点围着斜线散开成什么样", "判断「系统性偏高还是偏低」时看"],
], ["指标", "大白话", "什么时候该看它"])}
<div class="note"><b>别只看一个指标，三个原因：</b>
① 训练集高分不代表测试集也好（<a href="b05.html">B5</a>）；
② 指标要<b>结合业务场景</b>一起看 —— 漏掉一个人的代价，和圈错一个人的代价，根本不是一个量级；
③ 模型既要<b>能解释</b>，也要有<b>泛化能力</b>，光看一个数顾不住这两头。</div>
<div class="note jade"><b>本案例用的是哪一套？</b>
我们<b>没用准确率</b>（要预测的是纯保费这个数字，不是类别），
主看 <b>AUC</b>（排序准不准）＋ <b>圈选纯度 / 召回率</b>（圈出来划不划算）＋ <b>校准比</b>（数字准不准）。
三把尺一起用，才得出「只能排序、不能定价」这个结论。</div>

<h2 id="case">本案例的四组数字</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>尺</th><th>承保人群（考试区内）</th><th>拒保人群（真正要用它的地方）</th></tr>
<tr><td>排序（AUC）</td><td class="num">{F['interp']['A']['auc']}</td><td class="num">{F['extrap']['A']['auc_all']}</td></tr>
<tr><td>圈最便宜 20% 里好司机占比</td><td class="num">{F['interp']['A']['purity']}%</td><td class="num">{F['extrap']['A']['purity20_all']}%</td></tr>
<tr><td>校准（预测/真实）</td><td class="num">接近 1.0</td><td class="num hl">{F['calib_A']}</td></tr>
</table></div>
<div class="tbl-cap">纯度从 {F['interp']['A']['purity']}% 掉到 {F['extrap']['A']['purity20_all']}%，
落差 {abs(F['purity_drop']):.1f} 个百分点 —— 这就是第 31 页要讲的核心事实。</div>
<div class="note"><b>为什么两列要分开看？</b>第一列是「它在熟悉的题上考了多少分」，
第二列才是「它在真正要用的地方考了多少分」。
<b>只报第一列的模型报告，是最常见的一种误导。</b>这一点在第 33 页会被拆到底。</div>

{_three([
    "「模型好不好」是<b>三个问题</b>：排序准不准、数字准不准、圈出来划不划算。",
    "<b>排序准 ≠ 数字准。</b>本案例模型整体虚高三成，所以只能用来排序、不能用来定价。",
    "召回率和纯度<b>互相拉扯</b>，没有又全又准，只有按成本算出来的平衡点。",
])}
"""


# ============================================================ B9 学习地图 · 门路推荐
def p_b09(F):
    rel_svg = f"""
<rect x="16" y="18" width="612" height="118" rx="14" fill="{INK}"/>
<text x="322" y="42" font-size="15" fill="#f5f1e6" text-anchor="middle">人工智能 AI（最大的那个词）</text>
<rect x="64" y="54" width="516" height="62" rx="10" fill="{JADE}"/>
<text x="322" y="78" font-size="14" fill="#fff" text-anchor="middle">机器学习 ML　不写死规则，让机器从例子里总结</text>
<text x="322" y="101" font-size="12" fill="#d8e6e0" text-anchor="middle">它下面按「怎么学」分出：监督 / 无监督 / 强化</text>
<rect x="420" y="146" width="208" height="34" rx="8" fill="{AMBER}" opacity="0.18" stroke="{AMBER}"/>
<text x="524" y="168" font-size="12.5" fill="{AMBER}" text-anchor="middle">深度学习 DL（按「用什么结构」分）</text>
<text x="524" y="194" font-size="11" fill="{GREY}" text-anchor="middle">另一把尺子，虚线那一支——擅长图像/语音/文字</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B9</span>
学习地图：一份不踩坑的门路推荐</h1>
<p class="lead">市面上的机器学习材料良莠不齐，新手最容易犯的错是<b>一上来就啃深度学习、被公式劝退</b>，
或者<b>收藏了 100 篇却一篇没读完</b>。这一页给你一条验证过的、由浅入深的路线，和一份精选的可点资源。</p>

{_toc([("rel", "先认清四个词的关系"), ("mat", "材料为什么挑花眼"), ("list", "精选资源（都可点）"), ("path", "零基础保险人怎么走")])}

<h2 id="rel">先认清四个词的关系</h2>
{_svg(644, 210, rel_svg, "AI 是最大的圈，机器学习在它里面；监督/无监督/强化是按「怎么学」分出的三支，深度学习是按「用什么结构」分的另一把尺子。完整关系图见基础篇 B7。")}
<p>记住一条就够用：<b>AI ⊃ 机器学习 ⊃ 深度学习</b>。你每天接触的表格数据（一行一个人），
通常<b>用不到深度学习</b>——树模型那一家又强又好解释。别因为深度学习名字响，就硬上最炫的那层。</p>

<h2 id="mat">材料为什么让你挑花眼</h2>
<div class="note"><b>三个常见坑：</b>
① 标题党「三天学会深度学习」——真学会要的是先把基础打牢，不是背 API；
② 一上来就推 PyTorch/TensorFlow——工具是最后才该关心的，先懂「模型在干什么」；
③ 只讲数学不讲直觉——看不懂不是你的问题，是它没把比喻给你。<br><br>
<b>本页的标准：</b>只列「免费或权威、由浅入深、能动手」的资源，并按用途分类，你按自己的阶段挑一类即可。</div>

<h2 id="list">精选资源（全部验证可点）</h2>
<h3 class="sub">① 视频公开课 · 建立直觉</h3>
<div class="tbl-wrap"><table class="tbl">
<tr><th>资源</th><th>适合谁</th><th>一句话点评</th></tr>
<tr><td><a href="https://www.coursera.org/learn/machine-learning-course" target="_blank" rel="noopener">吴恩达 · Machine Learning（Coursera）</a></td>
  <td>完全零基础</td><td class="good">入门首选。全球超 480 万人学，4.9 分；用 NumPy/scikit-learn 边做边学。</td></tr>
<tr><td><a href="https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php" target="_blank" rel="noopener">李宏毅 · 机器学习（台大，中文）</a></td>
  <td>想听中文、讲得透</td><td>幽默、覆盖全，从回归一路讲到生成式；配套作业与代码。</td></tr>
<tr><td><a href="https://www.3blue1brown.com" target="_blank" rel="noopener">3Blue1Brown · 神经网络系列</a></td>
  <td>想看懂「为什么」</td><td>视觉化讲透直觉，YouTube / B 站可搜；不看也能懂，看了忘不掉。</td></tr>
</table></div>

<h3 class="sub">② 交互式书 / 官方文档 · 系统学</h3>
<div class="tbl-wrap"><table class="tbl">
<tr><th>资源</th><th>适合谁</th><th>一句话点评</th></tr>
<tr><td><a href="https://d2l.ai" target="_blank" rel="noopener">动手学深度学习 D2L</a></td>
  <td>想跑代码、啃原理</td><td class="good">每节都是可运行 Jupyter，支持 PyTorch/NumPy/JAX/TF；500 所大学采用。</td></tr>
<tr><td><a href="https://scikit-learn.org/stable/" target="_blank" rel="noopener">scikit-learn 官方文档</a></td>
  <td>做表格数据实战</td><td>本案例这类「一行一个人」的任务，工具箱就在这里；例子极全，随查随用。</td></tr>
<tr><td><a href="https://www.deeplearning.ai" target="_blank" rel="noopener">DeepLearning.AI</a></td>
  <td>想跟 Andrew Ng 体系化</td><td>大量免费短课与专项，从 AI For Everyone 到 ML Specialization。</td></tr>
</table></div>

<h3 class="sub">③ 动手练 · 把知识焊牢</h3>
<div class="tbl-wrap"><table class="tbl">
<tr><th>资源</th><th>适合谁</th><th>一句话点评</th></tr>
<tr><td><a href="https://www.kaggle.com/learn" target="_blank" rel="noopener">Kaggle Learn</a></td>
  <td>学完想立刻上手</td><td class="good">免费短课 + 真实竞赛；Intro to ML / Intermediate ML / 模型可解释性都值得做。</td></tr>
</table></div>

<h3 class="sub">④ 书 · 想打深理论底子</h3>
<div class="tbl-wrap"><table class="tbl">
<tr><th>书</th><th>适合谁</th><th>一句话点评</th></tr>
<tr><td>周志华《机器学习》（西瓜书）</td><td>中文经典教材</td><td>覆盖全、讲得稳，适合当案头参考书。</td></tr>
<tr><td>李航《统计学习方法》</td><td>精算/统计背景</td><td class="good">公式推导严谨，和精算的语言最近，打基础首选。</td></tr>
<tr><td>邱锡鹏《神经网络与深度学习》</td><td>想系统学 DL</td><td>中文、有免费 PDF，从基础到前沿。</td></tr>
</table></div>
<div class="note jade"><b>一个实用提醒：</b>书买来是查的，不是从头读到尾的。先跟着视频和 Kaggle 跑通一个小模型，
遇到不懂的概念再回去翻书——这样书才用得上，也不会半途而废。</div>

<h2 id="path">零基础保险人，怎么走最顺</h2>
<div class="steps">
  <div class="step"><h4>第 1 步 · 先建立直觉（1–2 天）</h4>
    <p>把本库基础篇 <a href="b01.html">B1</a>–<a href="b08.html">B8</a> 读一遍，
    再补 <a href="https://www.3blue1brown.com" target="_blank" rel="noopener">3Blue1Brown 神经网络系列</a>。
    目标是「知道模型在干什么」，不急着写代码。</p></div>
  <div class="step"><h4>第 2 步 · 系统入门（2–3 周）</h4>
    <p><a href="https://www.coursera.org/learn/machine-learning-course" target="_blank" rel="noopener">吴恩达 Coursera</a> 前两周
    ＋ <a href="https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php" target="_blank" rel="noopener">李宏毅</a> 前几讲。
    把「训练/测试集」「过拟合」「线性回归」这几个词焊死。</p></div>
  <div class="step"><h4>第 3 步 · 上手表格数据（边做边学）</h4>
    <p><a href="https://scikit-learn.org/stable/" target="_blank" rel="noopener">scikit-learn 文档</a>
    ＋ <a href="https://www.kaggle.com/learn" target="_blank" rel="noopener">Kaggle Learn 的 Intro to ML</a>。
    拿一份你熟悉的表格（比如历史承保记录）跑一个逻辑回归，亲手看 AUC。</p></div>
  <div class="step"><h4>第 4 步 · 想深挖理论再看书</h4>
    <p><a href="https://d2l.ai" target="_blank" rel="noopener">D2L</a> ＋ 李航《统计学习方法》。
    别跳步——前面三步没走，书会劝退你。</p></div>
  <div class="step"><h4>第 5 步 · 千万别一上来啃深度学习</h4>
    <p>表格数据用树模型（GLM / 决策树 / GBDT）就够了；深度学习留给图像、语音、大段文字。
    选模型看数据长什么样，不看名字响不响——<a href="b07.html">B7</a> 讲得更透。</p></div>
</div>

{_three([
    "四个词是<b>包含关系</b>：AI ⊃ 机器学习 ⊃ 深度学习；别一上来就啃最炫的那层。",
    "路线就一条：<b>先直觉 → 再系统入门 → 上手表格数据 → 最后才啃理论书</b>。",
    "书是查的，不是通读的；<b>先跑通一个小模型，再回去翻书</b>，才不会半途而废。",
])}
"""


# ============================================================ B10 端到端完整流程
def p_b10(F):
    ring = f"""
<rect x="246" y="30" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="322" y="60" font-size="12.5" fill="{INK}" text-anchor="middle">① 明确业务问题</text>
<rect x="398" y="103" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="474" y="133" font-size="12.5" fill="{INK}" text-anchor="middle">② 收集与清洗数据</text>
<rect x="436" y="268" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="512" y="298" font-size="12.5" fill="{INK}" text-anchor="middle">③ 探索性分析 EDA</text>
<rect x="331" y="400" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="407" y="430" font-size="12.5" fill="{INK}" text-anchor="middle">④ 特征工程</text>
<rect x="161" y="400" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="237" y="430" font-size="12.5" fill="{INK}" text-anchor="middle">⑤ 划分数据集</text>
<rect x="56" y="268" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="132" y="298" font-size="12.5" fill="{INK}" text-anchor="middle">⑥ 训练与调参</text>
<rect x="94" y="103" width="152" height="50" rx="9" fill="#fbf8ef" stroke="{LINE}"/>
<text x="170" y="133" font-size="12.5" fill="{INK}" text-anchor="middle">⑦ 评估 · 部署 · 应用</text>
<circle cx="322" cy="250" r="90" fill="none" stroke="{LINE}" stroke-dasharray="5 5"/>
<text x="322" y="238" font-size="12" fill="{GREY}" text-anchor="middle">建模只是其中一环</text>
<text x="322" y="262" font-size="10.5" fill="{GREY}" text-anchor="middle">数据不行就退回第 ② 步</text>
<path d="M 398 62 L 420 100" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(420,100) rotate(60)" fill="{JADE}"/>
<path d="M 470 155 L 498 262" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(498,262) rotate(75)" fill="{JADE}"/>
<path d="M 470 320 L 478 396" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(478,396) rotate(73)" fill="{JADE}"/>
<path d="M 400 452 L 300 396" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(300,396) rotate(209)" fill="{JADE}"/>
<path d="M 161 425 L 120 330" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(120,330) rotate(247)" fill="{JADE}"/>
<path d="M 130 266 L 140 158" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(140,158) rotate(275)" fill="{JADE}"/>
<path d="M 200 100 L 250 84" stroke="{JADE}" stroke-width="1.6"/>
<polygon points="0,-5 9,0 0,5" transform="translate(250,84) rotate(342)" fill="{JADE}"/>
"""
    flow = f"""
<tr><td><b>① 明确业务问题</b></td>
  <td>被拒的 {F['n_rej']:,} 人里，有没有一批人真实风险<b>低于</b>已承保客户？值不值得找？</td>
  <td>这一步<b>先别写代码</b>，先写清问题定义卡；
      口径最终落在 {_cl('train_evaluate', 'def step2_define_good', label='step2_define_good')}</td>
  <td>一张问题定义卡：目标 / 口径 / 成功标准</td>
  <td>现行规则拒掉 {F['n_wrongly_killed']:,} 人，占拒保件 {F['pct_killed_of_rej']}%</td></tr>
<tr><td><b>② 收集与清洗数据</b></td>
  <td>手上有多少数据？哪些缺失、哪些口径不一致？<b>标签从哪来？</b></td>
  <td>{_cl('gen_data', 'def make_features', label='gen_data.py')} ·
      {_cl('gen_data', 'def simulate_claims', label='simulate_claims')} ·
      {_cl('_facts', label='_facts.py')}</td>
  <td><code>out/facts.json</code>——全站唯一数字源</td>
  <td>{F['n_total']:,} 份申请：{F['n_acc']:,} 已承保、{F['n_rej']:,} 拒保</td></tr>
<tr><td><b>③ 探索性分析 EDA</b></td>
  <td>数据本身在说什么？哪些车型 / 渠道几乎从不承保？</td>
  <td>{_cl('fig_01_look', 'def fig1_funnel', label='fig1 漏斗')} ·
      {_cl('fig_01_look', 'def fig2_channel', label='fig2 渠道')} ·
      {_cl('fig_02_model', label='fig_02_model.py')}</td>
  <td>业务侧关键图 + 模型侧九张图</td>
  <td>营运车承保率只有 <b>9.8%</b>；线上渠道错杀率是代理渠道的 <b>{F['kill_ratio_online_vs_agent']} 倍</b></td></tr>
<tr><td><b>④ 特征工程</b></td>
  <td>凭什么去预测？「渠道」这类<b>可能带偏见</b>的特征该不该用？</td>
  <td>{_cl('train_evaluate', 'def build_design', label='build_design')} ·
      {_cl('train_evaluate', 'def step2_define_good', label='定义好司机')}</td>
  <td>好司机标签 = 承保人群真实纯保费中位数</td>
  <td>好司机线定在 <b>{F['good_threshold']:,.0f} 元</b></td></tr>
<tr><td><b>⑤ 划分数据集</b></td>
  <td>哪些人用来练、哪些用来考？考试题能不能提前看过？</td>
  <td>{_cl('train_evaluate', 'def step3_dataset', label='step3_dataset')}
      （TEST_SIZE=0.25）</td>
  <td>{F['n_train']:,} 训练 / {F['n_test']:,} 测试</td>
  <td>两拨人<b>都只能来自 {F['n_acc']:,} 个已承保的人</b></td></tr>
<tr><td><b>⑥ 训练与调参</b></td>
  <td>一条直线够不够？要不要树？要不要集成？旋钮怎么拧？</td>
  <td>      {_cl('models', 'def fit(self, X, y, w=None):', label='Poisson.fit', nth=0)} ·
      {_cl('models', 'def _best_split', label='树找切点')} ·
      {_cl('models', 'def fit(self, X, y, w=None):', label='GBDT.fit', nth=3)} ·
      {_cl('train_evaluate', 'def step45_models', label='step45_models')} ·
      {_cl('_tune', 'def main', label='_tune.py')}</td>
  <td>四个模型（常数→GLM→单树→GBDT）＋ 一组规则系数</td>
  <td>直接建纯保费模型<b>撞墙</b>：deviance 是常数基线的 {F['dev_wall'][1]['pct']}%</td></tr>
<tr><td><b>⑦ 评估 · 部署 · 应用</b></td>
  <td>排序准不准？数字准不准？圈出来到底划不划算？</td>
  <td>{_cl('steps_678', 'def step6_rejected', label='step6 打分')} ·
      {_cl('steps_678', 'def step7_business', label='step7 业务账')} ·
      {_cl('steps_678', 'def step8_bias', label='step8 偏差')} ·
      {_cl('_build', 'def build', label='_build.py')}</td>
  <td>圈选名单 ＋ 业务增益 ＋ 落地 SOP</td>
  <td>内插 AUC <b>{F['interp']['A']['auc']}</b>／纯度 <b>{F['interp']['A']['purity']}%</b>；
      外推 AUC <b>{F['auc_A']}</b>／纯度 <b>{F['purity20_A']}%</b>；
      圈 {F['thr_peak_n']:,} 件增益 <b>{F['thr_peak_gain']:,.0f} 元</b></td></tr>
"""
    cmap = f"""
<tr><td>{_cl('gen_data', 'def make_features', label='gen_data.py')}</td><td>造 {F['n_total']:,} 份申请，<b>内置</b>「被拒保的人没有出险记录」这一机制</td><td><code>python gen_data.py</code></td></tr>
<tr><td>{_cl('_facts', label='_facts.py')}</td><td>抽出全站唯一数字源 <code>out/facts.json</code>，页面禁止硬编码</td><td><code>python _facts.py</code></td></tr>
<tr><td>{_cl('models', 'class PoissonRegressor', label='models.py')}</td><td>手写 4 个模型（Poisson 回归／逻辑回归／CART 树／GBDT）＋ 3 个评估工具</td><td>被主流程调用</td></tr>
<tr><td>{_cl('train_evaluate', 'def main', label='train_evaluate.py')}</td><td>主流水线 step1–step5：读数据→定义好司机→切分→四模型→评估</td><td><code>python train_evaluate.py</code></td></tr>
<tr><td>{_cl('steps_678', 'def step6_rejected', label='steps_678.py')}</td><td>step6–step8：给拒保人打分、算业务账、四种偏差修法对比</td><td>被主流程调用</td></tr>
<tr><td>{_cl('_tune', 'def main', label='_tune.py')}</td><td>扫参数，反推一套「梯度成立」的核保规则系数</td><td><code>python _tune.py</code></td></tr>
<tr><td>{_cl('fig_01_look', 'def fig1_funnel', label='fig_01_look.py')} /
    {_cl('fig_02_model', label='fig_02_model.py')}</td><td>业务侧关键图 / 模型侧九张图，全部由真实数据算出</td><td><code>python fig_01_look.py</code></td></tr>
<tr><td>{_cl('test_models', label='test_models.py')}</td><td>手写模型的正确性自检（解析解 vs 数值解互印）</td><td><code>python test_models.py</code></td></tr>
<tr><td>{_cl('_check', label='_check.py')} / {_cl('_build', 'def build', label='_build.py')}</td><td>站点自检（七类）／ 生成全部页面</td><td><code>python _check.py</code> · <code>python _build.py</code></td></tr>
"""
    return f"""
<h1><span class="thin">基础篇 · B10</span>
端到端：从问题定义一路做到落地</h1>
<p class="lead">前面九页教你「每个概念是什么」。这一页把它们<b>串成一条能跑通的路</b>：
从「业务上到底想解决什么」出发，到「模型上线、换成钱」为止，七个步骤每一步都对应到
<code>ai-kb/code</code> 里的真实文件。<b>你照着这条线走一遍，就是一个完整的机器学习实践。</b></p>

{_svg(644, 470, ring, "七个步骤围成一个环，不是一条线——数据不行就退回第 ② 步重做，这是常态而不是失败。")}

{_step_frame(
  "把「业务上想解决什么」翻译成「机器能算什么」，再一步步走到可执行的结论。",
  "一张问题定义卡、一份干净的标签、一个训好的模型、一组合乎业务账的圈选名单。",
  "先看上面的环记住七个步骤名；再对照「每一步的代码在哪」这张表往下读；最后看「一键复现」把整条流水线跑通。")}

<h2 id="flow">七个步骤，每一步在干什么、代码在哪</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th style="width:13%">步骤</th><th style="width:29%">业务问题（要回答什么）</th>
    <th style="width:21%">对应代码</th><th style="width:16%">产出物</th><th style="width:21%">本案例真实数字</th></tr>
{flow}</table></div>

<h2 id="phase">这一步对应本库的哪一页</h2>
<p>这条七步线，正好把后面 13 个场景页串起来——<b>你看的不是 13 个孤立的坑，是一条流水线上的 13 个关卡</b>：</p>
{_cmp_table([
    ["<b>第 1–4 步</b>：接住问题", "<a href=\"ch01.html\">ch01</a> 从 GLM 出发 · <a href=\"ch02.html\">ch02</a> −1 不是 0 · <a href=\"ch03.html\">ch03</a> 频率×损失", "把业务话翻译成机器话"],
    ["<b>第 5–6 步</b>：让机器学", "<a href=\"ch04.html\">ch04</a> GLM 迭代 · <a href=\"ch05.html\">ch05</a> 决策树 · <a href=\"ch06.html\">ch06</a> GBDT", "把 8,400 条训练样本吃进去"],
    ["<b>第 7 步（前半）</b>：看它学没学会", "<a href=\"ch07.html\">ch07</a> 选择偏差 · <a href=\"ch08.html\">ch08</a> IPW/双重稳健 · <a href=\"ch09.html\">ch09</a> 外推风险", "评估，也是最容易翻车的地方"],
    ["<b>第 7 步（后半）</b>：换成钱", "<a href=\"ch10.html\">ch10</a> 业务账与圈选 · <a href=\"ch11.html\">ch11</a> 陷阱 · <a href=\"ch12.html\">ch12</a> 端到端复盘", "输出落地方案，不是输出一个分数"],
], ["流水线阶段", "本库的对应页", "这一阶段的核心"])}
<div class="note"><b>为什么要按这个顺序排？</b>
很多项目栽在顺序上：先把模型调得花团锦簇，才发现<b>标签定义本身就是错的</b>（ch02），
或者<b>训练数据和用模型的那拨人根本不是一回事</b>（ch09）。
顺序的意义在于：<b>把「数据对不对」的验证，放在「模型好不好」的调校之前。</b></div>

<h2 id="cmap">代码地图：每个文件负责哪一环</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th style="width:24%">文件</th><th style="width:54%">干什么</th><th style="width:22%">怎么跑</th></tr>
{cmap}</table></div>

<h2 id="repro">一键复现：把整条流水线跑一遍</h2>
<p>下面这些命令在本项目根目录依次执行即可。<b>所有数字都会重新算一遍</b>，
和站点上写的完全一致——因为站点上的每一个数字，都是从 <code>out/facts.json</code> 注入的。</p>
<div class="copybox"><button class="copybtn" type="button" data-copy>复制全部命令</button><pre><code>cd ai-kb

python gen_data.py          # 造 20,000 份申请（含「被拒保的人没有出险记录」机制）
python _facts.py           # 抽出唯一数字源 out/facts.json
python test_models.py      # 先验证手写模型的正确性，别在错模型上谈精度
python train_evaluate.py   # 主流水线 step1~step5：读数据→定义标签→切分→四模型→评估
python steps_678.py        # step6~step8：给拒保人打分、算业务账、四种偏差修法对比
python _tune.py            # 反推一套「梯度成立」的核保规则系数
python fig_01_look.py      # 业务侧关键图
python fig_02_model.py     # 模型侧九张图
python _check.py           # 站点自检：七类检查，0 failures
python _build.py           # 生成全部页面 + src/ 源码浏览页</code></pre></div>
<div class="note jade"><b>为什么推荐按这个顺序跑？</b>
<code>test_models.py</code> 放在最前面，是因为<b>自己手写模型必须先证明自己没写错</b>——
不然你调了半天，可能只是在调一个 bug。这一步省不得。</div>

{_three([
    "机器学习项目是<b>七步环，不是一条直线</b>；数据不行就退回第 ② 步，这是常态。",
    "真正决定成败的<b>不是第 ⑥ 步（建模），而是第 ② ③ 步（数据从哪来、标签怎么定义）</b>。",
    "跑完命令序列不是终点，<b>要能回答「这份圈选名单给业务，能省多少钱」</b>——那才是落地。",
])}

<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>把一个「AI 项目」排进计划时，别按模型复杂度估工期，按<b>七步里最慢的那一步</b>估。
实践里最常拖死项目的从来不是调参，是<b>等数据口径对齐、等标签定义拍板、等业务方确认成功标准</b>。
这三项合起来，通常比写代码多花一倍的时间。</p></div>
"""


# ============================================================ B11 算法按任务分类
def p_b11(F):
    def col(x, title, desc, icon, algos):
        c = x + 76
        alg = "".join(f'<text x="{c}" y="{y}" font-size="11.5" fill="{INK}" '
                      f'text-anchor="middle">{a}</text>'
                      for y, a in zip((166, 184, 202), algos))
        return (f'<rect x="{x}" y="10" width="152" height="196" rx="10" fill="#fbf8ef" stroke="{LINE}"/>'
                f'<text x="{c}" y="36" font-size="12.5" fill="{INK}" text-anchor="middle">{title}</text>'
                f'<text x="{c}" y="56" font-size="10.5" fill="{GREY}" text-anchor="middle">{desc}</text>'
                f'{icon}{alg}')

    def axes(cx):
        return (f'<line x1="{cx-38}" y1="140" x2="{cx+38}" y2="140" stroke="{LINE}"/>'
                f'<line x1="{cx-38}" y1="140" x2="{cx-38}" y2="74" stroke="{LINE}"/>')

    i_a = (f'{axes(86)}'
           f'<circle cx="68" cy="118" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<circle cx="82" cy="104" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<circle cx="94" cy="126" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<circle cx="72" cy="88" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<circle cx="104" cy="96" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<circle cx="112" cy="112" r="3.2" fill="{JADE}" opacity="0.6"/>'
           f'<line x1="60" y1="132" x2="122" y2="80" stroke="{RED}" stroke-width="1.8"/>')
    i_b = (f'{axes(246)}'
           f'<circle cx="226" cy="112" r="3.4" fill="{JADE}" opacity="0.75"/>'
           f'<circle cx="236" cy="126" r="3.4" fill="{JADE}" opacity="0.75"/>'
           f'<circle cx="224" cy="94" r="3.4" fill="{JADE}" opacity="0.75"/>'
           f'<circle cx="266" cy="100" r="3.4" fill="{RED}" opacity="0.75"/>'
           f'<circle cx="278" cy="118" r="3.4" fill="{RED}" opacity="0.75"/>'
           f'<circle cx="264" cy="130" r="3.4" fill="{RED}" opacity="0.75"/>'
           f'<line x1="250" y1="72" x2="250" y2="140" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    i_c = (f'<circle cx="216" cy="118" r="26" fill="none" stroke="{JADE}" stroke-dasharray="4 3"/>'
           f'<circle cx="292" cy="82" r="26" fill="none" stroke="{AMBER}" stroke-dasharray="4 3"/>'
           f'<circle cx="206" cy="112" r="3.4" fill="{JADE}"/>'
           f'<circle cx="220" cy="122" r="3.4" fill="{JADE}"/>'
           f'<circle cx="212" cy="100" r="3.4" fill="{JADE}"/>'
           f'<circle cx="224" cy="106" r="3.4" fill="{JADE}"/>'
           f'<circle cx="284" cy="76" r="3.4" fill="{AMBER}"/>'
           f'<circle cx="298" cy="90" r="3.4" fill="{AMBER}"/>'
           f'<circle cx="288" cy="66" r="3.4" fill="{AMBER}"/>'
           f'<circle cx="300" cy="76" r="3.4" fill="{AMBER}"/>')
    i_d = (f'{axes(406)}'
           f'<circle cx="382" cy="112" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<circle cx="394" cy="128" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<circle cx="378" cy="88" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<circle cx="392" cy="106" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<circle cx="386" cy="120" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<circle cx="398" cy="94" r="3.4" fill="{JADE}" opacity="0.7"/>'
           f'<line x1="418" y1="110" x2="446" y2="110" stroke="{RED}" stroke-width="1.6"/>'
           f'<circle cx="452" cy="106" r="4" fill="{RED}"/>'
           f'<circle cx="452" cy="118" r="4" fill="{RED}"/>')

    body = (col(10, "① 回归算法", "预测连续数值", i_a,
                ["线性回归 / 岭回归", "Lasso / Ridge", "决策树 / GBDT"])
            + col(170, "② 分类算法", "预测类别结果", i_b,
                  ["逻辑回归 / KNN", "SVM", "决策树 / 随机森林"])
            + col(330, "③ 聚类算法", "没有标签时自动分组", i_c,
                  ["K-Means", "层次聚类", "DBSCAN / GMM"])
            + col(490, "④ 降维方法", "压缩特征、提主信息", i_d,
                  ["PCA", "LDA", "特征选择"]))
    return f"""
<h1><span class="thin">基础篇 · B11</span>
算法怎么分：先按任务分，再记名字</h1>
<p class="lead">学机器学习最容易走错的路，是<b>把算法名当菜单背</b>——线性回归、决策树、随机森林、K-Means、SVM……
一长串，背完还是不知道该用哪个。正确的顺序是：<b>先看你的业务问题要预测什么，再去看哪个算法管这摊事。</b></p>

{_svg(644, 210, body, "四类任务是「按要预测什么」分的：连续数值→回归，类别→分类，无标签分组→聚类，压缩特征→降维。")}

{_step_frame(
  "把「该用哪个算法」这个问题，从背名字改成「先问我要预测什么」。",
  "一张四分区表：任务类型 → 典型算法 → 本案例用哪几个 → 对应哪一页。",
  "先读四分区图建立分类感；再对照「本案例落在哪一格」确认自己在干什么；最后看算法选择四问，下次拿到新问题自己就能定。")}

<h2 id="task">先按「要预测什么」分，不是按算法名分</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th style="width:15%">任务类型</th><th style="width:26%">要预测的是什么</th>
    <th style="width:30%">典型算法</th><th style="width:29%">生活里的例子</th></tr>
<tr><td><b>回归</b></td><td>一个<b>连续数字</b>：多少钱、几次、多 long</td>
    <td>线性回归、岭/Lasso 回归、决策树回归、GBDT</td><td>房价、销量、成本、<b>出险次数</b></td></tr>
<tr><td><b>分类</b></td><td>一个<b>类别</b>：是或不是、A 类还是 B 类</td>
    <td>逻辑回归、KNN、SVM、决策树、随机森林</td><td>会不会流失、是不是垃圾邮件、<b>好司机还是坏司机</b></td></tr>
<tr><td><b>聚类</b></td><td><b>没有标签</b>，只想把相似的归成一堆</td>
    <td>K-Means、层次聚类、DBSCAN、GMM</td><td>用户分群、商品分层</td></tr>
<tr><td><b>降维</b></td><td>特征太多，想<b>压缩又保留主要信息</b></td>
    <td>PCA、LDA、特征选择</td><td>特征压缩、画散点图</td></tr>
</table></div>
<p>注意一件事：<b>回归和分类是「有监督」的</b>（有标准答案），聚类和降维是「无监督」的（没有答案，只有结构）。
所以判断顺序其实只有两个问题：<b>① 有没有已知答案？② 答案是个数字还是个类别？</b>详见 <a href="b07.html">B7</a> 三大类型。</p>

<h2 id="case">本案例落在哪一格</h2>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>我们的目标是「这些被拒保的人，真实风险有多高」。风险高不高，是个<b>数字</b>（一年大概赔多少钱），
所以落在<b>回归</b>这一格——不是分类。具体拆成两个模型：<b>出险次数</b>（多少次，计数型）用 Poisson 回归，
<b>每次赔多少</b>（案均损失）用树模型，两个相乘得到<b>纯保费</b>。这就是 <a href="ch03.html">ch03</a> 说的「频率 × 损失」。</p></div>
<div class="note jade"><b>但这里有个反直觉的地方，值得停一下：</b>
我们最后<b>没有</b>拿预测出来的金额直接定价，而是拿它<b>排序、圈人</b>。
圈选这个动作看起来像分类（圈 / 不圈），但它考核的不是「圈对了没有」，而是「<b>圈出来的这批人里，好司机占比高不高</b>」——
所以看的是 <b>AUC 和纯度</b>，不是准确率。算法选回归，考核用排序指标，这是两件事。</div>

<h2 id="four">下次拿到新问题，用这四问定算法</h2>
<div class="steps">
  <div class="step"><h4>第一问：我要预测的东西，是不是一个数字？</h4>
    <p>是 → <b>回归</b>。赔多少钱、出几次险、什么时候来——都是回归。<br>
    不是（是「是/否」「A/B/C」）→ <b>分类</b>。</p></div>
  <div class="step"><h4>第二问：我手上有没有「已知答案」的历史数据？</h4>
    <p>有 → 可以继续做回归 / 分类（<b>监督学习</b>）。<br>
    <b>没有</b>，只是想按相似性分堆 → <b>聚类</b>（<b>无监督</b>），比如把客户分成高/中/低活跃。</p></div>
  <div class="step"><h4>第三问：是不是没有答案、也没有对错，只要求一个最优策略？</h4>
    <p>是 → <b>强化学习</b>：在环境里反复试错，做对了给奖励。典型如自动驾驶、游戏 AI、动态定价策略。</p></div>
  <div class="step"><h4>第四问：前面都定了，还差什么？</h4>
    <p>特征太多 → <b>降维/特征选择</b>；想要更稳 → <b>集成</b>（多棵树投票 / 逐轮补差）；
    要能给人解释 → 优先<b>单棵决策树或 GLM</b>，别上黑箱集成。</p></div>
</div>

{_three([
    "记名字之前先记任务：<b>数字→回归，类别→分类，无标签→聚类，特征太多→降维</b>。",
    "本案例预测的是<b>纯保费（连续数字）</b>，所以是回归；但落地动作是排序圈人，所以<b>看 AUC 不看准确率</b>。",
    "「算法越复杂越好」是错的：<b>能解释、能落地</b>的算法，常常比高 1 个点准确率的黑箱值钱得多。",
])}
"""


# ============================================================ B12 选模型的决策路径
def p_b12(F):
    inner = f"""
<circle cx="322" cy="44" r="32" fill="#fbf8ef" stroke="{LINE}"/>
<text x="322" y="49" font-size="12.5" fill="{INK}" text-anchor="middle">业务问题</text>
<polygon points="322,94 402,132 322,170 242,132" fill="#fbf8ef" stroke="{JADE}" stroke-width="1.6"/>
<text x="322" y="137" font-size="11" fill="{JADE}" text-anchor="middle">有明确目标结果吗？</text>
<polygon points="112,196 194,234 112,272 30,234" fill="#fbf8ef" stroke="{JADE}" stroke-width="1.6"/>
<text x="112" y="239" font-size="10.5" fill="{JADE}" text-anchor="middle">自动分组还是学策略？</text>
<polygon points="510,196 592,234 510,272 428,234" fill="#fbf8ef" stroke="{JADE}" stroke-width="1.6"/>
<text x="510" y="239" font-size="10.5" fill="{JADE}" text-anchor="middle">连续数值还是类别？</text>
<text x="200" y="212" font-size="10.5" fill="{RED}" text-anchor="middle">没有</text>
<text x="440" y="212" font-size="10.5" fill="{RED}" text-anchor="middle">有</text>
<path d="M 322 78 L 322 90" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 268 168 L 190 208" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 376 168 L 460 208" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 108 274 L 100 308" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 142 274 L 182 308" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 506 274 L 470 308" stroke="{JADE}" stroke-width="1.5"/>
<path d="M 522 276 L 560 308" stroke="{JADE}" stroke-width="1.5"/>
<rect x="14" y="310" width="176" height="48" rx="8" fill="{JADE}" opacity="0.1" stroke="{JADE}"/>
<text x="102" y="330" font-size="11.5" fill="{INK}" text-anchor="middle">聚类 / 无监督</text>
<text x="102" y="348" font-size="9.5" fill="{GREY}" text-anchor="middle">没有标签，自动分组</text>
<rect x="206" y="310" width="176" height="48" rx="8" fill="{JADE}" opacity="0.1" stroke="{JADE}"/>
<text x="294" y="330" font-size="11.5" fill="{INK}" text-anchor="middle">强化学习</text>
<text x="294" y="348" font-size="9.5" fill="{GREY}" text-anchor="middle">反复试错换奖励</text>
<rect x="398" y="310" width="122" height="48" rx="8" fill="{AMBER}" opacity="0.14" stroke="{AMBER}"/>
<text x="459" y="330" font-size="11.5" fill="{INK}" text-anchor="middle">回归</text>
<text x="459" y="348" font-size="9.5" fill="{GREY}" text-anchor="middle">预测连续值</text>
<rect x="534" y="310" width="108" height="48" rx="8" fill="{AMBER}" opacity="0.14" stroke="{AMBER}"/>
<text x="591" y="330" font-size="11.5" fill="{INK}" text-anchor="middle">分类</text>
<text x="591" y="348" font-size="9.5" fill="{GREY}" text-anchor="middle">预测类别</text>
<rect x="14" y="386" width="616" height="40" rx="8" fill="{JADE}" opacity="0.1" stroke="{JADE}"/>
<text x="322" y="412" font-size="11" fill="{JADE}" text-anchor="middle">本案例：有标签 + 预测连续值（出险次数、案均损失）→ 回归；但落地动作是「排序 + 圈选」，重点看 AUC</text>
"""
    return f"""
<h1><span class="thin">基础篇 · B12</span>
遇到问题，到底该选哪类模型</h1>
<p class="lead">选模型的第一步<b>不是挑算法，是定义任务</b>。
同样一份客户表，你想「猜他今年赔多少钱」和想「判断他会不会跑掉」，
是两个完全不同的问题，要用两套完全不同的模型和两套完全不同的指标。</p>

{_svg(644, 430, inner, "从业务问题出发，连问三个问题（有没有目标结果 → 是数字还是类别 → 有标签还是求策略），就能落到唯一一支任务类型上。")}

{_step_frame(
  "把「我们到底要解决什么」翻译成「这是回归、分类、聚类还是强化学习」。",
  "一张决策路径图 + 四个常见场景的判定 + 一句判断口诀。",
  "照着图从上往下走：只要能回答出「有没有目标结果」「结果是数字还是类别」，路线就定死了；最后对号入座看本案例落点。")}

<h2 id="path">决策路径：三个问题定死一条路</h2>
<p>看图，从上往下问自己三句话，答案就出来了：</p>
<ul>
<li><b>第 1 问（图顶部）：「我到底想算出个什么东西出来？」</b><br>
  想不出来 → 说明你可能还<b>没定义清楚业务问题</b>，这时候写代码就是浪费时间。<br>
  想得出来 → 进第 2 问。</li>
<li><b>第 2 问（右上）：「那个东西，是一个数字，还是一类标签？」</b><br>
  数字（赔多少钱、出几次险、什么时候来）→ <b>回归</b>；<br>
  标签（会/不会、是/不是、A 类/B 类）→ <b>分类</b>。</li>
<li><b>第 3 问（左下）：「我手上压根没有已知答案，只是想分个堆？」</b><br>
  想自动分组 → <b>聚类（无监督）</b>；<br>
  要在环境里反复试错求最优 → <b>强化学习</b>。</li>
</ul>

<h2 id="scene">四个常见场景，对号入座</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th style="width:8%">编号</th><th style="width:26%">业务问题</th>
    <th style="width:24%">要输出什么</th><th style="width:14%">落在哪一支</th><th style="width:28%">学习类型</th></tr>
<tr><td><b>1</b></td><td>预测一套房子值多少钱</td><td>一个具体价格</td><td><b>回归</b></td><td>监督学习</td></tr>
<tr><td><b>2</b></td><td>这个客户会不会流失</td><td>会 / 不会</td><td><b>分类</b></td><td>监督学习</td></tr>
<tr><td><b>3</b></td><td>把这一万个人自动分群</td><td>没有现成标签，自己分组</td><td><b>聚类</b></td><td>无监督学习</td></tr>
<tr><td><b>4</b></td><td>让智能体学会最优动作</td><td>反复试错，追求奖励最大</td><td><b>强化学习</b></td><td>另起一支</td></tr>
</table></div>
<p>注意第 3 行和第 2 行的区别：<b>「会不会流失」是有历史答案的</b>（去年留下来的人，今年到底留没留），
所以能做分类；<b>「自动分群」你连「群」该叫什么名字都不知道</b>，只能让机器按相似度高不高自己抱堆。</p>

<h2 id="case">本案例走的是哪条路</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th style="width:26%">决策问题</th><th style="width:30%">本案例的答案</th><th style="width:44%">为什么这么答</th></tr>
<tr><td>有明确目标结果吗？</td><td><b>有</b></td><td>「这批被拒的人，真实风险有多高」——一个明确的、可计算的量</td></tr>
<tr><td>结果是数字还是类别？</td><td><b>数字 → 回归</b></td><td>要预测的是纯保费（continuous），拆成出险次数 + 案均损失两块</td></tr>
<tr><td>有标签吗？</td><td><b>只有一部分人有</b></td><td>11,200 个已承保的人有真实出险记录，8,800 个拒保的<b>一个都没有</b>——这才是本案例真正的难点</td></tr>
<tr><td>考核指标是什么？</td><td><b>AUC / 圈选纯度</b></td><td>落地动作是「排序 + 圈人」，不是定价，所以不看准确率，看排序能力</td></tr>
</table></div>
<div class="note red"><b>本案例最容易答错的一题：</b>
有人会脱口而出「这是二分类——好司机 / 坏司机」。
<b>不是。</b>「好 / 坏」只是我们最后<b>圈完之后贴的标签</b>（圈出来的叫疑似好司机），
模型从头到尾学的都是<b>纯保费这个连续数字</b>。把「业务上的圈选决定」和「模型要预测的量」混为一谈，
是初学阶段最常见的分类错误。</div>

<h2 id="口诀">判断口诀（背这一句就够）</h2>
<div class="note jade"><b>想预测多少 → 回归；判断属于哪类 → 分类；没有标签先分组 → 聚类；连续试错求最优 → 强化学习。</b></div>
<p>把这四句和 <a href="b11.html">B11</a> 的四分区图放一起看：<b>左边那两支（回归 / 分类）是有监督的，右边（聚类 / 强化）是无监督或另起一脉的</b>。
判断顺序永远是先看「要预测什么」，不是先看「哪个算法名字熟」。</p>

{_three([
    "选模型的<b>第一步不是挑算法，是定义任务</b>——先回答「我要预测什么」。",
    "数字→回归，类别→分类，无标签→聚类，试错求奖励→强化学习；本案例走的是<b>回归</b>这一支。",
    "「业务上圈不圈」和「模型预测什么」是两件事，<b>别把它们混成一个分类问题</b>。",
])}
"""


# ============================================================ B13 六个最常见的误区
def p_b13(F):
    rows_l = ["① 训练集分数高，就说明模型好",
              "② 模型越复杂越好",
              "③ 数据量越多越好",
              "④ 特征越多越好",
              "⑤ 准确率高就一定可用",
              "⑥ 把模型跑出来就结束了"]
    rows_r = ["训练 / 验证 / 测试三个都要看",
              "简单模型往往更稳、更好解释",
              "数据质量与口径比数量重要得多",
              "无效特征只会增加噪声、拖慢训练",
              "类别不平衡时，准确率会骗你",
              "还要解释结果、监控效果、回业务迭代"]
    inner = ""
    for i, (a, b) in enumerate(zip(rows_l, rows_r)):
        y = 60 + i * 36
        inner += (f'<text x="30" y="{y}" font-size="10.5" fill="{RED}">✗</text>'
                  f'<text x="44" y="{y}" font-size="10.5" fill="{INK}">{a}</text>'
                  f'<text x="410" y="{y}" font-size="10.5" fill="{GREY}">✓</text>'
                  f'<text x="424" y="{y}" font-size="10.5" fill="{INK}">{b}</text>')
    inner += (f'<line x1="20" y1="266" x2="624" y2="266" stroke="{LINE}"/>'
              f'<text x="322" y="290" font-size="11" fill="{JADE}" text-anchor="middle">'
              f'真正该关注四件事：① 问题定义清不清晰　② 数据质量靠不靠谱　③ 模型有没有泛化能力　④ 结果能不能指导业务</text>')
    return f"""
<h1><span class="thin">基础篇 · B13</span>
机器学习最常见的六个误区</h1>
<p class="lead">很多模型问题，<b>不是算法不够强，是认知先出了偏差</b>。
下面这六句话，每一句听着都挺像那么回事，每一句都能把项目带沟里去。
本案例在写的过程中基本<b>全踩过一遍</b>，所以这一页不举教科书例子，只讲我们翻过的车。</p>

{_svg(644, 300, inner, "左边是六个听起来很对、实际很坑的念头；右边是对应的纠正。底部是真正该长期盯着的四件事。")}

{_step_frame(
  "识别六句「听着对、做就错」的行话，避免在项目还没开始时就把方向走歪。",
  "六条纠正 + 本案例里对应的真实数字（比如外推纯度从 96.6% 掉到 62.2%）。",
  "对照这张对照表扫一遍，看自己中了哪几条；尤其第 5、6 条，是本项目真正付出代价的两条。")}

<h2 id="m1">误区一：训练集分数高，就说明模型好</h2>
<p><b>错在哪：</b>模型可以<b>把训练样本整段背下来</b>——这不是学会，是抄答案。真正该看的是它面对<b>从没见过的人</b>表现如何。</p>
<p><b>本案例：</b>内插域（模型见过的那 11,200 人）AUC <b>0.885</b>、圈最便宜 20% 的纯度 <b>96.6%</b>；
换成外推域（8,800 个从没见过的人），AUC 掉到 <b>0.833</b>、纯度掉到 <b>62.2%</b>——<b>掉了 18.9 个百分点</b>。</p>
<div class="note"><b>怎么防：</b>留一份数据当「期末考」(<a href="b05.html">B5</a>)，考前一次都不许看。
这份数据只用来算最后的成绩，不参与任何调参。</div>

<h2 id="m2">误区二：模型越复杂越好</h2>
<p><b>错在哪：</b>复杂模型能记住更多噪声。它把「这条规则有偏差」这种偶然事件也当成规律学了。</p>
<p><b>本案例：</b>四个模型里，最朴素的<b>常数基线</b>（什么特征都不看）deviance 是 8,994.5；
Poisson GLM 建模纯保费后是 9,005.9，<b>反而是基线的 100.1%</b>——
也就是说「直接上模型」这一动作<b>一点忙都没帮上</b>（详见 <a href="ch03.html">ch03</a>）。
最后是靠拆成「频率 × 损失」才真正动起来。</p>
<div class="note"><b>正确的问法：</b>「这个复杂度，换来的提升配得上它的代价吗？」
代价包括：更难解释、更难维护、出错时更难定位。保险定价里，<b>能讲清为什么的人比准确率高 0.5 个点更重要</b>。</div>

<h2 id="m3">误区三：数据越多越好</h2>
<p><b>错在哪：</b>100 万条口径不一致的数据，不如 1 万条干净的数据。<b>标签错一点，数据再多也是往沟里带。</b></p>
<p><b>本案例：</b>最致命的一处就是 <code>claim_cnt = −1</code>。
它的意思是「<b>这个人的出险记录我们不知道</b>」，不是「这个人一次险都没出过」。
只要把它当成 0，等于宣称「被拒的 8,800 个全都是完美司机」——
模型会学出一个荒唐结论，而且<b>样本越多，学得越自信、越离谱</b>。详见 <a href="ch02.html">ch02</a>。</p>
<div class="note"><b>投入顺序建议：</b>先花时间统一口径、补齐标签定义，再谈加数据量。</div>

<h2 id="m4">误区四：特征越多越好</h2>
<p><b>错在哪：</b>无效特征增加噪声，还拖慢训练、让人更难判断哪个特征真有用。</p>
<p><b>本案例：</b>我们特意用了 <b>IPW 逆概率加权 / 双重稳健</b> 来修正「渠道」这类变量（<a href="ch08.html">ch08</a>），
因为线上渠道错杀率是代理渠道的 <b>2.3 倍</b>——「渠道」这个特征不是没用，
而是<b>它混进了「资料全不全」和「风险高不高」两件事</b>。加特征容易，判断特征「该不该加」才难。</p>
<div class="note"><b>本案例的做法：</b>不是一刀切删掉渠道，而是把它<b>单独拎出来做敏感性分析</b>，
看结论在「含渠道 / 不含渠道」下稳不稳。稳，就留。</div>

<h2 id="m5">误区五：准确率高就一定可用</h2>
<p><b>错在哪：</b>类别不平衡时，准确率会骗人。比如模型对所有人都判「不出险」，准确率可以高达 90%+，
但它<b>一个坏司机都没找出来</b>。</p>
<p><b>本案例：</b>我们<b>根本不看准确率</b>，看的是<b>圈最便宜 20% 里好司机占比（纯度）</b>和<b>召回率</b>。
模型内插域纯度 <b>96.6%</b>、外推域 <b>62.2%</b>；圈 4,400 件时业务增益最大，<b>387,474 元</b>（<a href="ch10.html">ch10</a>）。
这三个数字放在一起，才回答了「划不划算」。</p>
<div class="note red"><b>这一条的影子在 ch11 出现过：</b>模型 B 报表上全面优于 A，但它其实一点都没更准，
只是把预测刻度整体压低了。<b>指标要成对看，别只看一个。</b></div>

<h2 id="m6">误区六：把模型跑出来就结束了</h2>
<p><b>错在哪：</b>模型上线只是开始。它<b>需要被解释、被监控、被业务持续迭代</b>。</p>
<p><b>本案例：</b>我们最后给的不是一个模型，是一份 <b>SOP 与清单</b>（<a href="ch13.html">ch13</a>）：
第一年只做保守版——<b>只对「模型熟悉的人」放宽，远点维持原规则</b>。
为什么？因为外推域的纯度只有 <b>62.2%</b>，还没到「可以规模化放开」的程度。</p>
<div class="note jade"><b>上线后真正要看的四件事：</b>
① 谁被改了结论、改成了什么；② 这批人的实际赔付，和预测差多少（<b>校准漂移</b>）；
③ 渠道 / 车型结构变了没有（<b>分布漂移</b>）；④ 业务侧按名单复核完，省下来多少钱。
四项任一超标，退回第 ② 步重来。</div>

{_three([
    "六句话听着都挺对，<b>每一句都能把项目带沟里</b>：训练集高分、越复杂越好、数据越多越好、特征越多越好、准确率高就可用、跑完就结束了。",
    "本案例真正付过代价的是<b>第 5、6 条</b>：外推纯度从 96.6% 掉到 62.2%，直接决定了第一年只能保守上线。",
    "记住对照表底部那四件事：<b>问题定义、数据质量、泛化能力、能不能指导业务</b>——这才是长期该盯的。",
])}
"""


PAGES_BASIC = [
    ("b01", "B1", "机器学习到底在干什么", p_b01),
    ("b02", "B2", "数据长什么样：一行一个人", p_b02),
    ("b03", "B3", "模型是什么：一个会算数的套路", p_b03),
    ("b04", "B4", "训练是什么：反复改到改不动", p_b04),
    ("b05", "B5", "过拟合：背熟习题却考砸", p_b05),
    ("b06", "B6", "算法是什么：找数字的工艺", p_b06),
    ("b07", "B7", "家族树：AI / ML / 深度学习", p_b07),
    ("b08", "B8", "怎么判断一个模型好不好", p_b08),
    ("b09", "B9", "学习地图 · 门路推荐", p_b09),
    ("b10", "B10", "端到端：从问题定义到落地", p_b10),
    ("b11", "B11", "算法怎么分：先按任务分", p_b11),
    ("b12", "B12", "遇到问题该选哪类模型", p_b12),
    ("b13", "B13", "最常见的六个误区", p_b13),
    ("b14", "B14", "模型是怎么被教会的一趟下山路", p_b14),
]
