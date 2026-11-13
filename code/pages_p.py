# -*- coding: utf-8 -*-
"""AI 实践库 · P01「把业务问题翻译成可计算的问题」

端到端流程里最容易翻车、又最少有人讲的一步：业务诉求是模糊的，
机器学习要的是精确定义。中间那一步叫「翻译」，绝大多数失败发生在这一步。

这一页不写代码、不训练模型，只回答一件事：
一个含糊的业务诉求，怎么变成一道机器能算的题。
"""

from pages_a import _toc, _step_frame
from pages_basics import (_svg, _cmp_table, _three, _why,
                          INK, GREY, RED, JADE, AMBER, LINE)


def _map_svg():
    """翻译示意图：业务诉求 → 问清四件事 → 机器学习问题。"""
    def box(x, y, w, h, fill, stroke):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')

    def arrow(x1, x2, y):
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{RED}" '
                f'stroke-width="2"/><path d="M{x2} {y} L{x2-8} {y-5} '
                f'L{x2-8} {y+5} Z" fill="{RED}"/>')

    c = []
    # 左：业务诉求
    c.append(box(10, 70, 186, 100, "#fbf8ef", LINE))
    c.append(f'<text x="103" y="94" font-size="13" font-weight="bold" '
             f'fill="{INK}" text-anchor="middle">业务诉求</text>')
    c.append(f'<text x="103" y="118" font-size="12" fill="{INK}" '
             f'text-anchor="middle">「规则误杀了好人」</text>')
    c.append(f'<text x="103" y="140" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">模糊 · 无从下手</text>')
    c.append(f'<text x="103" y="156" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">不知道从哪算起</text>')
    c.append(arrow(198, 226, 120))

    # 中：翻译
    c.append(box(230, 42, 200, 156, "#fff", RED))
    c.append(f'<text x="330" y="66" font-size="13" font-weight="bold" '
             f'fill="{RED}" text-anchor="middle">翻译：问清四件事</text>')
    for i, t in enumerate(["① 输入 X 是什么", "② 输出 y 是什么",
                           "③ 怎么算成功", "④ 然后谁做什么"]):
        yy = 92 + i * 25
        c.append(f'<rect x="248" y="{yy-14}" width="164" height="21" rx="5" '
                 f'fill="#fbf8ef" stroke="{LINE}"/>')
        c.append(f'<text x="330" y="{yy+1}" font-size="12" fill="{INK}" '
                 f'text-anchor="middle">{t}</text>')
    c.append(arrow(432, 456, 120))

    # 右：机器学习问题
    c.append(box(460, 70, 190, 100, "#f3f7f4", JADE))
    c.append(f'<text x="555" y="94" font-size="13" font-weight="bold" '
             f'fill="{JADE}" text-anchor="middle">机器学习问题</text>')
    c.append(f'<text x="555" y="118" font-size="12" fill="{INK}" '
             f'text-anchor="middle">估计每人「若承保」</text>')
    c.append(f'<text x="555" y="136" font-size="12" fill="{INK}" '
             f'text-anchor="middle">的真实赔款并排序</text>')
    c.append(f'<text x="555" y="156" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">可计算 · 可验证</text>')

    # 底部注
    c.append(f'<text x="330" y="222" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">这一步不写代码、不训练模型——只需要业务和精算坐下来把四件事问清楚</text>')
    return _svg(660, 232, "".join(c),
                "翻译这一步的产物不是模型，是四行字。这四行字写不清楚，后面做得再漂亮也是白做。")


def _wall_svg(F):
    """同一诉求的两种翻译：一种废、一种 AUC 0.885。用两张对比卡，文字不出界。"""
    d = F["dev_wall"]
    g = d[1]["dev"]          # Poisson GLM 直接预测纯保费的偏差
    pct = d[1]["pct"]
    c3 = [x for x in F["combos"] if x["name"][0] == "③"][0]

    def card(x, w, stroke, head, sub, big, small, bcol):
        o = [f'<rect x="{x}" y="26" width="{w}" height="112" rx="10" '
             f'fill="#fff" stroke="{stroke}" stroke-width="1.6"/>',
             f'<rect x="{x}" y="26" width="{w}" height="4" rx="2" fill="{stroke}"/>',
             f'<text x="{x+w/2}" y="54" font-size="13.5" font-weight="bold" '
             f'fill="{stroke}" text-anchor="middle">{head}</text>',
             f'<text x="{x+w/2}" y="74" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">{sub}</text>',
             f'<text x="{x+w/2}" y="102" font-size="19" font-weight="bold" '
             f'fill="{bcol}" text-anchor="middle">{big}</text>',
             f'<text x="{x+w/2}" y="124" font-size="11.5" fill="{GREY}" '
             f'text-anchor="middle">{small}</text>']
        return "".join(o)

    c = []
    c.append(card(10, 310, RED, "直接预测纯保费", "Poisson GLM 一步到位",
                  f'偏差 {g:,.1f}', f'＝ 常数基线的 {pct}% —— 白做', RED))
    c.append(card(340, 310, JADE, "拆成频率 × 损失", "还是那个 GLM，分两步",
                  f'AUC {c3["auc"]}', f'Top20% 纯度 {c3["purity"]}%', JADE))

    for i, t in enumerate([
            "左边那种比「什么都不做」还差一点：95% 的人真实纯保费是 0，",
            "模型只要输出一个接近 0 的常数就最优，什么也没学会。"]):
        c.append(f'<text x="14" y="{160 + i * 18}" font-size="11.5" '
                 f'fill="{GREY}">{t}</text>')
    c.append(f'<text x="14" y="200" font-size="11.5" font-weight="bold" '
             f'fill="{INK}">差别不在算法，在问题怎么问。</text>')
    return _svg(660, 210, "".join(c),
                "同一个业务诉求，两种翻译方式：一种是废的，一种是 0.885。"
                "模型没换，换的是题目。")


def p_p01(F):
    killed = F["n_wrongly_killed"]
    nrej = F["n_rej"]
    combos = {c["name"][0]: c for c in F["combos"] if c["name"][0] in "①②③"}
    c3 = combos.get("③", {"auc": 0.885, "purity": 96.6})
    c1 = combos.get("①", {"auc": 0.753, "purity": 76.6})

    return f"""
<h1><span class="thin">第 2 段 · 端到端 · 阶段二</span>
把业务问题翻译成可计算的问题</h1>
<p class="lead">业务说「规则好像误杀了好人」，这句话机器一个字都听不懂。
<b>中间那一步叫翻译，它是整条流水线里最容易翻车、又最少有人讲的一步。</b>
这一页不写代码、不训练模型，只做一件事：把一句含糊的诉求，变成四行能算的字。</p>

{_step_frame(
  "学会把模糊的业务诉求，翻译成一道机器能算、并且算出来就有用的题目。",
  "一张翻译示意图、四问清单、本案例的完整翻译过程、三种常见翻车方式。",
  "这一页是全库最「不像机器学习」的一页，但它决定了后面所有页面的价值：题目问错了，算法再好也是错的。")}

{_toc([("why", "为什么要有这一步"), ("four", "翻译就是问清四件事"),
       ("case", "本案例是怎么翻译的"), ("bad", "三种常见的翻车方式"),
       ("check", "开工前的检查清单")])}

<h2 id="why">为什么要有这一步</h2>
<p>端到端流程通常被画成「数据 → 特征 → 训练 → 评估 → 部署」，
看起来是从拿到数据开始的。<b>但真正决定成败的，是数据之前那一步。</b></p>
<p>业务诉求天然是模糊的：它描述的是一个<b>不舒服的现状</b>（"我们好像丢了不少好客户"），
不是一个<b>可计算的目标</b>。机器学习只能接受后者。把前者变成后者，这一步没有工具可代劳，
只能靠人坐下来问清楚。</p>
<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>有人跟你说"这儿有点堵"。这句话没法算。你得先问清楚：
<b>堵在哪一段、什么时段、什么叫不堵、疏通之后谁去现场</b>。
问完这四句，才轮到摄像头和算法上场。机器学习项目里，"有点堵"这句话就是需求文档的全部。</p></div>

<h2 id="four">翻译就是问清四件事</h2>
{_map_svg()}
<p>四个问题，一个都不能省。它们的顺序也不能颠倒——<b>先问输出 y，再问输入 X</b>，
因为 y 决定了这件事能不能做，X 只决定它做得好不好。</p>
{_cmp_table([
    ["<b>② 输出 y 是什么</b>", "我们要预测的那个数／那个判断",
     "最关键的一个。<b>观测不到就没法做</b>——本案例的 y 恰恰观测不到，"
     "于是派生出后面整整一页（ch02 标签不可见）",
     "能不能做"],
    ["<b>① 输入 X 是什么</b>", "预测时手上能拿到哪些字段",
     "必须是<b>决策当时</b>就拿得到的，不能事后补；"
     "用了事后才知道的字段，模型上线就废",
     "做得好不好"],
    ["<b>③ 怎么算成功</b>", "用什么指标判定，达到多少算成",
     "必须是<b>能换算成钱或风险</b>的指标。"
     "AUC 高是必要条件，不是成功标准",
     "什么时候停"],
    ["<b>④ 然后谁做什么</b>", "预测出来之后，谁、凭什么、做什么动作",
     "没有动作的输出等于没有输出。"
     "<b>模型的价值是省下判断之前的那次翻牌</b>",
     "值不值得做"],
], ["问什么", "具体在问", "容易踩的坑", "它决定"])}

<h2 id="case">本案例是怎么翻译的</h2>
{_cmp_table([
    ["业务诉求", "「核保规则可能误杀了好人，我们想找回来」", "模糊，无法计算"],
    ["<b>② 输出 y</b>",
     f"每个被拒保的人，<b>假如当初承保了他</b>，一年的真实赔款是多少",
     "<b>这是个反事实问题</b>——他被拒了，永远不会有理赔记录"],
    ["<b>① 输入 X</b>",
     "投保当时已知的字段：年龄、车型、车龄、里程、渠道、地区……",
     "全部是决策当时就拿得到的，没有一条事后补"],
    ["<b>③ 怎么算成功</b>",
     f"不是 AUC，是「相对随机的增益」——同一笔复核预算，模型挑人比抽签多赚多少",
     f"峰值 {F['thr_peak_gain']:,.0f} 元（ch10 有完整推导）"],
    ["<b>④ 然后谁做什么</b>",
     f"输出一张 {F['thr_peak_n']:,} 人的名单，核保员逐件人工复核，<b>模型不拍板</b>",
     "模型是排队机，不是裁判"],
], ["翻译项", "本案例的答案", "为什么这么定"])}

<div class="note"><b>整个库最难的一点，就藏在 ② 那一行里。</b>
<p>我们要预测的是「<b>假如承保了他</b>会赔多少」，但这些人<b>恰恰被拒保了，根本不会有理赔记录</b>。
想预测的量，和能观测到的量，不是同一个东西——这在统计上叫
<a href="ch02.html">标签不可见</a>，在因果推断里叫反事实。
后面 ch02（标签为什么不是 0）、ch07（选择偏差）、ch08（IPW 与双重稳健）
整整三页，都是在给这一行填空。<b>翻译这一步如果偷懒，这里就会被悄悄跳过，
后面的模型会用一个错误的 y 训练得很漂亮。</b></p></div>

<h2 id="bad">三种常见的翻车方式</h2>
<p>同一个业务诉求，翻译方式不同，结果可能一个是废的、一个是满分。
先看本库自己踩过的那个：</p>

<h3>翻车一：题目问得太大，模型直接躺平</h3>
{_wall_svg(F)}
<p>第一版的想法很自然：既然要估计真实赔款，那就直接拿纯保费当 y，用 Poisson GLM 去回归。
结果偏差 9,005.9，<b>比什么都不做的常数基线 8,994.5 还差</b>——等于完全没学会。
原因不是算法不行，是题目问错了：95% 的人真实纯保费是 0，
模型只要输出一个接近 0 的常数就已经"最优"，没有任何动力去区分谁好谁坏。
<b>拆成「频率 × 损失」两步之后，同一个 GLM 的 AUC 变成 {c3['auc']}。</b>
差别不在算法，在问题怎么问。</p>

<h3>翻车二：拿能观测到的，代替真正想要的</h3>
<p>想要「真实风险」，手上只有「已承保客户的理赔记录」。
于是很自然地拿后者当 y——但已承保的人是被规则筛过的，
<b>用他们训练出来的模型，学的其实是「规则喜欢谁」，不是「谁风险低」</b>。
这就是 <a href="ch07.html">选择偏差</a>：模型会把规则的历史偏见原封不动地学回去，
甚至放大它。本案例里线上渠道错杀率是代理渠道的
{F['kill_ratio_online_vs_agent']} 倍，规则把「信息好不好查」当成了「风险高不高」——
这种偏见一旦被学进去，模型会替规则辩护。</p>

<h3>翻车三：指标和决策脱节</h3>
<p>AUC 从 {c1['auc']} 提到 {c3['auc']} 听起来是大进步，
但真正决定赚多少钱的是「圈多少人」那条倒 U 曲线，
而<b>那条曲线上根本没有 AUC 这个轴</b>。
指标再漂亮，如果它和「然后谁做什么」对不上，那个数字就是自娱自乐。
本库的做法是：<b>先用 AUC 证明排序有价值，再用增益曲线决定圈多少</b>，两步分开，
各管一件事。</p>

<h2 id="check">开工前的检查清单</h2>
{_cmp_table([
    ["☐ 输出 y 写清楚了吗", "能用一句话说完「预测什么」吗",
     "说不出来就别开工，回去问业务"],
    ["☐ y 观测得到吗", "样本里真的有这个标签吗，还是只有它的一部分",
     "观测不到 → 先读 ch02，不是先调参"],
    ["☐ X 都是当时能拿到的吗", "有没有混入「事后才知道」的字段",
     "漏网一条，上线就废（时间旅行泄漏）"],
    ["☐ 成功标准能换算成钱吗", "指标涨了，业务会多赚多少",
     "不能换算 → 换指标，别换模型"],
    ["☐ 输出之后谁做什么", "有没有一个具体的人、具体的动作",
     "没有动作 → 这个项目不会有收益"],
    ["☐ 不做模型行不行", "有没有更便宜的办法（改规则、做实验）",
     "见 s02：先比再选，别默认就该用模型"],
], ["检查项", "问自己", "不通过怎么办"])}

{_three([
    "<b>翻译这一步不产出模型，产出四行字。</b>这四行字写不清楚，后面的算法、调参、部署做得再漂亮，都是在给一个错的问题找漂亮的答案。",
    "四个问题的顺序不能颠倒：<b>先问 y，再问 X</b>。y 决定这件事能不能做，X 只决定做得好不好。",
    f"本案例的全部难点，都源于 ② 那一行——想预测的量（{nrej:,} 个被拒保的人若承保会赔多少）恰恰观测不到。"
    f"后面三页都是在给这一行填空，不是在做模型优化。",
])}

<div class="quote q-talk"><span class="q-tag">下一步</span>
<p>翻译完成，题目立住了：<b>估计每个被拒保的人若承保的真实赔款，并排序</b>。
接下来要选一个能干这活的模型。下一页
<a href="ch01.html">从你熟悉的 GLM 出发</a>——
先看你已经在用的东西为什么不够，再谈机器学习补上了什么。</p></div>
"""
