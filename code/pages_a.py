# -*- coding: utf-8 -*-
"""AI 实践库 · 页面内容 A：总览 + 01 从 GLM 出发 + 02 标签不可见 + 03 频率×损失"""


def _toc(items):
    h = ['<div class="toc"><div class="t">本页目录</div>']
    for a, t in items:
        h.append(f'<a href="#{a}">{t}</a>')
    h.append("</div>")
    return "\n".join(h)


def _fig(name, cap):
    return (f'<div class="fig"><img src="img/{name}" alt="">'
            f'<div class="fig-cap">{cap}</div></div>')


def _step_frame(goal, output, howto):
    """场景页通用的「目标 / 输出 / 怎么读」三栏框。
    让每一页一上来就讲清：这页要干嘛、会产出什么、结论该怎么看。"""
    return f"""
<div class="gof">
  <div class="gof-h">本页要做的三件事</div>
  <div class="gof-row"><span class="gof-k gof-goal">目标</span>
    <div class="gof-v">{goal}</div></div>
  <div class="gof-row"><span class="gof-k gof-out">输出</span>
    <div class="gof-v">{output}</div></div>
  <div class="gof-row"><span class="gof-k gof-read">怎么读</span>
    <div class="gof-v">{howto}</div></div>
</div>"""


from pages_basics import _svg, _why   # 放在 _toc 定义之后，避免循环导入


# ================================================================ 总览
from terms import TERMS
from navmap import NAV


def _kmap():
    """知识地图：直接从 NAV 生成。

    为什么不手写——手写会和侧栏各说一套，加一页就要改两处还容易漏。
    这里读的是同一个 NAV，加页、调顺序，地图自动跟上。
    """
    # 先把 NAV 切成「段 → [(子组标题 or None, [(fn, title, no)])]」
    segs, cur = [], None
    for item in NAV:
        if item[1] is None:
            if item[0].startswith("第"):
                cur = {"name": item[0], "rows": []}
                segs.append(cur)
            elif cur is not None:
                cur["rows"].append([item[0], []])
            continue
        if cur is None or not cur["rows"]:
            cur["rows"].append([None, []])
        cur["rows"][-1][1].append(item)

    out = ['<div class="kmap">']
    for k, seg in enumerate(segs):
        head = seg["name"].split(" · ")
        no = head[0]                                  # 「第 0 段」
        rest = head[1] if len(head) > 1 else ""
        name = rest.split("：")[0]                     # 「知识地图」
        desc = rest.split("：")[1] if "：" in rest else ""
        n = sum(len(r[1]) for r in seg["rows"])
        out.append(f'<div class="km-seg s{k}"><div class="km-hd">'
                   f'<span class="km-no">{no}</span>'
                   f'<span class="km-t">{name}</span>'
                   f'<span class="km-d">{desc} · {n} 页</span></div>'
                   f'<div class="km-bd">')
        for sub, pages in seg["rows"]:
            if sub:
                out.append(f'<div style="margin-top:6px;color:var(--cinnabar);'
                           f'font-size:12.5px">{sub}</div>')
            line = []
            for fn, title, no2 in pages:
                line.append(f'<a href="{fn}.html"><code>{no2}</code> {title}</a>')
            out.append(" · ".join(line))
        out.append("</div></div>")
    out.append("</div>")
    return "\n".join(out)


def _routes():
    """四条路线：不同角色从哪里进、按什么顺序读。"""
    def card(who, when, steps, end):
        li = "".join(f'<li><a href="{fn}.html">{t}</a></li>' for fn, t in steps)
        return (f'<div class="route"><div class="rt-who">{who}</div>'
                f'<div class="rt-when">{when}</div><ol>{li}</ol>'
                f'<div class="rt-end">{end}</div></div>')

    return '<div class="routes">' + "".join([
        card("我完全零基础", "没写过代码，想搞懂这东西在干嘛",
             [("index", "知识地图"), ("x01", "一页讲清楚"),
              ("b01", "机器学习到底在干什么"), ("b12", "数据长什么样"),
              ("b03", "模型是什么"), ("ch04", "动画 · GLM 迭代"),
              ("s07", "三十秒版本")],
             "读完能向别人讲清这件事，约 40 分钟"),
        card("我是精算 / 风控", "想知道这套能不能用在自己公司",
             [("x01", "一页讲清楚"), ("s02", "不用机器学习行不行"),
              ("p01", "把问题翻译成可计算的题"), ("ch07", "选择偏差"),
              ("ch08", "IPW 与双重稳健"), ("ch10", "业务账与圈选阈值"),
              ("s03", "投入产出账")],
             "拿到一套可复用的判断口径，约 70 分钟"),
        card("我是管理层", "只要结论和风险边界",
             [("s07", "三十秒版本"), ("x01", "一页讲清楚"),
              ("s02", "不用 ML 行不行"), ("s03", "投入产出账"),
              ("s06", "组织与分工")],
             "能拍板要不要干，约 15 分钟"),
        card("我想照着做一遍", "要复现、要改代码",
             [("b10", "路线图：端到端七步"), ("p01", "问题定义"),
              ("ch01", "从 GLM 出发"), ("ch03", "频率 × 损失"),
              ("ch09", "外推风险"), ("ch12", "端到端复盘"),
              ("m01", "模型速查")],
             "顺着这条线能跑通全流程，半天起"),
    ]) + "</div>"


def p_index(F):
    return f"""
<h1><span class="thin">AI 实践库 · 场景一 · 定价</span>
找出被<span style="color:var(--cinnabar)">错杀</span>的好司机</h1>

<h2>知识地图：这套库怎么读</h2>
<p>整库分四段，<b>一条主线</b>：先看全貌 → 把道理讲透 → 从问题定义一路做到落地 → 随查随用。
编号是连续的，看编号就知道读到哪一段、哪一阶段。</p>
{_kmap()}

<h2>四条路线：你属于哪一种</h2>
<p>不用从头读到尾。挑一条最接近你的：</p>
{_routes()}

<div class="quote q-talk"><span class="q-tag">一句话</span>
<p>保险公司用一套规则拒掉了 {F['n_rej']:,} 个人。
我们用机器学习回看了一遍，发现其中有 <b>{F['n_wrongly_killed']:,} 个人其实比已承保客户还安全</b>——
他们是被规则冤枉的。这个库讲的就是：<b>怎么把这批人找回来，
以及怎么确认机器没有骗我们。</b>
以及最后一件事——<b>什么时候不该用机器学习</b>。</p></div>

<h2>三问三答：如果你只想知道结论</h2>
<div class="ans3">
  <a class="ans-item" href="x01.html#q1">
    <span class="aq">解决什么问题</span>
    <span class="aa">在被规则拒掉的 {F['n_rej']:,} 个人里，
      有 {F['n_wrongly_killed']:,} 人的真实风险比已承保客户还低。
      他们被冤枉了，而公司看不见——因为被拒的人不在公司，没有出险记录。</span></a>
  <a class="ans-item" href="x01.html#q2">
    <span class="aq">采用什么方法</span>
    <span class="aa">不是「训练一个模型」，是四步：拆成频率 × 损失分别建模、
      给被抽歪的审计样本加权、外推时只排序不定价、阈值贴着盈亏平衡点定。</span></a>
  <a class="ans-item" href="x01.html#q3">
    <span class="aq">达到什么效果</span>
    <span class="aa">原来 {F['n_rej']:,} 件要一张张翻，现在先翻 {F['thr_peak_n']:,} 件就找回了大部分；
      单件复核成本低于 {F['thr_peak_gain']/F['thr_peak_n']:.0f} 元就划算。</span></a>
</div>
<div class="note jade"><b>完整版（含全部数字与深读入口）见
<a href="x01.html">X · 一页讲清楚：问题 · 方法 · 效果</a>。</b>
模型是<b>排队机</b>，不是裁判：它不决定谁对谁错，只决定<b>谁先被看</b>。</div>

<h2>先花一分钟：这到底是个什么问题</h2>
<p>假设你面前坐着 {F['n_total']:,} 个来投保的司机。公司有一套核保规则——
年龄多少加几分、什么车型加几分、什么渠道加几分，加过线就拒保。</p>
<p>这套规则<b>讲得通</b>，但它有两个毛病：</p>
<div class="steps">
<div class="step"><h4>毛病一：分数是人拍的</h4>
<p>「线上渠道加 7 分」——这个 7 是哪来的？大概率是某年某次开会定的，
没人验证过它到底是保护了公司，还是赶走了客户。</p></div>
<div class="step"><h4>毛病二：它分不清「危险」和「不好查」</h4>
<p>线上渠道的客户不是更爱出事，只是资料不全、不好核实。
规则把「信息难不难拿到」当成了「风险高不高」，
结果线上渠道的错杀率是代理渠道的 <b>{F['kill_ratio_online_vs_agent']} 倍</b>。</p></div>
</div>
<p>于是 {F['n_wrongly_killed']:,} 个真实风险很低的人被拒之门外。
他们不是坏客户，他们只是<b>长得像坏客户</b>。</p>

<h2>如果你完全零基础，先读这十四页</h2>
<div class="note jade"><b>这一组是专门为零基础写的。</b>不用任何数学，全是比方。
读完这十四页，你再回来看这个案例，会发现所有术语都认识你了。</div>
<div class="card-grid">
  <a class="card" href="b01.html"><span class="no">B1</span>
    <div class="t">机器学习到底在干什么</div>
    <div class="d">一个猜房价的游戏。看完你会说：哦，就这么回事。</div>
    <span class="tag">必读 · 第一页</span></a>
  <a class="card" href="b02.html"><span class="no">B2</span>
    <div class="t">数据长什么样</div>
    <div class="d">一行一个人、一列一个属性。以及 −1 不是 0 这个致命细节。</div>
    <span class="tag">必读</span></a>
  <a class="card" href="b03.html"><span class="no">B3</span>
    <div class="t">模型是什么</div>
    <div class="d">你每天都在用好几个模型：菜谱、评分表、核保规则分。</div>
    <span class="tag">必读</span></a>
  <a class="card" href="b04.html"><span class="no">B4</span>
    <div class="t">训练是什么</div>
    <div class="d">猜 → 看差距 → 挪一点，然后重复。就这三步。</div>
    <span class="tag">必读</span></a>
  <a class="card" href="b05.html"><span class="no">B5</span>
    <div class="t">过拟合：为什么模型会考砸</div>
    <div class="d">留出一份没见过的数据当期末考，考前一次都不许看。</div>
    <span class="tag anim">第一号翻车原因</span></a>
  <a class="card" href="b06.html"><span class="no">B6</span>
    <div class="t">算法是什么</div>
    <div class="d">模型是成品，算法是工艺。还有几个旋钮得人来拧。</div>
    <span class="tag">选读</span></a>
  <a class="card" href="b07.html"><span class="no">B7</span>
    <div class="t">AI / ML / 深度学习的关系</div>
    <div class="d">它们不是并列关系，是包含关系。一图看清。</div>
    <span class="tag">选读 · 理清名词</span></a>
  <a class="card" href="b08.html"><span class="no">B8</span>
    <div class="t">怎么判断模型好不好</div>
    <div class="d">排序准 ≠ 数字准。这是全库最容易被忽略的一条。</div>
    <span class="tag anim">必读 · 决定后面能不能看懂</span></a>
  <a class="card" href="b09.html"><span class="no">B9</span>
    <div class="t">学习地图 · 门路推荐</div>
    <div class="d">想继续往下学，书、课、文档该从哪儿入手。</div>
    <span class="tag">选读 · 指路</span></a>
  <a class="card" href="b10.html"><span class="no">B10</span>
    <div class="t">端到端：从问题定义到落地</div>
    <div class="d">七个步骤串成一条线，每一步都点得开真实代码。</div>
    <span class="tag anim">必读 · 想亲手跑一遍就看这页</span></a>
  <a class="card" href="b11.html"><span class="no">B11</span>
    <div class="t">算法怎么分：先按任务分</div>
    <div class="d">回归 / 分类 / 聚类 / 降维，四格图一次分清。</div>
    <span class="tag">理清名词</span></a>
  <a class="card" href="b12.html"><span class="no">B12</span>
    <div class="t">遇到问题该选哪类模型</div>
    <div class="d">三个问题走完决策路径，不用再靠猜。</div>
    <span class="tag">能直接用</span></a>
  <a class="card" href="b13.html"><span class="no">B13</span>
    <div class="t">最常见的六个误区</div>
    <div class="d">六句听着都对、做就错的念头，本案例基本全踩过。</div>
    <span class="tag">避坑</span></a>
  <a class="card" href="b14.html"><span class="no">B14</span>
    <div class="t">模型是怎么被教会的一趟下山路</div>
    <div class="d">损失 → 梯度 → 什么时候停，一条主线讲透。</div>
    <span class="tag">选读 · 想懂原理</span></a>
  <a class="card" href="b09.html"><span class="no">B9</span>
    <div class="t">学习地图 · 门路推荐</div>
    <div class="d">想继续往下学，书、课、文档该从哪儿入手。</div>
    <span class="tag">选读 · 指路</span></a>
  <a class="card" href="b10.html"><span class="no">B10</span>
    <div class="t">端到端：从问题定义到落地</div>
    <div class="d">七个步骤串成一条线，每一步都点得开真实代码。</div>
    <span class="tag anim">必读 · 想亲手跑一遍就看这页</span></a>
  <a class="card" href="b11.html"><span class="no">B11</span>
    <div class="t">算法怎么分：先按任务分</div>
    <div class="d">回归 / 分类 / 聚类 / 降维，四格图一次分清。</div>
    <span class="tag">理清名词</span></a>
  <a class="card" href="b12.html"><span class="no">B12</span>
    <div class="t">遇到问题该选哪类模型</div>
    <div class="d">三个问题走完决策路径，不用再靠猜。</div>
    <span class="tag">能直接用</span></a>
  <a class="card" href="b13.html"><span class="no">B13</span>
    <div class="t">最常见的六个误区</div>
    <div class="d">六句听着都对、做就错的念头，本案例基本全踩过。</div>
    <span class="tag">避坑</span></a>
  <a class="card" href="b14.html"><span class="no">B14</span>
    <div class="t">模型是怎么被教会的一趟下山路</div>
    <div class="d">损失 → 梯度 → 什么时候停，一条主线讲透。</div>
    <span class="tag">选读 · 想懂原理</span></a>
</div>

<h2>四个数字，先记住</h2>
<div class="stat-grid">
  <div class="stat"><div class="v">{F['n_wrongly_killed']:,}<small> 件</small></div>
    <div class="k">被冤枉的好司机<br>占拒保件的 {F['pct_killed_of_rej']}%</div></div>
  <div class="stat"><div class="v">{F['kill_by_channel'][2]['kill_rate']}<small>%</small></div>
    <div class="k">线上渠道错杀率<br>是代理渠道的 {F['kill_ratio_online_vs_agent']} 倍</div></div>
  <div class="stat"><div class="v">{F['interp']['A']['auc']}</div>
    <div class="k">模型排序能力 AUC<br>0.5 = 瞎猜，1.0 = 完美</div></div>
  <div class="stat"><div class="v">{F['thr_peak_gain']/10000:,.0f}<small> 万元</small></div>
    <div class="k">选对圈选阈值时<br>比随机多赚的钱（年）</div></div>
</div>

<h2>四条路线，挑一条走</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>如果你……</th><th>走这条线</th><th>花多久</th></tr>
<tr><td><b>只想搞明白大概</b></td>
    <td><a href="b01.html">B1</a> → <a href="b02.html">B2</a> →
        <a href="index.html#map">看一眼地图</a> →
        <a href="ch10.html">第 32 页（圈谁最划算）</a></td><td>20 分钟</td></tr>
<tr><td><b>想学会判断模型靠不靠谱</b></td>
    <td><a href="b03.html">B3</a> <a href="b04.html">B4</a> <a href="b05.html">B5</a>
        <a href="b08.html">B8</a> → <a href="ch04.html">26</a>
        <a href="ch05.html">27</a> <a href="ch06.html">28</a> 三套动画 →
        <a href="ch09.html">第 31 页（外推风险）</a></td><td>1 小时</td></tr>
<tr><td><b>想亲手跑一遍</b></td>
    <td><a href="b10.html">B10 端到端七步</a>（每步点得开真实代码）→
        <a href="m01.html">模型速查</a> / <a href="a01.html">算法速查</a> →
        照 <a href="b10.html#repro">一键复现</a> 的命令跑一遍</td><td>2 小时</td></tr>
<tr><td><b>要把它落到业务上</b></td>
    <td>全部基础篇 → 全部正文 →
        <a href="ch10.html">32</a> <a href="ch11.html">33</a>
        <a href="ch13.html">35</a>，重点看清单怎么用</td><td>半天</td></tr>
</table></div>

<h2 id="map">完整地图：你会经历什么</h2>
<p>这不是一份「机器学习入门讲义」。它是<b>一次完整的实战</b>：
从一个你每天都在做的动作（核保规则把一批人拒了）出发，
一直走到能把模型变成钱的业务账。每个概念都挂在这个案例上，不悬空。</p>
<div class="card-grid">
  <a class="card" href="ch01.html"><span class="no">第一部分 · 翻译</span>
    <div class="t">把业务问题翻译给机器</div>
    <div class="d">从你天天在用的 GLM 出发；搞清「−1 不是 0」；学会把纯保费拆成频率×损失。</div>
    <span class="tag">01 – 03</span></a>
  <a class="card" href="ch04.html"><span class="no">第二部分 · 直觉</span>
    <div class="t">看着模型一点点学会</div>
    <div class="d">三套可交互动画：GLM 怎么迭代、决策树怎么挑问题、GBDT 怎么逐轮补差。</div>
    <span class="tag anim">04 – 06 · 含动画</span></a>
  <a class="card" href="ch07.html"><span class="no">第三部分 · 防骗</span>
    <div class="t">模型会在哪里骗你</div>
    <div class="d">审计样本的坑、IPW 与双重稳健、以及「外推」这个最隐蔽的翻车点。</div>
    <span class="tag">07 – 09</span></a>
  <a class="card" href="ch10.html"><span class="no">第四部分 · 变现</span>
    <div class="t">把模型换成钱</div>
    <div class="d">倒 U 曲线回答「圈谁最划算」；以及「B 看起来更好」是怎么骗过所有人的。</div>
    <span class="tag">10 – 11</span></a>
  <a class="card" href="ch12.html"><span class="no">第五部分 · 走通</span>
    <div class="t">端到端复盘与落地</div>
    <div class="d">八步流水线每一步的「为什么」；一张可以直接交给同事复核的清单怎么用。</div>
    <span class="tag">12 – 13</span></a>
</div>

<h2>要拿去汇报？先读这七页</h2>
<div class="note red"><b>前面所有页面回答的是「怎么做」，这七页回答的是「要不要做」。</b>
决策会上必被问到的四件事——现在在干嘛、不用模型行不行、要花多少钱、上线之后谁管——都在这里。</div>
<div class="card-grid">
  <a class="card" href="s01.html"><span class="no">S1</span>
    <div class="t">当下是怎么做的</div>
    <div class="d">规则引擎 / 申诉复议 / 合规抽检三条腿，以及为什么看不见自己错了。</div>
    <span class="tag">立项理由</span></a>
  <a class="card" href="s02.html"><span class="no">S2</span>
    <div class="t">不用机器学习行不行</div>
    <div class="d">五条路摆在一起比。机器学习是排队机，不是裁判。</div>
    <span class="tag anim">必读 · 最值钱的一页</span></a>
  <a class="card" href="s03.html"><span class="no">S3</span>
    <div class="t">投入产出账</div>
    <div class="d">成本侧补上，填一个数就能算的测算器。</div>
    <span class="tag anim">必读 · 盈亏平衡点</span></a>
  <a class="card" href="s04.html"><span class="no">S4</span>
    <div class="t">上线之后</div>
    <div class="d">监控 / 灰度 / 重训 / 下线条件 / 三道防线。</div>
    <span class="tag">运营机制</span></a>
  <a class="card" href="s05.html"><span class="no">S5</span>
    <div class="t">四种范式：从预测到决策</div>
    <div class="d">预测 / 因果 / 运筹 / 实验——能做实验时别用模型。</div>
    <span class="tag">升维</span></a>
  <a class="card" href="s06.html"><span class="no">S6</span>
    <div class="t">组织与分工</div>
    <div class="d">精算 / 数据 / 核保 / IT / 合规各干什么，最容易卡在哪。</div>
    <span class="tag">谁来干</span></a>
  <a class="card" href="s07.html"><span class="no">S7</span>
    <div class="t">三十秒版本</div>
    <div class="d">电梯演讲 + 分对象讲法 + 六问六答，可直接拿去汇报。</div>
    <span class="tag">汇报用</span></a>
</div>

<h2>三张随查随用的表</h2>
<div class="card-grid">
  <a class="card" href="m01.html"><span class="no">M</span>
    <div class="t">常见模型速查</div>
    <div class="d">12 个模型：是什么、什么时候用、数学表达、配图、Python 代码（点开即展开）。</div>
    <span class="tag">12 个模型</span></a>
  <a class="card" href="a01.html"><span class="no">A</span>
    <div class="t">常见算法速查</div>
    <div class="d">13 个算法：怎么把模型「算出来」的那套办法，同样配图配代码。</div>
    <span class="tag">13 个算法</span></a>
  <a class="card" href="glossary.html"><span class="no">G</span>
    <div class="t">术语表 · 中英双语</div>
    <div class="d">一句话大白话 + 一个生活类比，可实时搜索。</div>
    <span class="tag">可搜索</span></a>
</div>

<h2>看不懂的词怎么办</h2>
<div class="note"><b>左边每页顶部都有两块「护身符」：</b>上面一块用大白话告诉你这页在讲什么、
读完你会知道什么；下面一块列出这页会遇到的词，配一句话解释，点一下能跳到完整术语表。<br><br>
另外，<a href="glossary.html"><b>术语表</b></a>收录了全部 {len(TERMS)} 个词，
<b>中英双语 + 一句话大白话 + 一个生活类比</b>，还能实时搜索。
遇到 IPW、GBDT、IRLS 这类缩写，直接去那里查。</div>

<h2>开工之前，三句丑话说在前面</h2>
<div class="note red"><b>数据是模拟的。</b>案例里的 {F['n_total']:,} 个司机由 <code>gen_data.py</code> 生成——
这不是缺陷，是特性：只有模拟器才知道每个人的「真实风险」，我们才能公平地评判模型有没有找错人。
真实业务里你永远拿不到这份「标准答案」。</div>
<div class="note"><b>Tweedie 回归只讲了思路、没有实现。</b>正文里的第三层建模路线是「频率×损失拆解」，
更高级的 Tweedie 一步到位方案，我们在 <a href="ch03.html">第 25 页</a>明确标注为「未实现，留作练习」。</div>
<div class="note"><b>所有模型都是手写的 NumPy。</b>不是因为我们清高，是因为 scikit-learn 在这台机器上被
安全策略拦了。因祸得福：你能看见每一行数学，而不是调包。</div>

<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>如果你只有十分钟：直接跳到 <a href="ch10.html">第 32 页</a>（圈谁最划算）和
<a href="ch11.html">第 33 页</a>（「看起来更好」的陷阱）。前者回答钱的问题，后者回答
「为什么你办公室里那个用旧指标的人可能会骗你」。</p></div>
<div class="quote q-warn"><span class="q-tag">特别提醒</span>
<p>本库的每一张表、每一个数字，都来自 <code>out/facts.json</code> 这一份文件——
它由 <code>code/_facts.py</code> 自动从运行日志和产物 CSV 中抽取。如果你在别处看到与本库
不同的数字，请以 facts.json 为准。</p></div>
"""


# ================================================================ 01 GLM
def p_ch01(F):
    return f"""
<h1><span class="thin">第一部分 · 把问题翻译给机器 · 01</span>
从你熟悉的 GLM 出发</h1>
<p class="lead">先说一个可能让你意外的事实：<b>你已经会机器学习了。</b>
你上个月做费率因子的时候，用的就是它——只不过你们管它叫 GLM，
隔壁互联网公司管它叫「逻辑回归模型」。</p>

{_step_frame(
  "把你天天在做的 GLM 费率因子，翻译成机器学习的语言，看清「系数」和「特征权重」其实是同一个东西。",
  "一个能用「训练集 / 测试集」分开评价的 Poisson GLM 频率模型（核心代码就在 models.py，不到 30 行）。",
  "重点看左右两栏公式哪里相等；并记牢机器学习加的第一条铁律：考试不许考原题——训练集上漂亮不算数。")}

<h2 id="same">同一个公式，两种行话</h2>
<p>车险定价里你写过无数次这个式子：</p>
<div class="fx">风险 = 基准风险 × 年龄因子 × 车型因子 × 区域因子 × …
<small>精算行话：乘法费率模型，因子通过边际分析 + 判断法确定</small></div>
<p>机器学习里它长这样：</p>
<div class="fx">log(E[出险次数 | x]) = β₀ + β₁·年龄 + β₂·车型 + β₃·区域 + …
<small>机器学习行话：Poisson 回归，系数通过「最小化损失函数」自动算出</small></div>
<p>两边取个指数，机器学习的式子就变成了你的式子：<b>exp(β₁) 就是年龄因子，就是相对风险 RR。</b>
不是类比，是同一个东西。</p>
<div class="explain">唯一真正的区别在于「系数怎么来」：你的流程是人先挑变量、再拟合、再看显著性、
凭经验调整；机器学习的流程是机器在同一个框架里自动搜索，再用一套统一的分数（损失函数）评价好坏。
工具一样，工作流不一样。</div>

{_why("为什么必须是对数连接？不写 log 行不行？",
      "要预测的出险次数 λ 必须大于 0，而右边那个线性组合可以取任意负数——"
      "直接连会算出「负的出险次数」，没有意义。对数把「正数」映射到「任意实数」，"
      "怎么加都不会跑出正数轴。",
      "λ(x) = exp(β₀ + β₁x₁ + β₂x₂ + …) = e^{β₀} · e^{β₁x₁} · e^{β₂x₂} · …",
      [("λ(x)", "这个人的期望出险次数，必须 &gt; 0"),
       ("β₀", "基准水平，取指数后就是基准风险"),
       ("β₁…", "各特征的系数，取指数后就是相对风险 RR")],
      "取指数之后，加法变回乘法——这就是你写了无数遍的乘法费率模型。"
      "所以 exp(β₁) 就是年龄因子：不是类比，是同一个东西。")}

{_toc([("train-test", "先记住一条考场规则"), ("hand", "手写一遍 GLM"), ("ceiling", "GLM 的天花板")])}

<h2 id="train-test">机器学习加的第一条规矩：考试不许考原题</h2>
<p>你以前拟合 GLM，是拿全部数据拟合、全部数据出表——没人管这个模型「遇到陌生人」会怎样。
机器学习把这件事变成了铁律：</p>
<div class="steps">
  <div class="step"><h4>训练集 —— 平时的作业题</h4>
    <p>本案例 11,200 个已承保客户中留 {F['n_train']:,} 件给机器找系数。</p></div>
  <div class="step"><h4>测试集 —— 期末考试</h4>
    <p>剩下 {F['n_test']:,} 件封存，模型练完才准碰。考试分数（测试 AUC）才算数。</p></div>
  <div class="step"><h4>过拟合 —— 背题背出来的好学生</h4>
    <p>训练分数很高、考试崩掉，就是过拟合。GLM 因为形态简单，几乎不会过拟合——
    本案例三个模型训练→测试的衰减全部在 ±2% 以内，包括那个学习率最快的 GBDT。</p></div>
</div>
<div class="tbl-wrap"><table class="tbl">
<tr><th>模型</th><th class="num">训练 AUC</th><th class="num">测试 AUC</th><th class="num">衰减</th></tr>
{''.join(f'<tr><td>{o["name"]}</td><td class="num">{o["train"]:.3f}</td><td class="num">{o["test"]:.3f}</td><td class="num">{o["decay"]:+.1f}%</td></tr>' for o in F['overfit'])}
</table></div>
<div class="tbl-cap">训练—测试对照（承保人群）。衰减极小：这个案例的问题从来不是「模型背题」，后面你会看到，真正的坑在别处。</div>
{_fig('fig2_07_overfit.png','训练集与测试集的 AUC 几乎重合。如果哪天你看到一个模型这两根柱子差得很远，先别看它的宣传页，先怀疑它在背题。')}

<h2 id="hand">手写一遍 GLM：IRLS 到底在转什么</h2>
<p>Poisson 回归的求解器叫 IRLS（迭代重加权最小二乘），名字吓人，动作只有三步：</p>
<div class="fx">① 用当前系数猜一遍：μᵢ = exp(β₀ + β₁xᵢ)　　② 看差距：zᵢ = ηᵢ + (yᵢ − μᵢ)/μᵢ　　③ 带权回归一遍更新系数
<small>重复 ①②③ 直到系数几乎不动（收敛）。<a href="ch04.html">第 26 页的动画</a>会把这三步逐步演给你看</small></div>
<p>本库的 <code>models.py</code> 里，这 30 行就是全部——没有 sklearn：</p>
<pre><code><span class="cm"># Poisson IRLS 的核心循环（models.py 摘录）</span>
for it <span class="kw">in</span> range(max_iter):
    mu    = np.exp(np.clip(X @ beta, -8, 8))       <span class="cm"># ① 猜</span>
    z     = eta + (y - mu) / mu                    <span class="cm"># ② 差距 → 工作响应</span>
    W     = mu                                     <span class="cm"># Poisson 的权重就是 mu</span>
    beta  = solve(X.T @ (W[:,None]*X), X.T @ (W*z)) <span class="cm"># ③ 加权最小二乘</span>
    <span class="kw">if</span> np.max(np.abs(beta - beta_old)) &lt; tol: <span class="kw">break</span></code></pre>
<div class="explain">两个细节值得停一下：<b>对数链接</b>保证预测永远为正（保费不能是负数）；
<b>权重 W = μ</b> 意味着模型自动更在乎「高风险的人」——他们预测错一个，代价更大。</div>

{_why("IRLS 和牛顿法是什么关系？为什么它比梯度下降快？",
      "牛顿法的思路是「用二阶导数决定往哪走、走多快」。泊松对数连接下，"
      "每一步的二阶信息刚好等价于「用权重 μ 做一次加权最小二乘」——"
      "所以 IRLS 不是另一套方法，就是牛顿法换了个写法。",
      "β<sup>(t+1)</sup> = β<sup>(t)</sup> − H<sup>−1</sup> · ∇ℓ( β<sup>(t)</sup> )　　其中 H = XᵀWX，W = diag(μ)",
      [("∇ℓ", "损失函数的一阶导数（梯度）：往哪个方向走"),
       ("H", "二阶导数（Hessian）：路有多弯，决定步长"),
       ("W", "权重矩阵，Poisson 下正好等于 μ")],
      "因为它用了曲率信息（H），所以收敛比普通梯度下降快得多——"
      "代价是每轮要解一个线性方程组，样本很大时会慢。")}

<h2 id="ceiling">GLM 的天花板：它只会画直线</h2>
<p>GLM 学到的东西永远是「每个变量乘一个固定系数」。年龄每涨一岁，风险永远降同样的百分比。
但真实世界里的规律常常是弯的、是拐弯的、是「35 岁以下风险陡增，以上平坦」的。
GLM 想拟合拐弯，你得自己动手造交互项、造分段——造不造，全凭人的经验。</p>
<p>而决策树和 GBDT 会<b>自己从数据里找出拐点</b>。这正是第二部分要演给你看的。</p>

<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>机器学习没有把你的 GLM 扔掉。<b>它只是给你的老工具加了三个新习惯：留考卷、统一打分、
以及允许模型自己找拐弯。</b></p></div>
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>下次有人跟你汇报「我们上了机器学习定价模型」，第一个问题就问：<b>「训练集和测试集是怎么切的？」</b>
答不上来的，大概率是把作业题当考卷用了——数字漂亮，一上线就露馅。</p></div>
<div class="quote q-warn"><span class="q-tag">特别提醒</span>
<p>AUC 这个词在这一页还只是「排序能力」的代号。记住一个反直觉的点：
本案例的模型要找的是<b>风险最低</b>的人，所以打分时用的是 <b>−预测值</b>。
方向搞反，你会得出「模型比乱猜还差」的结论——我们自己就踩过这个坑，测试集 AUC 一度算出 0.4。</p></div>
"""


# ================================================================ 02 标签不可见
def p_ch02(F):
    return f"""
<h1><span class="thin">第一部分 · 把问题翻译给机器 · 02</span>
标签不可见：−1 不是 0</h1>
<p class="lead">整个案例最值钱的一个字符，是一个负号。<b>被拒保的人，出险次数记作 −1——
意思是「没有记录」，而不是「零出险」。</b>看懂这一行，你就看懂了保险行业里机器学习
最特殊的一道坎。</p>

{_step_frame(
  "说清为什么被拒保的人没有标签，以及数据库里的 −1 到底是什么意思。",
  "一个「可计算的好司机定义」（真实期望纯保费 ≤ 承保人群中位数），和一条红线：−1 绝不能被当成 0。",
  "记住一句话——模型只用承保人群训练，却要给从没见过的人打分，这才是整个案例真正的难处。")}

<h2 id="shadow">阴影下的 8,800 人</h2>
<p>先看清我们手里有什么：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>人群</th><th class="num">人数</th><th>出险记录</th><th>机器能学到什么</th></tr>
<tr><td>已承保</td><td class="num">{F['n_acc']:,}</td>
  <td>有：真实出险次数与金额</td><td class="good">一切照旧——这就是训练集</td></tr>
<tr><td>被拒保</td><td class="num">{F['n_rej']:,}</td>
  <td><span class="hl">没有：</span>数据库里记作 −1 / 空值</td>
  <td><span class="hl">什么也学不到——但模型偏要给他们打分</span></td></tr>
</table></div>
<p>问题来了：模型是靠「出险记录」学会估价的。可被拒保的人恰恰<b>因为被拒了所以没有记录</b>。
这就好比你让一个只见过白天行人的交警，去给夜路定规矩。</p>

<div class="quote q-warn"><span class="q-tag">特别提醒 · 本库最容易翻车的一步</span>
<p>如果把 −1 当成 0 喂给模型，等于告诉它：<b>「这 8,800 个人都没出过险，都是天使。」</b>
模型会立刻学出「拒保人群零风险」——然后建议你把他们的保费降到底。
这不是 hypothetical（假设），这是数据清洗里真实发生过的错误，而且极难被发现：
因为输出看起来「很合理」——数字都挺小、没有报错、报表美观。</p></div>

<h2 id="label">把「好司机」变成一个机器能算的东西</h2>
<p>业务上你说「找出被错杀的好司机」。机器听不懂「错杀」和「好」。
翻译工作分三步，每一步都是一次立场声明：</p>
<div class="steps">
  <div class="step"><h4>「好」的标准是什么？</h4>
    <p>我们定义为：<b>真实期望纯保费 ≤ 承保人群的中位数（{F['good_threshold']:,.0f} 元）</b>。
    意思是「如果当初放他进来，他的成本不比现有客户的中位数差」。
    这是一个可以辩护的业务标准，而不是拍脑袋。</p></div>
  <div class="step"><h4>「真实」从哪来？</h4>
    <p>承保客户有真实赔款，可以直接算；被拒保客户的真实赔款只有<b>模拟器知道</b>
    （本库专门造了这份「上帝视角」字段 <code>_true_premium</code>）。
    现实业务里你拿不到它——所以后面第 07、08 页专门讲「拿不到的时候怎么办」。</p></div>
  <div class="step"><h4>「错杀」于是有了精确定义</h4>
    <p>真实期望纯保费 ≤ {F['good_threshold']:,.0f} 元、却被规则拒掉的人。
    按这个定义，8,800 件拒保件里藏着 <b>{F['n_wrongly_killed']:,} 件错杀</b>
    ——占拒保件的 {F['pct_killed_of_rej']}%，占全部申请的 {F['pct_killed_of_all']}%。</p></div>
</div>
{_fig('fig2_01_dist.png','承保与拒保人群的真实风险分布。拒保人群整体确实更贵（均值 '+f"{F['true_prem_rej']:,.0f}"+' 元 vs '+f"{F['true_prem_acc']:,.0f}"+' 元）——均值会骗人，但左边的绿色区域不会：那里躺着 '+f"{F['n_wrongly_killed']:,}"+' 个比中位数还便宜的人。')}
<div class="explain">注意一个容易被带偏的争论：「拒保人群整体更贵，说明规则拒得对啊！」
——这句话犯了「用平均数审判个人」的错误。规则的任务从来不是「平均地拒」，而是「该拒的拒、不该拒的留」。
分布重叠的那一块，才是规则真正犯错的地方。</div>

<h2 id="p10">一个意外友好的发现</h2>
<p>拒保人群真实纯保费的十分位数：<b>P10 = {F['rej_p10']:,.0f} 元，P50 = {F['rej_p50']:,.0f} 元，
P90 = {F['rej_p90']:,.0f} 元</b>。承保人群的中位数（{F['good_threshold']:,.0f} 元）
落在 P10 和 P50 之间——这意味着被拒的人群里，至少有一成的人比现有客户的一半还要好。
<b>「有梯度、有重叠」是整个案例能成立的前提。</b>如果拒保的人清一色是坏风险，
那规则就没有偏见、模型也没有用武之地——那种数据也值得警惕：它可能是被「修」出来的。</p>

<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>机器学习的第一课不是算法，是老实：<b>模型只能学「看得见的标签」；
看不见的那群人，才是你要用全部智慧去对待的。</b></p></div>
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>凡是「模型要给没经历过结果的人群打分」的项目——拒保件复核、新渠道客群、新地区拓客——
都自带这一页的问题。立项书里如果没人回答「标签从哪来」，这个项目八成会在半年后
无声无息地死掉，而且死前一直在出「看起来很美」的报表。</p></div>
"""


# ================================================================ 03 频率×损失
def p_ch03(F):
    _maxp = max(c["purity"] for c in F["combos"])
    _combo_rows = "".join(
        f'<tr><td>{c["name"]}</td><td class="num">{c["auc"]:.3f}</td>'
        f'<td class="num{" hl" if c["purity"] == _maxp else ""}">{c["purity"]}%</td>'
        f'<td class="num">{c["dev"]:+.1f}%</td></tr>'
        for c in F["combos"])
    # 「圈最便宜 20% 里好司机占几成」示意图：左 20% 高亮为被圈出，绿满程度 = 纯度
    _seg = 120
    _green = _seg * F["interp"]["A"]["purity"] / 100.0
    purity_inner = f"""
<text x="322" y="30" font-size="12" fill="#8a8578" text-anchor="middle">按模型预测从「最便宜」排到「最贵」→</text>
<rect x="20" y="46" width="604" height="34" rx="6" fill="#efe9d8"/>
<rect x="20" y="46" width="{_seg}" height="34" rx="6" fill="#2f6b5a" opacity="0.16" stroke="#2f6b5a"/>
<rect x="20" y="46" width="{_green:.0f}" height="34" fill="#2f6b5a" opacity="0.55"/>
<text x="80" y="98" font-size="11.5" fill="#2f6b5a" text-anchor="middle">← 左 20% 是被圈出的人</text>
<text x="80" y="114" font-size="11.5" fill="#8a8578" text-anchor="middle">其中真正好司机占 {F['interp']['A']['purity']}%</text>
<text x="430" y="68" font-size="12" fill="#8a8578" text-anchor="middle">右边 80% 没被圈</text>
"""
    return f"""
<h1><span class="thin">第一部分 · 把问题翻译给机器 · 03</span>
频率 × 损失：拆开再拼</h1>
<p class="lead">模型第一次上场就摔了一跤：直接用纯保费建模，效果<b>和闭着眼睛猜差不多</b>。
这一页讲它为什么摔、以及精算人的老本行怎么救场。</p>

{_step_frame(
  "说清为什么直接拿纯保费建模会失败，并演示怎么用「出险频率 × 案均损失」拆开救场。",
  "三个组合方案在测试集上的对比表——排序能力、圈选纯度、校准偏差各占一列。",
  "表头那三个词别混着看；本页配了一张图专门讲「圈最便宜 20% 里好司机占几成」到底是什么意思。")}

<h2 id="wall">先看一次诚实的失败</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>直接对纯保费建模</th><th class="num">测试集 deviance</th><th class="num">相对「闭眼猜」</th></tr>
{''.join(f'<tr><td>{d["name"]}</td><td class="num">{d["dev"]:,.0f}</td><td class="num{" hl" if d["pct"]>100 else ""}">{d["pct"]:.1f}%</td></tr>' for d in F['dev_wall'])}
</table></div>
<div class="tbl-cap">「闭眼猜」= 常数基线：预测所有人都等于平均值，deviance {F['dev_wall'][0]['dev']:,.0f}。</div>
<p>Poisson GLM 是常数基线的 {F['dev_wall'][1]['pct']:.1f}%，GBDT 是 {F['dev_wall'][2]['pct']:.1f}%
——<b>不但没赢，还微弱地输了。</b>两个模型、两种完全不同的数学，输得整整齐齐。
这说明输的不是模型，是<b>考卷出错了</b>。</p>

<h2 id="why">考卷错在哪：零膨胀 + 重尾</h2>
<p>纯保费这个变量长得非常恶劣：</p>
<div class="steps">
  <div class="step"><h4>一大半是 0</h4>
    <p>多数人全年不出险，纯保费 = 0。模型在这片 0 的海洋里学不到任何梯度。</p></div>
  <div class="step"><h4>极少数巨灾大得离谱</h4>
    <p>本数据里有单笔十几万的赔款——一个人一年吃掉几千个人的保费。
    deviance 对这种点极其敏感：模型为了拉平这一个点，会把其他 19,999 个人全都带偏。</p></div>
  <div class="step"><h4>而巨灾本来就不可能被预测</h4>
    <p>谁在哪个雨夜追尾谁，本质是随机事件。要求模型预测它，等于要求天气预报报出
    「哪片雪花先落地」。</p></div>
</div>
<div class="note red">这一课是全库最重要的一课的下半句：<b>第 23 页说「模型没坏，是尺子不对」；
这一页补全——尺子不对的根源，是变量本身由两种完全不同的机制混合而成。</b></div>

<h2 id="split">精算人的本能：拆</h2>
<p>你其实早就知道答案。精算定价从来不是一个公式算到底，而是：</p>
<div class="fx">纯保费 = 出险频率 × 案均损失
<small>频率：一年出几次险 → 计数问题，用 Poisson 建模，天生对口</small></div>
<p>拆开之后，每一段都用<b>合适的尺子</b>单独考核：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>组件</th><th>数据的毛病</th><th>正确的尺子</th></tr>
<tr><td>频率（出险次数）</td><td>计数、0 多但不极端</td>
  <td class="good">Poisson deviance —— 只在有出险的样本上才说话</td></tr>
<tr><td>案均损失（赔款金额）</td><td>重尾、右偏、巨灾</td>
  <td class="good">先取 log 再算 MSE —— 巨灾从「绑架指标」降级为「一个较大的数」</td></tr>
</table></div>
<p>三个组合方案，在我们已经承保、机器见过的那批人（专业说法叫「内插域」）身上一较高下：</p>
{_svg(644, 140, purity_inner, "横轴是按模型预测从最便宜排到最贵。左边高亮 20% 就是「被圈出的最便宜的人」；这一格里绿色越满，说明真正好司机占比（纯度）越高。")}
<div class="tbl-wrap"><table class="tbl">
<tr><th>组合</th><th class="num">AUC</th><th class="num">圈最便宜20%里好司机占比</th><th class="num">均值偏差</th></tr>
{''.join(_combo_rows)}
</table></div>
<div class="tbl-cap">「圈最便宜 20% 里好司机占比」= 把模型认为最便宜的 20% 圈出来，里面真正好司机占几成（就是纯度）；「均值偏差」= 模型平均预测值相对真实均值的偏离，衡量它报价准不准。两个指标一个看排序、一个看报价，别混着看。</div>
<p>三个信息值得划线：</p>
<p><b>一，组合①和②的均值偏差约 −31%。</b>频率模型 × 损失单树，排序还行（AUC 0.75），
但整体估价比真实低了三成——<b>「排得准」和「报得准」是两种能力</b>，在这个业务里后者同样要命。</p>
<p><b>二，组合③赢了，而且赢得有点尴尬。</b>它的「损失模型」干脆就是一个常数（承保人群的案均损失均值）——
没训练任何损失形状，反而校准最好（−0.8%）。因为在「圈最便宜 20%」这个任务里，
<b>排名主要靠频率端驱动</b>，损失端只要不添乱就行。单棵树学损失反而引入噪声。</p>
<p><b>三，这再次验证了第 23 页的钩子：</b>组合②（GBDT 频率）还不如组合①（GLM 频率），
因为这个案例的真实规律恰好接近线性。模型不天然越复杂越好——
<b>「合适的模型」打败「更先进的模型」。</b></p>

{_why("为什么一定要拆成「频率 × 案均」？一步建模到底差在哪？",
      "一步建模等于要求<b>一个分布同时长成两种形状</b>：出险次数是零膨胀的"
      "（大多数人一次都不出，全是 0），案均损失是重尾的（少数个案金额极大）。"
      "一个 Poisson 分布两头都要顾，结果两头都不像。拆开后各用各的分布，就顺了。",
      "纯保费 = E[N] × E[S | N &gt; 0] = λ × m",
      [("N", "出险次数，零膨胀 → 用 Poisson / 负二项"),
       ("S", "单次案均损失，重尾 → 用 Gamma"),
       ("λ, m", "频率与案均，各自单独建模")],
      "本案例实测：直接建纯保费的 Poisson GLM，deviance 只到常数基线的 "
      f'{F["dev_wall"][1]["pct"]}%（等于没学到东西）；拆开成两步后 deviance 再降 {abs(F["combos"][0]["dev"])}%。'
      "这就是「拆」的全部理由——不是玄学，是实测出来的。")}

<h2 id="tweedie">没做完的部分：Tweedie（诚实声明）</h2>
<div class="note"><b>本库没有实现真正的 Tweedie 回归。</b>它是把「频率×损失」一步到位的优雅方案
（Tweedie P∈(1,2)，P→1.5 时恰好是「复合 Poisson-伽马」分布）。
两条路径是等价的：要么用本库的拆解法（可解释、可分组件考核），
要么用 Tweedie（一个公式、但对实现的要求高得多）。
<b>本案例选拆解不是偷懒</b>：要的是「圈出最便宜的 20%」，看重排序与分组件考核，
而拆解法在强监管下更容易解释给核保和合规听。这里明确留作练习，
不假装它存在——你在别处读到「一行代码搞定零膨胀重尾」时，请先问一句：巨灾样本进去，deviance 还是稳定的吗？</div>

<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>模型第一次失败，不是因为它笨，是因为<b>你让它一口气回答了两个不同的问题：
「他会不会出事」和「出了事多严重」。</b>拆开来问，两个都答得很好。</p></div>
<div class="quote q-mgmt"><span class="q-tag">管理启示</span>
<p>评审模型时，别只问「准不准」，要问三个问题：<b>排序准吗（AUC / 纯度）？校准准吗（均值偏差）？
尺子是不是被少数极端值绑架了？</b>三个答案齐了，这个模型才算被「看懂」过。</p></div>
<div class="quote q-warn"><span class="q-tag">特别提醒</span>
<p>组合③「损失端用常数」是本案例的最优解，但它是<b>这个任务</b>（圈最便宜 20%）的最优解。
如果你的任务是给每张保单精确定价，损失端偷懒会让价格失去区分度。
结论永远跟着任务走，没有万能模型。</p></div>
"""


PAGES_A = [
    ("index", "00", "总览 · 学习地图", p_index),
    ("ch01", "01", "从你熟悉的 GLM 出发", p_ch01),
    ("ch02", "02", "标签不可见：−1 不是 0", p_ch02),
    ("ch03", "03", "频率 × 损失：拆开再拼", p_ch03),
]
