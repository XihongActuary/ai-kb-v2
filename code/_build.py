# -*- coding: utf-8 -*-
"""
AI 实践库 · 站点构建器

用法：python _build.py
  读 pages_basics / pages_a/b/c.py 里的页面定义 + out/facts.json 的数字，
  套上统一的侧栏与骨架，输出全部 HTML 到项目根目录。

为什么用构建器：20+ 页共用一套导航，改导航不必改 20 个文件；
数字从 facts.json 注入，杜绝「页面说 15%，数据说 25.7%」的腐烂。

2026-10-03 改造（针对「看不懂」的反馈）：
  1. 修掉导航高亮的引号嵌套 bug（`class="nav class="on""`）
  2. 每页顶部自动注入「白话摘要」——先把这页讲什么用大白话说一遍
  3. 每页顶部自动注入「本页会遇到的词」——从术语词典匹配，链接到术语表
"""
import os
import io
import re
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navmap import NAV, PART, FILES
from pages_a import PAGES_A
from pages_b import PAGES_B
from pages_c import PAGES_C
from pages_basics import PAGES_BASIC
from pages_glossary import p_glossary
from pages_tools import PAGES_TOOL
from pages_up import PAGES_UP
from pages_x import p_x01, p_x02
from pages_p import p_p01
from pages_code import p_code, short_of, src_of_page
import _srcdoc
from terms import TERMS, IDX, ALIASES, COMMON, SLUG, NO_INLINE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_facts():
    """数字的唯一来源。

    facts.json 来自 Python 流水线；anim_facts.json 是三个动画（纯前端算法）
    的最终数字，由 node code/_animfacts.js 复算产出。两者合并后注入页面，
    页面里就不允许再写死数字。
    """
    F = json.load(open(os.path.join(ROOT, "out", "facts.json"), encoding="utf-8"))
    p = os.path.join(ROOT, "out", "anim_facts.json")
    if os.path.exists(p):
        F["anim"] = json.load(open(p, encoding="utf-8"))
    else:
        F["anim"] = {}
    return F


F = _load_facts()


# glossary 在侧栏「工具」组里渲染，顺序以上面 NAV 为准
FILES = [n[0] for n in NAV if n[1]]


# 每页属于哪一「篇」——从 NAV 的分组标题反推，页头标题栏要用
PART = {}
_cur = ""
for item in NAV:
    if item[1] is None:
        _cur = "第 2 段 · 端到端" if item[0].startswith("阶段") else item[0]
    else:
        PART[item[0]] = _cur

# ---------------------------------------------------------------- 姊妹库互链
# 本库（ai-kb）讲「怎么做到落地」，姊妹库 ml-kb 讲「背后的道理讲透」。
# 两边各管一段、互相指路，不复制内容——否则要维护两份，迟早对不上。
MLKB = {
    "b01": [("overview", "机器学习到底在干什么"),
            ("mgmt", "给管理层看的通俗版")],
    "b02": [("onepage", "一文读懂机器学习")],
    "b03": [("core", "核心三要素")],
    "b04": [("oneday", "一小时精读"), ("core", "核心三要素")],
    "b05": [("notes", "西瓜书 · 模型评估与选择"),
            ("onepage", "一文读懂机器学习")],
    "b06": [("notes", "西瓜书十七章 + 拓展")],
    "b07": [("core", "AI 全景"), ("onepage", "一文读懂机器学习")],
    "b08": [("notes", "西瓜书 · 模型评估与选择"),
            ("oneday", "一小时精读")],
    "b14": [("oneday", "一小时精读"), ("core", "核心三要素")],
    "b11": [("notes", "西瓜书十七章 + 拓展")],
    "b12": [("notes", "西瓜书十七章 + 拓展"),
            ("resources", "外部资源与素材来源")],
    "b13": [("oneday", "一小时精读")],
    "b09": [("index", "ml-kb 首页 · 三层学习路径"),
            ("resources", "外部资源与素材来源")],
}


def mlkb_bar(fn):
    """理论页顶部的「往深了学」条：指向姊妹库 ml-kb。"""
    items = MLKB.get(fn)
    if not items:
        return ""
    links = " · ".join(
        f'<a href="../ml-kb/{f}.html" target="_blank" rel="noopener">{t}</a>'
        for f, t in items)
    return (f'<div class="mlkb"><span class="ml-k">往深了学 · 机器学习知识库</span>'
            f'{links}</div>')


# ---------------------------------------------------------------- 白话摘要
# 格式：(这一页在讲什么, 读完你会知道)
SUMMARY = {
    "index": ("这个库要解决的，是一件很具体的事：保险公司的核保规则拒掉了 8,800 个人，"
              "其中 2,259 个人的真实风险其实比已承保客户还低。他们是被规则冤枉的。"
              "我们要用机器学习把他们找回来，同时搞清楚机器每一步在干什么、什么时候会骗人。",
              "机器学习不难，难的是判断它什么时候不可信。这个库教的就是后者。"),
    "p01": ("业务说「规则好像误杀了好人」，这句话机器一个字都听不懂。"
            "中间那一步叫翻译：把含糊的诉求变成四行能算的字——输出 y 是什么、输入 X 是什么、"
            "怎么算成功、然后谁做什么。这一页不写代码、不训练模型，但它是整条流水线里"
            "最容易翻车的一步。",
            "翻译这一步不产出模型，产出四行字。这四行字写不清楚，"
            "后面的算法做得再漂亮，都是在给一个错的问题找漂亮的答案。"),
    "x01": ("如果这个库读了好几页还是有点飘，就来这一页。它只回答三件事："
            "解决了什么问题、用了什么方法、达到了什么效果——每件事一句话说完，再给撑得住这句话的数字。",
            "模型是排队机，不是裁判：它不决定谁对谁错，只决定谁先被看。"
            "原来 8,800 件才找得完，现在复核 4,400 件就找回了大部分。"),
    "x02": ("三个动画看完，画面记住了却说不清它们各自解决了什么。这一页用一张表横向对齐："
            "每个动画解决什么问题、最终的数学表达式怎么读、代码在哪。",
            "三个动画其实在解同一道题——找一组参数让猜错的代价最小；"
            "区别只是你允许这条规律长成什么样：一条线、一串台阶、还是一群接力的小树。"),
    "b01": ("机器学习到底是什么。不讲公式，先玩一个「猜房价」的游戏："
            "给你一本规则手册，和给你 1,000 条真实成交记录，你会选哪个？",
            "机器学习 = 用一堆过去的答案，换一套能应付新问题的规则。它不聪明，只是不厌其烦。"),
    "b02": ("机器学习吃的那张表长什么样。以及本案例最要命的一个坑："
            "被拒保的人根本没有出险记录。",
            "一行一个人、一列一个属性；数据里的 −1 表示「不知道」，不是「零」。这一字之差能毁掉模型。"),
    "b03": ("模型是什么。你每天都在用好几个模型——菜谱、体检评分表、核保规则分，"
            "它们本质上都是「输入 → 输出」的套路。",
            "学模型 = 把模型里那几个空数字填上。没有别的玄机。"),
    "b04": ("训练在干什么。就三步：先瞎猜一次，看看差多少，往对的方向挪一点——然后重复。",
            "挪到挪不动就叫收敛，可以停了。损失函数听着吓人，其实就是「猜错的扣分表」。"),
    "b05": ("为什么有的模型训练时完美、一上真实业务就崩。这是机器学习第一号翻车原因。",
            "留出一份从没见过的数据当期末考，考前一次都不许看。这就够防住大部分翻车。"),
    "b06": ("模型和算法到底有什么区别。以及为什么「上 AI」不是买个软件就完事。",
            "模型是成品，算法是工艺。还有几个旋钮（树多深、走多快）必须懂业务的人来拧。"),
    "b07": ("人工智能、机器学习、深度学习、强化学习——这四个词天天一起出现，但它们不是并列的。",
            "AI ⊃ 机器学习 ⊃ 深度学习。表格数据（一行一个人）一般用不到深度学习。"),
    "b08": ("「这个模型好不好」其实不是一个问题，是三个问题：排序准不准、数字准不准、圈出来划不划算。",
            "排序准 ≠ 数字准。本案例的模型整体虚高三成，所以只能用来排序、不能用来定价。"),
    "b09": ("市面材料良莠不齐，新手最容易一上来啃深度学习被劝退，或收藏 100 篇一篇没读完。",
            "这条路线就一句：先直觉、再系统入门、上手表格数据、最后才啃理论书；选模型看数据，不看名字。"),
    "b10": ("机器学习项目不是「训练一个模型」，而是从业务问题走到落地的一整条流水线。"
            "这页把七个步骤画成一个环，每一步都落到真实源码文件上。",
            "顺序比算法重要：把「数据对不对」的验证，放在「模型好不好」的调校之前。"),
    "b11": ("算法名不该当菜单背。先看你到底要预测什么——数字、类别、还是分组。",
            "数字→回归，类别→分类，无标签→聚类，特征太多→降维。本案例预测纯保费，是回归。"),
    "b12": ("选模型的第一步不是挑算法，是定义任务：先回答「我到底想算出个什么东西」。",
            "「业务上圈不圈」和「模型预测什么」是两件事——本案例是回归，不是二分类。"),
    "b13": ("六句听着都对、做就错的念头，本案例基本全踩过一遍。",
            "真正该长期盯的是四件事：问题定义、数据质量、泛化能力、结果能不能指导业务。"),
    "b14": ("「训练」这两个字背后其实是一趟下山：先算错了多少（损失），再朝错得少的方向挪一点（梯度）。",
            "本案例的 Poisson GLM 就是这么挪的：deviance 从 8,994.5 挪到 9,005.9 是因为挪过头了——这本身就是收敛判据。"),
    "ch01": ("把你天天在用的费率因子，翻译成机器学习的语言。你会发现：你早就会机器学习了。",
            "精算叫费率因子、统计叫回归系数、机器学习叫特征权重——说的是同一个东西。"),
    "ch02": ("被拒保的人没有出险记录。这个事实看着简单，但它决定了整个案例的难度。",
            "claim_cnt = −1 表示「没有记录」，不是「零出险」。当成零，模型会学出一个荒唐结论。"),
    "ch03": ("为什么直接预测纯保费会失败——因为大多数人是 0，极少数人赔得极多。",
            "大量 0 + 极少数巨额，会把普通指标搅乱。标准解法是拆成「频率 × 损失」分别建模。"),
    "ch04": ("点开动画，看着机器把一条线从「完全瞎猜」改到「基本画对」，一共只用了七步。",
            "IRLS 这个名字很唬人，意思就是「猜一次、看差距、挪一点」，重复到不动为止。"),
    "ch05": ("点开动画，看机器怎么挑出「该先问哪个问题」。它会把所有可能的问法都试一遍。",
            "决策树每次挑能让两边各自最「纯」的那一刀。所谓纯，就是那一堆人好坏比例别各占一半。"),
    "ch06": ("一棵树不够用怎么办？让第二棵树专门去补第一棵漏掉的部分，再来第三棵……",
            "GBDT 就是「学生做题」：第一遍做完，第二遍只攻错题，几轮下来就接近满分。"),
    "ch07": ("审计样本是从被拒的人里抽一小部分人工核查。但抽样本身可能是歪的。",
            "你手上只有被承保人的记录——你的「已知世界」从一开始就是歪的。"),
    "ch08": ("怎么把被抽歪的样本掰回来。两种修法：逆概率加权，和更稳的双重稳健。",
            "IPW 给被少抽到的人更大的权重；双重稳健两条腿走路，断一条还能站。"),
    "ch09": ("给模型一个它从没见过的人打分，会发生什么。这是本案例最反直觉的一页。",
            "排序能力没崩，但数值整体虚高三成。所以落地方案是：只用它排序，不用它定价。"),
    "ch10": ("圈谁去复核最划算？圈太少漏掉利润，圈太多白花人工——中间有个最优点。",
            "倒 U 曲线：圈 4,400 件时增益最大。阈值要贴着「盈亏平衡」定，不是贴着中位数定。"),
    "ch11": ("模型 B 在报表上全面优于模型 A，但它其实一点都没更准。这一页把它拆到底。",
            "B 只是把预测刻度整体压低了，于是同样阈值下圈出更多人。跨模型比较必须先对齐刻度。"),
    "ch12": ("八步流水线从头走一遍，每一步回答「为什么这么做」，而不只是「做了什么」。",
            "整套流程里，真正决定成败的不是算法，是每一步对「数据从哪来」的追问。"),
    "s01": ("在谈模型之前，先说清公司现在是怎么处理被拒客户的：三条腿各自覆盖多少人、盲区在哪。",
            "现状不是做得不好，是「看不见自己错了」——被拒的人不在公司，没有出险记录。"),
    "s02": ("同一个问题有五条路。两条走不通、一条是基线、一条必做、一条才是本库方案。",
            "机器学习不是替代复核，是省下复核——它是排队机，不是裁判。"),
    "s03": ("收益侧已经算出来了，成本侧还是空的。这页把成本补上，并给出唯一的那个关键输入。",
            "盈亏平衡点在单件复核成本 88 元——这个数一拿到，整本账立刻就清楚了。"),
    "s04": ("模型上线不是终点，是风险的开始：看什么、怎么灰度、什么时候重训、什么时候撤。",
            "必须保留一组随机对照，否则分不清模型是真变准了，还是越转越确信。"),
    "s05": ("同一个问题至少四种范式：预测 / 因果 / 运筹 / 实验，机器学习只是第一种。",
            "能做实验的场合，实验优于模型——模型是「不能做实验时」的次优解。"),
    "s06": ("谁来做？精算 / 数据 / 核保 / IT / 合规各干什么，要多大投入，最容易卡在哪。",
            "牵头人应该是精算，因为他要拍板「什么叫对」——那是立场，不是技术。"),
    "s07": ("错杀怎么在二十年来都没被发现？——因为规则从来不去问「拒了的人如果承保会怎样」。"
            "方案再好讲不清就批不下来。一段三十秒电梯演讲、三句分对象的话、六问六答。",
            "三十秒版本的核心不是数字，是那句「我们看不到自己错了」。"),
    "q01": ("15 道反直觉的自测题，按五个主题分组，答案默认折叠。",
            "错在哪一组，就回去读哪一组对应的页面——这是最快找出自己没真懂的地方的办法。"),
    "code": ("这个库里出现的每一个数字、每一张图，都由 code/ 下真实跑过的代码产生。"
             "这一页是它们的总闸：七阶段各自对应哪份代码、想上手跑该敲哪三条命令。",
             "摆得下、找得到、能跑通——代码入口不替人家读代码，只让人想求证时知道去哪儿找。"),
    "ch13": ("导出清单怎么用、第一年该做到什么程度、什么情况下必须停下来人工看。",
            "第一年只做保守版：只对「模型熟悉的人」放宽，远点维持原规则。少赚一点，但不出事。"),
    "m01": ("12 个常见模型的一页速查：每个都说清它是什么、什么时候该用、怎么用，"
            "并标出本案例到底用没用过它、用在哪段源码。",
            "别按名字选模型，按任务选：预测数字走回归分支，分组走聚类分支。本案例只用其中三个。"),
    "a01": ("13 个常见算法的一页速查。算法是把模型「算出来」的那套工艺，不是模型本身。",
            "同一个模型可以换不同算法来算；选算法的实际依据是数据量、凸不凸、要不要可解释。"),
    "glossary": ("全库术语的中英双语大白话对照表，支持实时搜索。",
                "每条都配一句话白话和一个生活类比；看不懂的词不用背，回来查就行。"),
}


def plain_box(fn):
    if fn not in SUMMARY:
        return ""
    what, know = SUMMARY[fn]
    return (f'<div class="plain">'
            f'<div class="p-row"><span class="p-q">这一页在讲什么</span>'
            f'<p>{what}</p></div>'
            f'<div class="p-row"><span class="p-q">读完你会知道</span>'
            f'<p class="p-know">{know}</p></div>'
            f'</div>')


def _div_end(body, start):
    """从 start 处的 <div …> 开始，返回它配对 </div> 结束后的下标。"""
    depth, j = 1, body.find(">", start) + 1
    while depth:
        nd = body.find("<div", j)
        cd = body.find("</div>", j)
        if cd < 0:
            return len(body)
        if 0 <= nd < cd:
            depth += 1
            j = nd + 4
        else:
            depth -= 1
            j = cd + 6
    return j


H2_RE = re.compile(r'<h([234])(?![^>]*\bid=")[^>]*>([\s\S]*?)</h\1>')


def ensure_ids(body):
    """给没写 id 的 <h2>/<h3>/<h4> 补一个，保证目录里有锚点可跳。"""
    box = {2: 0, 3: 0, 4: 0}

    def rep(m):
        lv = int(m.group(1))
        box[lv] += 1
        return m.group(0).replace(f"<h{lv}", f'<h{lv} id="sec{lv}-{box[lv]}"', 1)
    return H2_RE.sub(rep, body)


def auto_toc(body):
    """没手写目录的页（工具页、速查页）按小节自动生成，保证每页标题下都有目录。

    优先用 h2；只有一节标题、但正文是「步骤 1 / 步骤 2…」这种结构的页（如 ch12），
    退到 h4，否则整页就没有目录可点。
    """
    for lv in (2, 3, 4):
        heads = re.findall(rf'<h{lv} id="([^"]+)">([\s\S]*?)</h{lv}>', body)
        if len(heads) >= 2:
            items = "".join(
                f'<a href="#{i}">{re.sub(r"<[^>]+>", "", t).strip()}</a>'
                for i, t in heads)
            return f'<div class="toc"><div class="t">本页目录</div>{items}</div>'
    return ""


def pull_toc(body):
    """把「本页目录」从正文里摘出来。

    为什么摘：页头把 h1 与 lead 提到标题栏之后，原本紧跟标题的目录就被
    挤到了摘要、术语条后面——等于目录跑到了正文头上。现在统一抽出来，
    紧贴标题栏下方，读者第一眼就知道这页分几段。
    """
    i = body.find('<div class="toc">')
    if i < 0:
        return "", body
    j = _div_end(body, i)
    return body[i:j].strip(), (body[:i] + body[j:]).strip()


def merge_summary(fn, body):
    """把「这一页在讲什么 / 读完你会知道」并进「本页要做的三件事」框。

    两个框说的是同一件事的两种说法，分开摆等于让人读两遍。合并后：
    「讲什么」当框的引子，「读完你会知道」当框的收尾，中间仍是目标/输出/怎么读。
    没有 gof 框的页面（纯理论页）保持原来的白话摘要框不动。
    """
    if fn not in SUMMARY or '<div class="gof-h">' not in body:
        return body, False
    what, know = SUMMARY[fn]
    hi = body.find('<div class="gof-h">')
    hj = body.find("</div>", hi) + 6
    body = body[:hj] + f'<p class="gof-what">{what}</p>' + body[hj:]
    gi = body.find('<div class="gof">')
    gj = _div_end(body, gi)
    row = (f'<div class="gof-row"><span class="gof-k gof-know">读完你会知道</span>'
           f'<div class="gof-v">{know}</div></div>')
    body = body[:gj - 6] + row + body[gj - 6:]
    return body, True


# -------------------------------------------------- 正文术语内联链接
# 为什么要做：读者在正文里撞见「MSE」的时候，旁边没有任何可点的地方——
# 要么硬猜，要么自己翻到术语表从头找。现在正文里带虚线下划线的词都能点，
# 鼠标停一下还会浮出那句大白话解释，大多数时候根本不用离开这一页。
#
# 两条硬约束：
#   1. 只在纯文本里替换 —— <a> / <code> / <script> / <svg> 内部一律跳过，
#      否则会把标签属性和代码里的变量一起链掉；
#   2. 同一个词一页最多链 2 次 —— 链满页等于没链，反而把正文染成蓝色。
SKIP_TAGS = {"a", "code", "script", "style", "svg", "textarea", "h1"}
TAG_RE = re.compile(r"(<[^>]+>)")

_ALIAS_LC = {}
for _k, _ws in ALIASES.items():
    if _k in NO_INLINE:
        continue
    for _w in _ws:
        if _w:
            _ALIAS_LC.setdefault(_w.lower(), _k)

# 长词优先：否则「深度学习」会被「深度」抢走、「随机种子」会被「种子」抢走
_WORDS = sorted(_ALIAS_LC, key=lambda s: (-len(s), s))
TERM_RE = re.compile("|".join(
    (r"(?<![A-Za-z0-9])" + re.escape(w) + r"(?![A-Za-z0-9])")
    if w.isascii() and w[0].isalnum() else re.escape(w)
    for w in _WORDS), re.I)


def link_terms(body, fn, maxn=2):
    """把正文里出现的术语，就地换成指向术语表对应条目的链接。"""
    if fn in NO_LINK:
        return body
    used = {}

    def rep(m):
        w = m.group(0)
        tid = _ALIAS_LC.get(w.lower())
        if tid is None or used.get(tid, 0) >= maxn:
            return w
        used[tid] = used.get(tid, 0) + 1
        t = IDX[tid]
        tip = t["plain"]
        if len(tip) > 46:
            tip = tip[:44] + "…"
        for a, b in (("&", "&amp;"), ('"', "&quot;"), ("<", "&lt;"), (">", "&gt;")):
            tip = tip.replace(a, b)
        return (f'<a class="tl" href="glossary.html#term-{t["slug"]}" '
                f'title="{t["zh"]}｜{tip}">{w}</a>')

    out, stack = [], []
    for seg in TAG_RE.split(body):
        if not seg:
            continue
        if seg[0] == "<":
            out.append(seg)
            m = re.match(r"<\s*(/)?\s*([a-zA-Z0-9]+)", seg)
            if m:
                tag = m.group(2).lower()
                if m.group(1):
                    if tag in stack:
                        while stack and stack.pop() != tag:
                            pass
                elif tag in SKIP_TAGS:
                    stack.append(tag)
            continue
        out.append(seg if stack else TERM_RE.sub(rep, seg))
    return "".join(out)


# 每页的「核心术语」——手工指定，优先于按词频自动匹配。
# 为什么不能只靠词频：ch08 讲 IPW，但正文里「外推」两字出现次数更多，
# 结果 IPW 被挤到后面。读者要的是「这页的主角是谁」，不是「哪个词重复最多」。
PRIORITY = {
    "index": ["错杀", "ML", "AUC"],
    "x01": ["错杀", "召回率", "精确率（圈选纯度）", "AUC", "审计样本", "误伤"],
    "p01": ["特征", "标签（答案）", "过拟合", "AUC", "偏差（广义）", "无监督学习"],
    "x02": ["梯度下降", "Gini", "集成学习", "学习率", "MSE", "过拟合"],
    "b01": ["ML", "AI", "监督学习"],
    "b02": ["特征", "标签（答案）", "训练集", "测试集"],
    "b03": ["模型", "参数（系数）", "GLM", "决策树"],
    "b04": ["训练（拟合）", "损失函数", "收敛"],
    "b05": ["过拟合", "训练集", "验证集", "测试集", "泛化能力"],
    "b06": ["算法", "超参数", "正则化", "IRLS"],
    "b07": ["AI", "ML", "DL", "RL", "监督学习", "集成学习"],
    "b08": ["AUC", "校准", "召回率", "精确率（圈选纯度）", "提升度（Lift）", "阈值（切点）"],
    "b09": ["AI", "ML", "DL", "RL", "监督学习", "神经网络"],
    "b10": ["训练集", "测试集", "特征工程", "超参数", "AUC", "外推（训练域外）"],
    "b11": ["监督学习", "回归（预测连续值）", "分类（预测类别）", "聚类（无标签分组）", "降维", "GBDT"],
    "b12": ["监督学习", "无监督学习", "RL", "回归（预测连续值）", "分类（预测类别）", "外推（训练域外）"],
    "b13": ["过拟合", "训练集", "测试集", "泛化能力", "偏差-方差权衡", "外推（训练域外）"],
    "b14": ["损失函数", "梯度下降", "收敛", "学习率", "局部最优 / 全局最优", "超参数"],
    "ch01": ["GLM", "泊松回归", "纯保费"],
    "ch02": ["标签（答案）", "错杀", "选择偏差"],
    "ch03": ["纯保费", "出险频率", "案均损失", "零膨胀", "重尾", "Tweedie"],
    "ch04": ["IRLS", "GLM", "泊松回归", "收敛", "偏差（广义）"],
    "ch05": ["决策树", "不纯度", "Gini", "Gain", "树深与叶子"],
    "ch06": ["GBDT", "残差（梯度）", "学习率", "MSE", "集成学习", "噪声"],
    "ch07": ["选择偏差", "审计样本", "错杀"],
    "ch08": ["IPW", "DR", "审计样本", "选择偏差"],
    "ch09": ["外推（训练域外）", "校准", "AUC"],
    "ch10": ["召回率", "精确率（圈选纯度）", "阈值（切点）", "误伤", "错杀"],
    "ch11": ["校准", "代理变量", "AUC", "召回率"],
    "ch12": ["训练集", "测试集", "ML", "上线与部署", "A/B"],
    "ch13": ["错杀", "误伤", "审计样本", "PSI", "漂移"],
    "s01": ["错杀", "审计样本", "选择偏差"],
    "s02": ["召回率", "精确率（圈选纯度）", "监督学习"],
    "s03": ["召回率", "精确率（圈选纯度）", "校准"],
    "s04": ["校准", "外推（训练域外）", "AUC"],
    "s05": ["监督学习", "无监督学习", "外推（训练域外）"],
    "s06": ["训练集", "审计样本", "错杀"],
    "s07": ["错杀", "精确率（圈选纯度）", "校准"],
    "q01": ["过拟合", "外推（训练域外）", "校准", "召回率", "审计样本"],
    "code": ["ML", "训练集", "测试集", "偏差（广义）", "AUC", "错杀"],
}


CODE_LINK_RE = re.compile(r'<a class="codelink" href="src/([a-z_0-9.]+)\.html(?:#[^"]*)?"')


def code_bar(fn, body):
    """页尾「本页用到的代码」：把正文里链到的源码文件收成一排。

    正文里的绿色代码块已经能直达具体那几行，但看完一段代码之后，
    读者并不知道这份文件在整个项目里排第几。这里给位置，也给回到总闸的出口。
    """
    if fn == "code":                       # 代码入口页自己不必总结自己
        return ""
    names, seen = [], set()
    for m in CODE_LINK_RE.finditer(body):
        n = m.group(1)
        if n not in seen:
            seen.add(n)
            names.append(n)
    # 再补「这一页在讲的那份代码」——正文没提文件名的，靠映射表照样能回到代码
    for n in src_of_page(fn):
        if n not in seen:
            seen.add(n)
            names.append(n)
    if not names:
        return ""
    items = "".join(
        f'<a class="cb-i" href="src/{n}.html"><b>{n}</b>'
        f'<span>{short_of(n) or "源码"}</span></a>' for n in names)
    return (f'<div class="codebar"><div class="cb-t">本页用到的代码</div>'
            f'<div class="cb-items">{items}</div>'
            f'<a class="cb-all" href="code.html">全部代码 → 代码入口'
            f'<span>{NAV_NO.get("code", "")}</span></a>'
            f'</div>')


def page_terms(fn, body, maxn=6):
    """本页会遇到的词：先列手工指定的核心术语，再用词频自动补足。"""
    txt = re.sub(r"<script[\s\S]*?</script>", " ", body)
    txt = re.sub(r"<[^>]+>", " ", txt)
    hits = []
    for key, words in ALIASES.items():
        c = sum(txt.count(w) for w in words)
        if c > 0:
            hits.append((c, key))
    hits.sort(reverse=True)

    out, seen = [], set()
    for key in PRIORITY.get(fn, []):
        t = IDX.get(key)
        if t and t["id"] not in seen:
            out.append(t)
            seen.add(t["id"])

    auto, backup = [], []
    for _, key in hits:
        t = IDX.get(key)
        if t is None or t["id"] in seen:
            continue
        (backup if key in COMMON else auto).append(t)
    for t in auto + backup:
        if len(out) >= maxn:
            break
        if t["id"] not in seen:
            out.append(t)
            seen.add(t["id"])
    if not out:
        return ""
    rows = "".join(
        f'<div class="t-item"><a href="glossary.html#term-{t["slug"]}">'
        f'<b>{t["abbr"] or t["zh"]}</b></a>'
        f'<span>{t["plain"]}</span></div>' for t in out)
    # 「本页词语解释」放在正文之后：读的时候先顺着读，遇到想查的词再回来看，
    # 摆在最上面等于进门先背六个名词，反而劝退
    return ('<div class="terms-here"><div class="th-t">本页词语解释'
            '<span>正文里带虚线的词，点一下也能到这里</span></div>'
            f'{rows}</div>')


# ---------------------------------------------------------------- 页头标题栏
# 为什么要把 <h1> 从正文里摘出来单独做一条标题栏：
# 之前 h1 排在白话摘要和术语条后面，等于把标题埋在两段说明文字底下，
# 滚到正文中段就不知道自己在哪一页了。现在统一提到最上方，
# 一行给出「编号 · 所属篇 · 大标题 · 一句话」，与姊妹知识库的章头保持一致。
H1_RE = re.compile(r'<h1>([\s\S]*?)</h1>(\s*<p class="lead">([\s\S]*?)</p>)?')


NAV_NO = {n[0]: n[2] for n in NAV if n[1]}


def _seg(part):
    """「第 1 段 · 理论：先把道理讲透」→「第 1 段 · 理论」（去掉副标题，页头只放段名）"""
    if not part:
        return ""
    seg = part.split(" · ")
    if len(seg) >= 2:
        return seg[0] + " · " + seg[1].split("：")[0]
    return part.split("：")[0]


def head_bar(fn, no, body, fallback_title):
    """返回 (标题栏 HTML, 摘掉 h1 与 lead 之后的正文)。"""
    m = H1_RE.search(body)
    if m:
        inner = m.group(1)
        lead = (m.group(3) or "").strip()
        body = body[:m.start()] + body[m.end():]
        t = re.search(r'<span class="thin">([\s\S]*?)</span>', inner)
        kicker = t.group(1).strip() if t else ""
        title = re.sub(r'<span class="thin">[\s\S]*?</span>', "", inner).strip()
        # 「决策篇 · 01」「第一部分 · … · 01」尾号已在编号徽标里，去掉避免重复
        kicker = re.sub(r"\s*[·・]\s*[\dA-Za-z]+\s*$", "", kicker).strip()
    else:
        # 少数页（速查类）没有 h1，标题取导航名；若正文开头有 lead，照样提上来当副标题
        kicker, title, lead = "", fallback_title, ""
        m2 = re.match(r'\s*<p class="lead">([\s\S]*?)</p>', body)
        if m2:
            lead = m2.group(1).strip()
            body = body[m2.end():]
    kicker = _seg(PART.get(fn, "")) or kicker
    title = title or fallback_title

    i = FILES.index(fn) + 1
    n = len(FILES)
    h = [f'<header class="pghead" data-no="{no}">',
         '<div class="ph-kicker">',
         f'<span class="ph-no">{no}</span>']
    if kicker:
        h.append(f'<span class="ph-part">{kicker}</span>')
    # 徽标就是连续页序，再显示一次「i / n」会重复同一个数字，这里只报总数
    h.append(f'<span class="ph-idx" title="你在第 {i} 页">共 {n} 页</span>')
    h.append("</div>")
    h.append(f"<h1>{title}</h1>")
    if lead:
        h.append(f'<p class="ph-lead">{lead}</p>')
    h.append("</header>")
    return "\n".join(h), body


def _nav_link(fn, title, no, cur):
    cls = "nav on" if fn == cur else "nav"
    return (f'<a class="{cls}" href="{fn}.html">'
            f'<span class="no">{no}</span>{title}</a>')


def about_box():
    """侧栏顶部的「关于」折叠块：项目介绍 + 西红精算介绍。

    这些内容原来单独占一个 about.html。撤掉独立页的理由很实在：
    一个只在侧栏底部露一行的入口，等于把介绍藏起来；放在侧栏顶部，
    每一页都能看见，点开就能读。
    """
    n = len(FILES)

    def lk(k, t):
        return f'<a href="{k}.html">{NAV_NO.get(k, "")} {t}</a>'

    return f"""<details class="sb-about" id="about">
<summary><span class="sba-t">关于这个库 · 关于西红精算</span><span class="caret">▸</span></summary>
<div class="sba-body">
<div class="sba-h">这个库在做什么</div>
<p>一个车险场景，从「这事到底要不要做」一路走到「上线之后怎么盯」，共 <b>{n} 页</b>、四段：
先看全貌 → 讲透道理 → 端到端做完 → 附录随查。</p>
<p><b>它不打算让你相信结论，它打算让你自己把结论跑出来一遍。</b>三条硬做法：
数据自己造（<code>code/gen_data.py</code>，不含任何真实保单）；
模型手写（Poisson GLM、决策树、GBDT 全不调现成包）；
数字只有一个来源（<code>out/facts.json</code>，页面里不写死任何一个）。</p>

<div class="sba-h">怎么读</div>
<p>零基础：从 {lk('b01', '机器学习到底在干什么')} 顺着读。<br>
赶时间：{lk('x01', '一页讲清楚')}。<br>
只要结论：{lk('s07', '三十秒版本')}。<br>
要落地过监管：{lk('ch13', '落地 SOP 与清单')}。</p>

<div class="sba-h">西红精算是谁</div>
<p><b>用数据讲保险 · 用真心做科普。</b>精算师视角，让风险从模糊变得可度量、可应对。<br>
四根支柱：精算通识 · 风险识别 · 风险应对 · 精算心境。<br>
四条硬规矩：<b>不卖焦虑 · 不讲术语 · 数字有出处 · 结论留退路</b>。</p>

<div class="sba-h">在哪儿找到我们</div>
<p>知识星球「用数据看保险的精算师们」：
<a href="https://t.zsxq.com/JhXu6" target="_blank" rel="noopener">t.zsxq.com/JhXu6</a><br>
姊妹项目：<a href="https://xihongactuary.github.io/risk-map/" target="_blank" rel="noopener">风险地图</a> ·
<a href="https://xihongactuary.github.io/alm-kb/" target="_blank" rel="noopener">ALM 知识库</a> ·
<a href="https://xihongactuary.github.io/ca-alm-kb/" target="_blank" rel="noopener">科目八</a> ·
<a href="https://xihongactuary.github.io/ca-fm-kb/" target="_blank" rel="noopener">财务管理</a> ·
<a href="https://xihongactuary.github.io/cross-solvency/" target="_blank" rel="noopener">偿二代</a> ·
<a href="https://xihongactuary.github.io/cas25-kb/" target="_blank" rel="noopener">CAS25</a></p>
</div>
</details>"""


def side(cur):
    """侧栏：分组标题一律可点（点击折叠 / 展开）。

    之前分组标题是纯文字，看着像能点却点不动，43 页的侧栏又只能一路滚到底。
    现在每段（以及第 2 段下面的每个阶段）都能收起，读哪段就展开哪段。
    """
    tree = []   # [(段标题, [条目], [阶段子组])]
    for item in NAV:
        if item[1] is None:
            if item[0].startswith("阶段") and tree:
                tree[-1][2].append({"t": item[0], "items": []})
            else:
                tree.append([item[0], [], []])
        else:
            node = tree[-1]
            (node[2][-1]["items"] if node[2] else node[1]).append(item)

    h = ['<aside class="side">',
         '<div class="brand">西红<b>精算</b> · AI 实践库</div>',
         '<a class="brand-sub" href="index.html" title="回到知识地图">'
         '场景一 · 找出被错杀的好司机</a>']
    h.append(about_box())
    gid = 0
    for title, items, subs in tree:
        gid += 1
        g = f"g{gid}"
        h.append(f'<button class="nav-title" type="button" data-t="{g}" '
                 f'aria-expanded="true"><span class="nt-t">{title}</span>'
                 f'<span class="caret">▾</span></button>')
        h.append(f'<div class="nav-items" data-i="{g}">')
        for fn, t, no in items:
            h.append(_nav_link(fn, t, no, cur))
        for s in subs:
            gid += 1
            sg = f"g{gid}"
            h.append(f'<button class="nav-title sub" type="button" data-t="{sg}" '
                     f'aria-expanded="true"><span class="nt-t">{s["t"]}</span>'
                     f'<span class="caret">▾</span></button>')
            h.append(f'<div class="nav-items" data-i="{sg}">')
            for fn, t, no in s["items"]:
                h.append(_nav_link(fn, t, no, cur))
            h.append("</div>")
        h.append("</div>")
    b1 = NAV_NO.get("b01", "05")
    h.append('<div class="side-foot">看不懂的词随时查'
             '<a href="glossary.html">术语表</a><br>'
             f'零基础请先读 <a href="b01.html">{b1} · 机器学习到底在干什么</a><br>'
             '数字唯一来源：<code>out/facts.json</code></div>')
    h.append("</aside>")
    return "\n".join(h)



# ------------------------------------------------- 复制到剪贴板（一键复现用）
# 为什么不用 navigator.clipboard：file:// 打开时它不是安全上下文，会直接抛错。
# 所以先试新 API，失败就退回 execCommand，两条路都走不通就提示手动复制。
COPY_JS = """<script>
(function () {
  document.querySelectorAll('button[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var box = btn.parentNode;
      var code = box.querySelector('pre');
      if (!code) return;
      var txt = code.innerText;
      function done() {
        var old = btn.textContent;
        btn.textContent = '已复制';
        btn.className = 'copybtn done';
        setTimeout(function () { btn.textContent = old; btn.className = 'copybtn'; }, 1600);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(txt).then(done, fallback);
      } else { fallback(); }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = txt;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); done(); }
        catch (e) { btn.textContent = '请手动选中复制'; }
        document.body.removeChild(ta);
      }
    });
  });
})();
</script>"""

# 侧栏分组折叠：点标题收起 / 展开该段。纯前端，无依赖，file:// 打开也有效。
NAV_JS = """<script>
(function () {
  document.querySelectorAll('button.nav-title').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var g = btn.getAttribute('data-t');
      var box = document.querySelector('[data-i="' + g + '"]');
      if (!box) return;
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (open) { box.setAttribute('data-hidden', '1'); }
      else { box.removeAttribute('data-hidden'); }
    });
  });
  /* 页脚「关于这个库」：展开侧栏那个折叠块并滚过去。
     <details> 只认 .open，光跳锚点是看不到内容的。 */
  document.querySelectorAll('a[data-about]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var d = document.getElementById('about');
      if (!d) return;
      ev.preventDefault();
      d.open = true;
      d.scrollIntoView({ block: 'start' });
    });
  });
})();
</script>"""

# ------------------------------------------------------ 动画页补链接
# 三个动画页是手写维护的独立文件（不走 ALL 列表），但它们正文里同样在讲
# MSE、基尼、梯度这些词。这里做一次幂等的后处理：加样式 + 加链接。
# 幂等性靠两点：样式只注入一次；link_terms 遇到 <a> 会整段跳过，
# 所以已经链过的词不会被套第二层。
ANIM_PAGES = ("anim_glm", "anim_tree", "anim_gbdt")
TL_CSS = ("\na.tl{color:inherit;text-decoration:none;cursor:help;"
          "border-bottom:1px dotted rgba(47,107,90,.6);}"
          "a.tl:hover{color:#b53d2e;border-bottom-color:#b53d2e;"
          "background:#f7e8e4;border-radius:2px;}\n")


def link_anim():
    for fn in ANIM_PAGES:
        p = os.path.join(ROOT, fn + ".html")
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding="utf-8").read()
        orig = s
        if "a.tl{" not in s:
            s = s.replace("</style>", TL_CSS + "</style>", 1)
        s = link_terms(s, fn)
        if s != orig:
            io.open(p, "w", encoding="utf-8").write(s)
            print("  " + fn + ".html  补术语链接")


def build(fn, no, title, body):
    i = FILES.index(fn)
    prev = FILES[i - 1] if i > 0 else None
    nxt = FILES[i + 1] if i < len(FILES) - 1 else None
    pg = []
    pg.append('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
              '<meta charset="UTF-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
              f'<title>{no} · {title} — AI 实践库</title>\n'
              '<link rel="stylesheet" href="css/style.css">\n</head>\n<body>\n'
              '<div class="layout">')
    pg.append(side(fn))
    pg.append('<main class="main">')
    head, body2 = head_bar(fn, no, body, title)
    body2 = ensure_ids(body2)
    toc, body2 = pull_toc(body2)
    if not toc:
        toc = auto_toc(body2)
    body2, merged = merge_summary(fn, body2)
    body2 = link_terms(body2, fn)
    pg.append(head)
    if toc:
        pg.append(toc)
    pg.append(mlkb_bar(fn))
    if not merged:
        pg.append(plain_box(fn))
    pg.append(body2)
    pg.append(code_bar(fn, body2))
    if fn not in NO_TERMS:
        pg.append(page_terms(fn, body2))
    pg.append('<div class="pager">')
    pg.append(f'<a href="{prev}.html"><span class="dir">◀ 上一页</span>'
              + TITLES[prev] + "</a>" if prev else "<span></span>")
    if nxt:
        pg.append(f'<a class="next" href="{nxt}.html"><span class="dir">下一页 ▶</span>'
                  + TITLES[nxt] + "</a>")
    pg.append('</div>')
    pg.append('<div class="foot">西红精算 · 用数据讲保险 · 用真心做科普<br>'
              '本库全部结论由 <code>ai-kb/code</code> 中的模拟数据与手写模型产生，'
              '数字统一来自 <code>out/facts.json</code>'
              '（三个动画的数字来自 <code>out/anim_facts.json</code>，'
              '由 <code>node code/_animfacts.js</code> 复算），可一键复现。<br>'
              '看不懂的词见 <a href="glossary.html">术语表</a> · '
              f'想看源代码<a href="code.html">代码入口</a> · '
              '读完还是飘？看 <a href="x01.html">一页讲清楚</a> · '
              '<a href="#about" data-about="1">关于这个库 · 关于西红精算</a> · '
              '知识星球：用数据看保险的精算师们</div>')
    pg.append("</main>\n</div>\n" + COPY_JS + "\n" + NAV_JS + "\n</body>\n</html>")
    out = os.path.join(ROOT, fn + ".html")
    io.open(out, "w", encoding="utf-8").write("\n".join(pg))
    print("  " + fn + ".html  " + title)


ALL = list(PAGES_BASIC) + list(PAGES_A) + list(PAGES_B) + list(PAGES_C)
ALL += list(PAGES_UP)
ALL += list(PAGES_TOOL)
ALL.append(("glossary", "G", "术语表 · 中英双语", p_glossary))
ALL.append(("x01", "X", "一页讲清楚：问题 · 方法 · 效果", p_x01))
ALL.append(("p01", "P", "把业务问题翻译成可计算的问题", p_p01))
ALL.append(("x02", "X2", "三个动画 · 各自给出了什么", p_x02))
ALL.append(("code", "C", "代码入口 · 全部源码", p_code))
TITLES = {fn: t for fn, no, t, body in ALL}
# 首页那张地图本身就是入口，再堆六个词反而是挡路 —— 只关掉「本页词语解释」框。
# 但正文里的内联链接照样要：首页也会出现 AUC、错杀这类词，一样该能点。
NO_TERMS = {"index"}
# 内联链接只在术语表自己那页关掉（自己链自己没有意义）
NO_LINK = {"glossary"}

print("构建 AI 实践库：")
print("  源码浏览页 → src/")
_srcdoc.build_all(ROOT)
for fn, no, title, body in ALL:
    # 编号以 NAV 为准：注册处那个 ALL 里的编号是历史遗留，侧栏和页头必须同一个数
    build(fn, NAV_NO.get(fn, no), title, body(F))
link_anim()
print("完成：%d 个页面 → %s" % (len(ALL), ROOT))
