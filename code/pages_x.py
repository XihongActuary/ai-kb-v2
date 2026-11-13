# -*- coding: utf-8 -*-
"""AI 实践库 · X01「一页讲清楚：问题 · 方法 · 效果」+ X02「三个动画 · 一页看懂」

为什么要有这两页：库做到 40 页之后，主线被淹没了——读者读完知道了很多概念，
却说不出「这个实践到底解决了什么问题」。X01 只回答三问，每问先给一句话答案，
再给撑得住这句话的数字，最后给深读入口。

X02 回答另一个方向的迷茫：三个动画看完，画面记住了，但说不清
「它们各自最终解决了什么、公式是什么、代码在哪」。这里用一张表横向对齐，
并点破三者其实是同一个问题的三种答案。

数字全部来自 out/facts.json 与 out/anim_facts.json，不写死。
"""
from pages_a import _toc
from pages_basics import _svg, _cl, INK, GREY, RED, JADE, AMBER, LINE


def _shapes_svg():
    """同一件事的三种画法：一条线 / 一串阶梯 / 一群接力的小树。"""
    g = []
    box = [(20, "一条线", "GLM：光滑、能外推", RED),
           (240, "一串问题", "决策树：阶梯、能解释", JADE),
           (460, "一群接力的小树", "GBDT：画得出 U 形", AMBER)]
    for x0, t1, t2, col in box:
        g.append(f'<rect x="{x0}" y="26" width="180" height="140" rx="8" '
                 f'fill="#fff" stroke="{LINE}"/>')
        g.append(f'<text x="{x0+90}" y="188" font-size="13" fill="{INK}" '
                 f'text-anchor="middle">{t1}</text>')
        g.append(f'<text x="{x0+90}" y="206" font-size="11" fill="{GREY}" '
                 f'text-anchor="middle">{t2}</text>')

    def dots(x0, ys):
        return "".join(
            f'<circle cx="{x0+24+i*20:.0f}" cy="{y}" r="3" fill="rgba(47,107,90,.5)"/>'
            for i, y in enumerate(ys))

    # ① 一条下斜的线（对数链接下是直线，落到原尺度是光滑曲线）
    g.append(dots(20, [64, 54, 74, 60, 46, 52, 40]))
    g.append(f'<path d="M34,66 L184,36" stroke="{RED}" stroke-width="2.4" fill="none"/>')
    # ② 一串阶梯
    g.append(dots(240, [64, 54, 74, 60, 46, 52, 40]))
    g.append(f'<path d="M254,64 H300 V48 H344 V42 H404" stroke="{JADE}" '
             f'stroke-width="2.4" fill="none"/>')
    # ③ 阶梯逼近 U 形
    g.append(dots(460, [50, 78, 112, 132, 124, 92, 58]))
    g.append(f'<path d="M474,44 Q554,152 634,44" stroke="{INK}" stroke-width="1.8" '
             f'fill="none" stroke-dasharray="5,4"/>')
    g.append(f'<path d="M474,48 H506 V96 H540 V130 H574 V100 H608 V62 H634" '
             f'stroke="{AMBER}" stroke-width="2.4" fill="none"/>')
    return _svg(660, 218, "".join(g),
                "同一堆数据的三种画法。选模型，其实是在选「你相信这个世界长什么样」："
                "相信是光滑的斜坡就用 GLM，相信是一档一档的台阶就用树，"
                "相信有拐点有 U 形就用 GBDT——代价是更难解释、更容易过拟合。")


def p_x02(F):
    A = F.get("anim") or {}
    glm = A.get("glm") or {}
    tr = A.get("tree") or {}
    gb = A.get("gbdt") or {}
    s1 = tr.get("s1") or {}
    s3 = tr.get("s3") or {}
    return f"""
<h1><span class="thin">起步 · 三个动画</span>
一页看懂：三个动画各自给出了什么</h1>
<p class="lead">动画好看，看完容易只记住画面。这一页把三件事钉死：
<b>它们各自最终解决了什么问题、最终的数学表达式是什么、代码在哪</b>。
一句话先说在前面：<b>三个动画在做同一件事，区别只有一个——你允许这条规律长成什么样。</b></p>

{_toc([("one", "先给一句话：它们在解同一道题"), ("tbl", "一页总览：三个动画横向对齐"),
       ("num", "跑完之后的真实数字"), ("role", "在本案例里各自是什么角色"),
       ("code", "代码入口：点开就能看"), ("end", "一句话带走")])}

<h2 id="one">先给一句话：它们在解同一道题</h2>
<div class="ans-a">三个动画都在解同一道题：<b>找一组参数，让「猜错的代价」最小</b>。
真正的区别只有一个，而且是个<b>信念问题</b>——你允许这条规律长成什么样。</div>

<div class="tbl-wrap"><table class="tbl">
<tr><th>如果你相信</th><th>那就用</th><th>你换来了什么</th><th>你付出了什么</th></tr>
<tr><td>风险随因子<b>平滑变化</b>、越远越单调</td><td><b>GLM</b>（一条线）</td>
    <td>系数能直接读（年龄每大一岁，出险降 {glm.get('drop_pct','—')}%）；
        外推稳；<b>预测值恒为正</b></td>
    <td>画不出拐点和交互作用</td></tr>
<tr><td>人是<b>一档一档</b>的，存在阈值</td><td><b>决策树</b>（一串问题）</td>
    <td>每条路径都能翻译成一句人话，监管沟通最友好</td>
    <td>阶梯形天生粗糙，容易把巧合当成规律</td></tr>
<tr><td>既有拐点、又有<b>交互作用</b>（年轻 且 开性能车）</td><td><b>GBDT</b>（一群小树）</td>
    <td>能画出 U 形和陡峭的组合效应，精度天花板最高</td>
    <td>难解释、吃数据、吃调参，<b>还特别容易过拟合</b></td></tr>
</table></div>

{_shapes_svg()}

<h2 id="tbl">一页总览：三个动画横向对齐</h2>
<div class="tbl-wrap"><table class="tbl">
<tr><th>动画</th><th>它最终解决了什么问题</th><th>最终的数学表达式</th>
    <th>跑完拿到手的东西</th></tr>

<tr><td><b>① GLM<br>迭代</b><br>
    <a href="ch04.html">CH04</a></td>
    <td>把一堆散点变成<b>一条能拿去定价的曲线</b>，
        并从数学结构上保证它永远为正</td>
    <td>μ(x) = exp(β₀ + β₁x)<br>
        β⁽ᵗ⁺¹⁾ = (XᵀWX)⁻¹XᵀWz<br>
        <small>z = η + (y−μ)/μ，W = diag(w·μ)</small></td>
    <td>β₀ = {glm.get('b0','—')}、β₁ = {glm.get('b1','—')}<br>
        → 年龄每大一岁，出险降 <b>{glm.get('drop_pct','—')}%</b><br>
        偏差 {glm.get('dev0','—')} → {glm.get('dev_end','—')}</td></tr>

<tr><td><b>② 决策树<br>挑问题</b><br>
    <a href="ch05.html">CH05</a></td>
    <td>不写公式，只靠一串「是 / 否」，
        把人群切出<b>能翻译成人话的分组</b></td>
    <td>选 argmax Gain(a,t)：<br>
        Gain = Gini(父) − [n_L/n·Gini(左) + n_R/n·Gini(右)]<br>
        Gini = 2p(1−p)</td>
    <td>{tr.get('n_splits','—')} 个问题、{len(tr.get('leaves') or []) or '—'} 片叶子；
        最纯的一叶 {round((tr.get('purest') or {}).get('p',0)*100) if tr.get('purest') else '—'}% 高风险，
        最脏的一叶 {round((tr.get('dirtiest') or {}).get('p',0)*100) if tr.get('dirtiest') else '—'}%</td></tr>

<tr><td><b>③ GBDT<br>逐轮补差</b><br>
    <a href="ch06.html">CH06</a></td>
    <td>一条直线画不出来的形状（U 形、拐点）怎么办——
        <b>用一群笨树接力补差</b></td>
    <td>F_M(x) = F₀ + η·Σ<sub>t=1..M</sub> f_t(x)<br>
        f_t ≈ −∂L/∂F（平方损失下 = y − F）<br>
        <small>η = {gb.get('lr','—')}，树深 {gb.get('max_depth','—')}</small></td>
    <td>{gb.get('rounds','—')} 轮把 MSE 从 {(gb.get('mse') or ['—'])[0]} 压到
        {(gb.get('mse') or ['—'])[-1]}；
        噪声地板 {gb.get('noise_emp','—')} → <b>第 {max(len(gb.get('mse') or [0])-2,0)} 轮之后就该停</b></td></tr>
</table></div>

<h2 id="num">跑完之后的真实数字</h2>
<p>这三个动画里的数不是画上去的，是真跑出来的（算法写在动画自己的
<code>&lt;script&gt;</code> 里，随机种子固定）。下面这些数字由
<code>node code/_animfacts.js</code> 复算后写进 <code>out/anim_facts.json</code>，
页面再从那里取值——和全站「数字只有一个来源」是同一条规矩。</p>

<div class="tbl-wrap"><table class="tbl">
<tr><th>动画</th><th>起点</th><th>终点</th><th>该怎么读这一行</th></tr>
<tr><td><b>GLM</b></td><td>β = (0, 0)，偏差 {glm.get('dev0','—')}</td>
    <td>β = ({glm.get('b0','—')}, {glm.get('b1','—')})，偏差 {glm.get('dev_end','—')}</td>
    <td>收敛值 β₁ = {glm.get('b1','—')} 和数据里埋的真值 {glm.get('b1_true','—')}
        只差 {abs(glm.get('b1',0)-glm.get('b1_true',0)):.4f}——<b>规律被找回来了</b></td></tr>
<tr><td><b>决策树</b></td><td>{tr.get('n','—')} 人，{tr.get('n_risk','—')} 个高风险，
    不纯度 {tr.get('root_gini','—')}</td>
    <td>切了 {tr.get('n_splits','—')} 刀</td>
    <td>第一刀「{(s1.get('attr')=='age' and '年龄' or '年里程')} ≤ {s1.get('thr','—')}」
        收益 {s1.get('gain','—')}：左边 {s1.get('nL','—')} 人里
        {round(s1.get('pL',0)*100) if s1 else '—'}% 高风险，右边 {s1.get('nR','—')} 人里
        {round(s1.get('pR',0)*100) if s1 else '—'}%；
        <b>第三刀收益只有 {s3.get('gain','—')}，几乎白切</b>——
        收益 = 切之前的不纯度 − 切之后的加权不纯度，
        <a href="ch05.html#howgain">手算过程见 CH05</a></td></tr>
<tr><td><b>GBDT</b></td><td>MSE {(gb.get('mse') or ['—'])[0]}（预测恒为 0）</td>
    <td>MSE {(gb.get('mse') or ['—'])[-1]}</td>
    <td>数据本身带的噪声是 {gb.get('noise_emp','—')}。
        <b>第 {len(gb.get('mse') or [])-2} 轮已经贴平，第 {len(gb.get('mse') or [])-1} 轮反而更低——
        那多出来的不是本事，是背噪声</b></td></tr>
</table></div>

<h2 id="role">在本案例里，它们各自是什么角色</h2>
<p>这一节很重要，因为它能治好「学了一堆模型，不知道用哪个」的迷茫——
<b>本案例不是三个都用上了，而是用比赛结果决定谁上场</b>：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>动画</th><th>在本案例里的角色</th><th>证据</th></tr>
<tr><td><b>GLM</b></td><td><b>主力</b>：频率链用它</td>
    <td>组合③「频率 GLM × 损失均值」AUC {F['combos'][2]['auc']}、Top20% 纯度 {F['combos'][2]['purity']}%，
        是全场最好的组合</td></tr>
<tr><td><b>决策树</b></td><td><b>主力</b>：损失额链用它（单棵）</td>
    <td>组合①「频率 GLM × 损失单树」AUC {F['combos'][0]['auc']}；
        它还是 GBDT 的积木，以及 <code>export_rules</code> 生成可解释规则的来源</td></tr>
<tr><td><b>GBDT</b></td><td><b>对照组：打了败仗</b></td>
    <td>组合②「频率 GBDT × 损失单树」AUC {F['combos'][1]['auc']}
        &lt; 组合①的 {F['combos'][0]['auc']}。
        本案例的频率规律接近线性，树和 GBDT 的灵活性用不上，反而先过拟合了</td></tr>
</table></div>
<div class="note jade"><b>这条结论比学会三个模型更值钱：</b>
不是「哪个模型更高级就用哪个」，而是<b>「让数据决定」</b>。
样本只有几万、规律接近线性的时候，GLM 赢；样本上十万、真有交互作用的时候，GBDT 才会翻盘。
工具先进不等于工具合适。</div>

<h2 id="code">代码入口：点开就能看</h2>
<p>每个动画都有两套代码：<b>动画自己那份</b>（十几行，为了让你看懂）
和<b>案例里那份</b>（带权重、正则、停止条件，真能跑业务）。行号在构建时现算，改了代码重建就自动对齐。</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>动画</th><th>动画源码（教学版）</th><th>案例源码（工业版）</th></tr>
<tr><td>GLM</td>
    <td>{_cl("anim_glm", "function irlsStep", None, "irlsStep")} ·
        {_cl("anim_glm", "function deviance", None, "deviance")}</td>
    <td>{_cl("models", "def fit", None, "PoissonRegressor.fit", nth=0)} ·
        {_cl("models", "def poisson_deviance", None, "poisson_deviance")}</td></tr>
<tr><td>决策树</td>
    <td>{_cl("anim_tree", "function gini", None, "gini")} ·
        {_cl("anim_tree", "function splitGain", None, "splitGain")}</td>
    <td>{_cl("models", "def _best_split", None, "_best_split")} ·
        {_cl("models", "def _build", None, "_build")} ·
        {_cl("models", "def export_rules", None, "export_rules")}</td></tr>
<tr><td>GBDT</td>
    <td>{_cl("anim_gbdt", "function fitStump", None, "fitStump")} ·
        {_cl("anim_gbdt", "for(var r=0;r<M;r++)", None, "主循环")}</td>
    <td>{_cl("models", "def fit", None, "GBDT.fit", nth=3)} ·
        {_cl("models", "def _set_leaf_values", None, "_set_leaf_values")}</td></tr>
</table></div>
<p>逐段讲解（每一步在干什么、为什么这么写）在各自的动画页里：
<a href="ch04.html#wrap">CH04 收个尾</a> ·
<a href="ch05.html#wrap">CH05 收个尾</a> ·
<a href="ch06.html#wrap">CH06 收个尾</a>。</p>

<h2 id="end">一句话带走</h2>
<div class="quote q-warn"><span class="q-tag">最后一句</span>
<p>三个动画看起来是三种技术，其实是一个问题的三种答案：
<b>你打算让机器用多复杂的形状去贴近现实。</b>
越复杂的形状越贴合历史数据，也越容易把噪声当规律——
所以本案例最后选了<b>最朴素的那个组合</b>（GLM 频率 × 单树损失，AUC {F['combos'][2]['auc']}），
而不是最先进的那个。<b>这不是保守，这是被数字选出来的。</b></p></div>
<p>深读：<a href="x01.html">X01 一页讲清楚（问题 · 方法 · 效果）</a> ·
<a href="b12.html">B12 怎么选模型</a> ·
<a href="m01.html">M01 常见模型速查</a> ·
<a href="b10.html">B10 端到端七步</a></p>
"""


def _main_svg(F):
    """一张图说完：20,000 人 → 承保/拒保两支 → 好人 → 排号 → 复核 4,400。"""
    inner = f"""
<defs><marker id="ax" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
<path d="M0,0 L8,4 L0,8 z" fill="{GREY}"/></marker></defs>

<rect x="247" y="8" width="150" height="44" rx="8" fill="#fff" stroke="{LINE}"/>
<text x="322" y="26" font-size="13" fill="{INK}" text-anchor="middle">{F['n_total']:,} 个投保申请</text>
<text x="322" y="42" font-size="11.5" fill="{GREY}" text-anchor="middle">全部</text>

<path d="M322 52 L322 68 L165 68 L165 88" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>
<path d="M322 52 L322 68 L479 68 L479 88" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>

<rect x="40" y="88" width="250" height="58" rx="8" fill="#e6efe9" stroke="{JADE}"/>
<text x="165" y="110" font-size="13" fill="{JADE}" text-anchor="middle">承保 {F['n_acc']:,} 人 · {F['pct_acc']:.0f}%</text>
<text x="165" y="130" font-size="11.5" fill="{GREY}" text-anchor="middle">有出险记录 → 看得见</text>

<rect x="354" y="88" width="250" height="58" rx="8" fill="#f7e8e4" stroke="{RED}"/>
<text x="479" y="110" font-size="13" fill="{RED}" text-anchor="middle">拒保 {F['n_rej']:,} 人 · {F['pct_rej']:.0f}%</text>
<text x="479" y="130" font-size="11.5" fill="{GREY}" text-anchor="middle">没有出险记录 → 看不见</text>

<path d="M165 146 L165 166" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>
<path d="M479 146 L479 166" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>

<rect x="40" y="166" width="250" height="58" rx="8" fill="#fff" stroke="{LINE}"/>
<text x="165" y="188" font-size="13" fill="{INK}" text-anchor="middle">用看得见的人，学出规律</text>
<text x="165" y="206" font-size="11.5" fill="{GREY}" text-anchor="middle">拆成「频率 × 损失」分别建模</text>

<rect x="354" y="166" width="250" height="58" rx="8" fill="#f6ecd6" stroke="{AMBER}"/>
<text x="479" y="188" font-size="13" fill="{AMBER}" text-anchor="middle">其中 {F['n_wrongly_killed']:,} 人是好人 · {F['pct_killed_of_rej']}%</text>
<text x="479" y="206" font-size="11.5" fill="{GREY}" text-anchor="middle">真实纯保费 {F['true_prem_killed']:.0f} 元 &lt; 好司机线 {F['good_threshold']:,.0f} 元</text>

<path d="M165 224 L165 236 L250 236 L250 246" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>
<path d="M479 224 L479 236 L394 236 L394 246" stroke="{GREY}" stroke-width="1.6" fill="none" marker-end="url(#ax)"/>

<rect x="170" y="246" width="304" height="58" rx="8" fill="#e6efe9" stroke="{JADE}"/>
<text x="322" y="268" font-size="13" fill="{JADE}" text-anchor="middle">模型排号 → 人工复核最前的 {F['thr_peak_n']:,} 件</text>
<text x="322" y="286" font-size="11.5" fill="{GREY}" text-anchor="middle">年增益 {F['thr_peak_gain']:,.0f} 元 · 单件复核成本盈亏线 {F['thr_peak_gain']/F['thr_peak_n']:.0f} 元</text>

<text x="322" y="320" font-size="11.5" fill="{GREY}" text-anchor="middle">原来 {F['n_rej']:,} 件才找得完，现在复核一半就找回了大部分</text>
"""
    return _svg(644, 330, inner,
                "全库的主线就这一张图：左边是「看得见的世界」，右边是「看不见的世界」，"
                "模型做的事是把右边的人排个号。")


def p_x01(F):
    lift = F['extrap']['A']['purity20_all'] / F['purity20_base']
    be = F['thr_peak_gain'] / F['thr_peak_n']
    onl = F['by_channel'][2]
    dr = F['bias'][3]
    raw = F['bias'][0]
    only = F['bias'][2]
    return f"""
<h1><span class="thin">起步 · 先看这一页</span>
一页讲清楚：问题 · 方法 · 效果</h1>
<p class="lead">如果这个库你读了好几页还是有点飘，就来这一页。它只回答三个问题：
<b>解决了什么问题、用了什么方法、达到了什么效果</b>。每个答案一句话说清，
再给撑得住这句话的数字，最后告诉你去哪几页深读。</p>

{_toc([("ans", "先给一句话"), ("q1", "第一问：解决什么问题"),
       ("q2", "第二问：采用什么方法"), ("q3", "第三问：达到什么效果"),
       ("not", "更重要的是：它没做到什么"), ("five", "五分钟深读路线")])}

<h2 id="ans">先给一句话</h2>
<div class="quote q-talk"><span class="q-tag">一句话</span>
<p>这个实践<b>不是让模型替谁做决定</b>，它只解决一件很窄的事：
<b>在被规则拒掉的 {F['n_rej']:,} 个人里，先复核谁？</b></p>
<p>做法：让模型给他们<b>排个号</b>，人去复核排在最前面的 {F['thr_peak_n']:,} 个。
原来 {F['n_rej']:,} 件才找得完，现在复核一半就找回了大部分——
<b>省下的那一半人工，就是这套东西赚的钱。</b></p></div>
<div class="note jade"><b>如果只能记一句：</b>模型是<b>排队机</b>，不是裁判。
它不决定谁对谁错，只决定<b>谁先被看</b>。</div>

{_main_svg(F)}

<h2 id="q1">第一问：到底解决什么问题？</h2>
<div class="ans-a">核保规则拒掉的 {F['n_rej']:,} 人里，有 <b>{F['n_wrongly_killed']:,} 人的真实风险比已承保客户还低</b>。
他们被冤枉了，而公司<b>永远看不见这件事</b>——因为被拒的人不在公司，不会有出险记录。</div>

<p>把这句话拆开，它由三个事实叠起来：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>事实</th><th>数字</th><th>为什么它是个问题</th></tr>
<tr><td><b>错杀是真的</b></td>
    <td>{F['n_wrongly_killed']:,} 人，占拒保件 {F['pct_killed_of_rej']}%</td>
    <td>他们的真实纯保费只有 {F['true_prem_killed']:.0f} 元，
        比已承保客户的中位数 {F['good_threshold']:,.0f} 元<b>还低</b>——这不是边缘客户，是好客户</td></tr>
<tr><td><b>看不见</b></td>
    <td>承保 {F['n_acc']:,} 人有记录<br>拒保 {F['n_rej']:,} 人没记录</td>
    <td>人不在公司，就永远不会有出险记录。<b>没有记录 ≠ 没有风险，但也 ≠ 有风险</b>——
        规则默认当成了「有风险」</td></tr>
<tr><td><b>错得有规律</b></td>
    <td>线上渠道错杀率 {F['kill_by_channel'][2]['kill_rate']}%<br>
        是代理渠道 {F['kill_by_channel'][0]['kill_rate']}% 的 {F['kill_ratio_online_vs_agent']} 倍</td>
    <td>规则把「<b>信息好不好查</b>」当成了「<b>风险高不高</b>」。
        线上客户不是更爱出事，只是资料不全、不好核实</td></tr>
</table></div>
<div class="note red"><b>所以真正的损失不是保费。</b>是这套规则在<b>系统性地歧视公司最便宜的那个获客渠道</b>，
而且因为看不见，没人会去改它。</div>
<p>深读：<a href="index.html">总览</a> ·
<a href="s01.html">当下是怎么做的</a>（为什么现有办法发现不了） ·
<a href="b02.html">数据长什么样</a>（−1 不是 0） ·
<a href="ch07.html">选择偏差</a></p>

<h2 id="q2">第二问：到底采用什么方法？</h2>
<div class="ans-a">不是「训练一个模型」，是<b>四步流水线</b>：
<b>拆开了学 → 把歪掉的样本掰正 → 外推时只排序不定价 → 圈选阈值贴着盈亏平衡点定</b>。
每一步都对应一个会翻车的坑，也都有数字作证。</div>

<div class="steps">
<div class="step"><h4>拆成「出险频率 × 案均损失」分别建模</h4>
<p>绝大多数人不出险，直接预测纯保费会被大量的 0 搅乱。证据很硬：
直接预测纯保费的 Poisson GLM，偏差 {F['dev_wall'][1]['dev']:,.1f}，
比什么都不做的常数基线 {F['dev_wall'][0]['dev']:,.1f} <b>还差</b>——等于完全没学会。
拆开之后：AUC {F['combos'][2]['auc']}，Top 20% 纯度 {F['combos'][2]['purity']}%。</p>
<p>深读 <a href="ch03.html">CH03 频率 × 损失</a> · <a href="b10.html">B10 七步流程</a></p></div>

<div class="step"><h4>给被抽歪的审计样本加权（IPW / 双重稳健）</h4>
<p>人工核查只做了 {F['n_aud']} 件（{F['pct_aud']}%），而且抽样偏向「看起来可疑的」。
不加权直接估：{raw['est']:,.1f} 元（偏差 {raw['bias']:+.1f}）；
只靠模型往外推：{only['est']:,.1f} 元（偏差 <b>{only['bias']:+.1f}</b>，离谱）；
双重稳健 DR：{dr['est']:,.1f} 元（偏差 {dr['bias']:+.1f}）。真值 {F['bias_true']:,.1f} 元。</p>
<p>深读 <a href="ch08.html">CH08 IPW 与双重稳健</a></p></div>

<div class="step"><h4>外推到没见过的人时，只用它排序，不用它定价</h4>
<p>给 {F['n_rej']:,} 个从没见过的人打分：<b>排序能力还在</b>（AUC {F['extrap']['A']['auc_all']}），
但<b>数值整体虚高 {(F['calib_A']-1)*100:.1f}%</b>（预测均值 {F['pred_mean_A']:,.0f} 元 vs 真值 {F['bias_true']:,.1f} 元）。
所以落地方案是：<b>只排号，不报价</b>。</p>
<p>深读 <a href="ch09.html">CH09 外推风险</a> · <a href="b08.html">B08 排序准 ≠ 数字准</a></p></div>

<div class="step"><h4>圈选阈值贴着「盈亏平衡」定，不是贴着中位数定</h4>
<p>圈太少漏掉好人，圈太多白花人工，中间有个最优点：
圈 {F['thr_curve'][2]['n']:,} 件增益 {F['thr_curve'][2]['gain']:,.0f} 元 →
圈 {F['thr_peak_n']:,} 件<b>峰值 {F['thr_peak_gain']:,.0f} 元</b> →
圈 {F['thr_curve'][5]['n']:,} 件反而降到 {F['thr_curve'][5]['gain']:,.0f} 元 →
全圈 = {F['thr_curve'][6]['gain']:.0f} 元。<b>倒 U 形，不是越多越好。</b></p>
<p>深读 <a href="ch10.html">CH10 业务账与圈选阈值</a> · <a href="s03.html">S03 投入产出账</a></p></div>
</div>

<h2 id="q3">第三问：到底达到什么效果？</h2>
<div class="ans-a">把「在 {F['n_rej']:,} 个看不见的人里找好人」这道题，
做成了「<b>复核 {F['thr_peak_n']:,} 件就找回大部分</b>」，
而且只要<b>单件复核成本低于 {be:.0f} 元就划算</b>。</div>

<div class="stat-grid">
  <div class="stat"><div class="v">{F['interp']['A']['auc']}</div>
    <div class="k">内插 AUC（熟悉人群）<br>0.5 = 瞎猜，1.0 = 完美</div></div>
  <div class="stat"><div class="v">{F['extrap']['A']['auc_all']}</div>
    <div class="k">外推 AUC（全部 {F['n_rej']:,} 人）<br>排序能力没崩</div></div>
  <div class="stat"><div class="v">{lift:.1f}<small> 倍</small></div>
    <div class="k">Top 20% 纯度 {F['extrap']['A']['purity20_all']}%<br>÷ 随机基线 {F['purity20_base']}%</div></div>
  <div class="stat"><div class="v">{onl['precision']:.0f}<small>%</small></div>
    <div class="k">线上渠道圈选精度<br>圈 {onl['n_flag']} 个，{onl['precision']:.0f}% 是好人</div></div>
  <div class="stat"><div class="v">{F['thr_peak_gain']/10000:,.1f}<small> 万元</small></div>
    <div class="k">圈 {F['thr_peak_n']:,} 件的年增益<br>比随机圈多赚的钱</div></div>
  <div class="stat"><div class="v">{be:.0f}<small> 元/件</small></div>
    <div class="k">单件复核成本盈亏线<br>低于它就赚，高于它就亏</div></div>
</div>

<p>分渠道看，效果不平均——<b>错杀最狠的渠道，模型也最准</b>：</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>渠道</th><th class="num">被拒人数</th><th class="num">其中好人</th>
    <th class="num">规则错杀率</th><th class="num">模型圈选精度</th></tr>
{''.join(f'<tr><td>{c["channel"]}</td><td class="num">{c["n"]:,}</td>'
         f'<td class="num">{c["n_good"]:,}</td>'
         f'<td class="num">{k["kill_rate"]}%</td>'
         f'<td class="num">{c["precision"]}%</td></tr>'
         for c, k in zip(F['by_channel'], F['kill_by_channel']))}
</table></div>
<div class="tbl-cap">线上渠道被规则错杀 {F['kill_by_channel'][2]['kill_rate']}%（最高），
模型在那里圈出来的 {onl['precision']:.0f}% 是真好人（也最高）——
被规则伤得最深的地方，恰恰是模型最能帮上忙的地方。</div>

<h2 id="not">更重要的是：它没做到什么</h2>
<p>这四条比前面三问更该记住。一个实践值不值得信，不看它做到了什么，看它<b>有没有说清自己没做到什么</b>。</p>
<div class="tbl-wrap"><table class="tbl">
<tr><th>没做到</th><th>数字</th><th>所以怎么办</th></tr>
<tr><td><b>不能拿去定价</b></td>
    <td>预测值整体虚高 {(F['calib_A']-1)*100:.1f}%</td>
    <td>只用它<b>排序</b>，费率仍走原口径</td></tr>
<tr><td><b>离训练域远的人不准</b></td>
    <td>近点纯度 {F['extrap']['A']['purity20_near']}% → 全体 {F['extrap']['A']['purity20_all']}%，
        掉 {abs(F['purity_drop'])} 个点</td>
    <td>远点（{F['n_far']:,} 人）只做保守处理，第一年不动</td></tr>
<tr><td><b>模型不拍板</b></td>
    <td>—</td>
    <td>模型只排号，<b>最终承保决定仍由人做</b>；这不是保守，是这套方案的定义</td></tr>
<tr><td><b>数据是模拟的</b></td>
    <td>—</td>
    <td>验证的是<b>方法能不能跑通、会在哪翻车</b>，不是某家公司的真实收益</td></tr>
</table></div>
<p>深读：<a href="ch13.html">CH13 落地 SOP 与边界</a> ·
<a href="s04.html">S04 上线之后</a>（风险从上线才开始） ·
<a href="s02.html">S02 不用机器学习行不行</a></p>

<h2 id="five">五分钟深读路线</h2>
<div class="note jade">如果你是被<b>三个动画</b>看懵的：先看
<a href="x02.html">X02 三个动画 · 各自给出了什么</a>——一张表横向对齐，
每个动画解决什么问题、公式怎么读、代码在哪。</div>
<div class="card-grid">
  <a class="card" href="s07.html">
    <div class="no">路线一</div><div class="t">要拿去汇报</div>
    <p class="d">S07 三十秒版本：一段电梯演讲、三句分对象的话、六问六答。</p>
    <span class="tag">5 分钟</span></a>
  <a class="card" href="b10.html">
    <div class="no">路线二</div><div class="t">想搞懂怎么做</div>
    <p class="d">B10 七步流程 → CH03 拆频率与损失 → CH08 纠偏 → CH10 圈选阈值。</p>
    <span class="tag">40 分钟</span></a>
  <a class="card" href="ch13.html">
    <div class="no">路线三</div><div class="t">要决定上不上</div>
    <p class="d">S03 投入产出账 → S04 上线之后 → S06 谁来干 → CH13 落地清单。</p>
    <span class="tag">30 分钟</span></a>
</div>
<div class="quote q-warn"><span class="q-tag">最后一句</span>
<p><b>机器学习在这件事上的价值，不是「更准」，而是「更省」。</b>
它省下的不是判断，是<b>判断之前的那次翻牌</b>——
原来 {F['n_rej']:,} 张牌要一张张翻，现在先翻 {F['thr_peak_n']:,} 张就够了。</p></div>
"""
