# -*- coding: utf-8 -*-
"""
步骤 6-8：真正的战场
================================================================================
本文件是 train_evaluate.py 的下游模块，依赖步骤 4-5 产出的 fitted 字典。

fitted 中每个元素的结构：
    dict(tag, use_ch, names, combo, freq_m, sev_m, sev_const,
         auc, purity, dev, base, wall)

核心主张（全案例的题眼）：
    训练数据里从来没有「被拒保的人」。
    所以对他们的预测本质是外推。
    所有难点、偏差、谨慎，都从这一句话来。
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_evaluate import build_design, hr, sub, OUT


def _live_module():
    """
    找到【真正在执行】的那份 train_evaluate 模块。

    ★ 这是一个很容易踩、而且不报错的坑：
      直接 `python train_evaluate.py` 时，本模块在 sys.modules 里的名字是
      `__main__`；而下面 `from train_evaluate import ...` 又按模块名
      **再加载一份全新的副本**，并注册为 `train_evaluate`。
      于是 sys.modules 里同时存在两份模块对象，它们各有各的全局变量。
      步骤 2 设的 GOOD_PREMIUM 写进了 `__main__` 那份，
      这里从 `train_evaluate` 那份读，读到的永远是 None。
    """
    for name in ("__main__", "train_evaluate"):
        m = sys.modules.get(name)
        if m is not None and getattr(m, "__file__", None) and \
                os.path.basename(m.__file__) == "train_evaluate.py":
            if getattr(m, "GOOD_PREMIUM", None) is not None:
                return m
    return sys.modules.get("train_evaluate")


def good_premium():
    """阈值在步骤 2 才确定，所以这里必须动态取，不能在 import 时快照。"""
    return float(_live_module().GOOD_PREMIUM)


# ==============================================================================
# 通用：纯保费预测
# ==============================================================================
def pp_predict(f, X):
    """
    纯保费 = 预测频率 × 预测损失。

    f 是 step45_models 产出的 fitted 字典。
    组合③（损失用常数均值）时 sev_m 为 None，自动退化为「频率 × 平均损失」。
    注意：损失模型是在 log 尺度上训练的，这里必须 exp 回来。
    """
    freq = np.clip(f["freq_m"].predict(X), 1e-6, None)
    if f["sev_m"] is None:
        sev = np.asarray(float(f.get("sev_const", 0.0)))
    else:
        sev = np.exp(np.clip(f["sev_m"].predict(X), -5.0, 12.0))
    return freq * sev


# ==============================================================================
# 外推距离（OOD）：拒保人群离训练中心有多远？
# ==============================================================================
def ood_scale(Xa):
    """
    返回 (均值, 尺度, 无变异列掩码)。

    ★ 这里有一个非常隐蔽、而且会把结果彻底带偏的坑：
      本案例里「营运」这个哑变量在【承保人群中恒等于 0】（因为营运车全被拒了）。
      它的标准差就是 0。
      如果照教科书写 sd = X.std() + 1e-9，分母就成了 1e-9，
      拒保人群里只要出现一个营运车，那个人的标准化距离就是 1/1e-9 ≈ 十亿，
      平均距离会被拉到几千万 —— 一个纯粹由数值除零造成的假信号。

    工程上正确的做法：给「训练集中无变异」的列一个先验尺度。
    对 0/1 哑变量，p≈0.5 时的标准差是 sqrt(0.5×0.5)=0.5，就用 0.5。
    """
    mu = Xa.mean(axis=0)
    sd = Xa.std(axis=0)
    ref = float(sd.max()) if sd.max() > 0 else 1.0
    flat = sd < 1e-6 * ref
    sd = np.where(flat, 0.5, sd)
    return mu, sd, flat


def ood_dist(X, mu, sd):
    """RMS 标准化距离：一个样本在所有维度上平均偏离训练中心多少个标准差。"""
    z = (X - mu) / sd
    return np.sqrt((z ** 2).mean(axis=1))


# ==============================================================================
# 步骤 6：给拒保人群打分
# ==============================================================================
def step6_rejected(df, fitted):
    hr("步骤 6 / 8    给拒保人群打分：真正的战场在这里")
    rej = df[df.accept == 0].copy().reset_index(drop=True)
    acc = df[df.accept == 1]
    print(f"被拒保 {len(rej):,} 件。它们的出险记录全部不可见（claim_cnt = -1）。")
    print("我们做的事，本质上是：拿「只见过被放行的人」训练出来的模型，")
    print("去预测「从来没被放行过的人」。")
    print("  >>> 这是外推，不是内插。所以必须诚实地评估外插质量。")

    print("\n【两种评估视角，缺一不可】")
    print("  内插视角（承保人群，标签可见）→ 衡量模型的基本功")
    print("  外插视角（拒保人群，靠审计样本）→ 衡量模型能不能拿去用")
    print("  内插漂亮 ≠ 外插能用。反过来同样不成立。")

    # ---- 6.1 外推距离：用【风险相关特征】衡量，不含 channel ------------------
    sub("6.1  外推有多远？用标准化距离量化")
    Xa0, names0 = build_design(acc, use_channel=False)
    Xr0, _ = build_design(rej, use_channel=False)
    mu0, sd0, flat0 = ood_scale(Xa0)

    n_flat = int(flat0.sum())
    if n_flat:
        fl = [names0[i] for i in np.where(flat0)[0]]
        print(f"  ⚠ 训练集中【无变异】的列：{'、'.join(fl)}（恒为同一个取值）")
        print("    教科书写法 sd = std + 1e-9 会让这些列的分母变成 1e-9，")
        print("    拒保人群里只要出现一次，距离就被除到十亿量级 —— 纯数值假信号。")
        print("    本步骤给无变异列套用先验尺度 0.5（0/1 哑变量 p=0.5 的标准差）。")

    d_acc = ood_dist(Xa0, mu0, sd0)          # 承保人群自己的距离（参照系）
    d_rej = ood_dist(Xr0, mu0, sd0)          # 拒保人群的距离
    # 阈值不用拍脑袋的 3σ，而是用「承保人群自己的距离分布」定标：
    # 训练集内样本的距离都不是 0，所以「远点」必须相对而言。
    thr = float(d_acc.mean() + 2 * d_acc.std())
    far = d_rej > thr

    print(f"\n  承保人群自身距离（参照）  均值 {d_acc.mean():.3f}  "
          f"P95 {np.quantile(d_acc, 0.95):.3f}")
    print(f"  拒保人群距离              均值 {d_rej.mean():.3f}  "
          f"P95 {np.quantile(d_rej, 0.95):.3f}  最大 {d_rej.max():.3f}")
    print(f"  「远点」判定线 = 承保均值 + 2σ = {thr:.3f}")
    print(f"  远点 {int(far.sum()):,} 件，占被拒保件 {far.mean():.1%}")
    print(f"  >>> 拒保人群整体确实在训练分布的边缘，但 {1-far.mean():.0%} 的件")
    print("      仍落在承保人群的正常波动范围内 —— 也就是说，")
    print("      「外推」不等于「不可用」，但外推的那部分必须单独标记。")

    # ---- 6.2 分渠道看距离：错杀的主因在这里 ---------------------------------
    sub("6.2  外推距离按渠道拆开看")
    print(f"  {'渠道':<10}{'件数':>8}{'平均距离':>10}{'远点占比':>10}{'真实纯保费':>12}")
    rows = []
    for nm in ["代理渠道", "直销渠道", "线上渠道"]:
        m = (rej.channel_nm == nm).values
        rows.append((nm, int(m.sum()), d_rej[m].mean(), far[m].mean(),
                     rej._true_premium.values[m].mean()))
    for nm, a, dd, ff, tp in rows:
        print(f"  {nm:<10}{a:>8,}{dd:>10.3f}{ff:>9.1%}{tp:>12,.0f}")
    print("  >>> 线上渠道既离训练中心更远、错杀率又最高。")
    print("      这两件事其实是同一件事：线上渠道缺信息 → 规则加分 → 被拒。")
    print("      我们的模型要做的，就是把这层「信息不足的惩罚」摘掉。")

    # ---- 6.3 逐模型打分（每个模型必须用它自己的设计矩阵！）------------------
    sub("6.3  逐模型对拒保人群打分")
    scores = {}
    for f in fitted:
        key = "A" if not f["use_ch"] else "B"
        # ★ 关键：设计矩阵必须按模型各自的特征集重新构造。
        #   A 不用 channel → 11 列；B 用 channel → 13 列。
        #   复用同一份矩阵会让模型 B 在 matmul 时维度不匹配。
        Xr_f, _ = build_design(rej, use_channel=f["use_ch"])
        pred = pp_predict(f, Xr_f)
        if f["use_ch"]:
            mu_b, sd_b, _ = ood_scale(build_design(acc, use_channel=True)[0])
            d_f = ood_dist(Xr_f, mu_b, sd_b)
            note = "（含 2 个渠道维度，距离数值与 A 不可直接比大小）"
        else:
            d_f = d_rej
            note = ""
        rej[f"pred_{key}"] = pred
        rej[f"ood_{key}"] = d_f
        rej[f"far_{key}"] = d_f > thr
        scores[key] = dict(rej=rej, pred=pred, f=f, d=d_f, far=d_f > thr, thr=thr)
        print(f"\n  {f['tag']}  /  {f['combo']}")
        print(f"    特征 {Xr_f.shape[1]} 列，已为 {len(rej):,} 件拒保件打分 {note}")
        print(f"    预测纯保费：均值 {pred.mean():>7,.0f} 元 / "
              f"中位数 {np.median(pred):>7,.0f} 元 / 最小 {pred.min():>6,.0f} 元")
        print(f"    对照真值：拒保人群 {rej._true_premium.mean():>7,.0f} 元  "
              f"承保人群 {acc._true_premium.mean():>7,.0f} 元")
        print(f"    校准偏差 {(pred.mean()-rej._true_premium.mean())/rej._true_premium.mean():+.1%}"
              "（外推人群的整体校准，是最容易翻车的地方）")

    # ---- 6.4 排序能力在外推人群上还剩多少？--------------------------------
    sub("6.4  关键体检：外推人群上，排序能力还剩多少？")
    med = good_premium()
    true_good = (rej._true_premium <= med).values
    from models import auc_score
    for key in ("A", "B"):
        if key not in scores:
            continue
        s = scores[key]
        p = s["pred"]
        far = s["far"]
        auc_all = auc_score(true_good.astype(int), -p)
        a_near = auc_score(true_good[~far].astype(int), -p[~far]) if (~far).sum() > 50 else float("nan")
        a_far = auc_score(true_good[far].astype(int), -p[far]) if far.sum() > 50 else float("nan")
        k = max(int(len(p) * 0.2), 1)
        order = np.argsort(p)
        pur_near = true_good[order[:k]][~far[order[:k]]].mean() if (~far).sum() > 0 else float("nan")
        print(f"\n  模型{key}：")
        print(f"    全体拒保件 AUC            {auc_all:>6.3f}")
        print(f"    仅「近点」AUC（{int((~far).sum()):,} 件）  {a_near:>6.3f}")
        print(f"    仅「远点」AUC（{int(far.sum()):,} 件）  {a_far:>6.3f}")
        print(f"    圈最低 20% 里的近点中，真正好司机占比   {pur_near:>6.1%}")
    print("\n  >>> 这张表回答了一个非常实际的问题：")
    print("      「模型能不能拿去救那些离训练数据最远的人？」")
    print("      如果远点 AUC 明显掉下来，落地时的做法应该是")
    print("      【先只对近点试点、远点继续走人工】，而不是一刀切。")
    return scores


# ==============================================================================
# 步骤 7：挑出「疑似错杀」并算业务账
# ==============================================================================
def step7_business(df, scores, key="A"):
    f = scores[key]["f"]
    rej, pred, far = scores[key]["rej"], scores[key]["pred"], scores[key]["far"]
    tag, combo = f["tag"], f["combo"]
    hr(f"步骤 7 / 8    业务账：{tag} / {combo} 找错杀值多少钱")

    med = good_premium()
    acc = df[df.accept == 1]
    flag = pred <= med
    n_flag = int(flag.sum())
    true_good = (rej._true_premium <= med).values
    tp = int((flag & true_good).sum())
    fp = int((flag & ~true_good).sum())
    fn = int((~flag & true_good).sum())
    tn = int((~flag & ~true_good).sum())
    n_good = tp + fn
    recall = tp / max(n_good, 1)
    precision = tp / max(n_flag, 1)

    print(f"判定口径：模型预测纯保费 ≤ {med:,.0f} 元（承保人群真实中位数）")
    print(f"模型圈出 {n_flag:,} 件「疑似错杀」，占被拒保件 {n_flag/len(rej):.1%}")
    print(f"  其中落在「近点」（外推可靠）{int((flag & ~far).sum()):,} 件，"
          f"落在「远点」{int((flag & far).sum()):,} 件")

    print("\n【召回 / 误伤】")
    print(f"  真实错杀            {n_good:>7,} 件")
    print(f"  模型抓到            {tp:>7,} 件   召回率 {recall:>6.1%}")
    print(f"  模型误伤            {fp:>7,} 件   精确率 {precision:>6.1%}")
    print(f"  模型漏掉            {fn:>7,} 件   漏杀率 {fn/max(n_good,1):>6.1%}")
    print(f"  判定正确            {tn:>7,} 件（本来就不该救，模型也确实没动）")

    acc_mean = acc._true_premium.mean()
    good_cost = rej[true_good]._true_premium.mean()
    if fn > 0:
        print("\n【被漏掉的那批人有多可惜？】")
        print(f"  漏杀组真实纯保费均值   {rej[(~flag) & true_good]._true_premium.mean():>7,.0f} 元")
        print(f"  抓到的错杀组          {rej[flag & true_good]._true_premium.mean():>7,.0f} 元")
    if fp > 0:
        fpv = rej[flag & ~true_good]._true_premium.mean()
        print("\n【误伤的人有多差？】")
        print(f"  误伤组真实纯保费均值   {fpv:>7,.0f} 元")
        print(f"  承保人群整体均值       {acc_mean:>7,.0f} 元（比值 {fpv/acc_mean:.2f}）")
        print("  >>> 误伤通常不是灾难：这些人只是比现有客户略贵一点。")
        print("      在车险里，「误收一个略贵的人」的代价，通常远小于")
        print(f"      「拒掉 {n_good/len(df)*100:.0f}% 好客户」的代价。所以召回可以往激进偏。")

    # ---- 业务账 -----------------------------------------------------------
    print("\n【业务账 · 精算】")
    # ★ 这里非常容易算错，而且错了以后「净增益」永远是负数，很容易被误读成
    #   「模型没用」。正确口径是：
    #     保费 P 里已经含了「预期赔款」这一块（综合成本率 COR 就是赔款占比），
    #     所以【不能再把真实赔款从毛利里减一遍】—— 那是重复扣减。
    #   正确算法是走增量：
    #     救回一单带来的毛利变化 = P − COR × 真实赔款
    #     （P 收进来，按真实成本赔掉，剩下的才是净赚）
    PREM = 3000.0
    COR = 0.75                       # 综合成本率：预期赔款占保费的 75%
    m_each = PREM - COR * good_cost  # 救回一单的实际毛利 = 3000 − 75%×964 ≈ 1,277
    print(f"  假设：年保费 {PREM:,.0f} 元")
    print(f"  错杀人群真实赔付成本   {good_cost:>7,.0f} 元/单")
    print(f"  >>> 口径澄清：综合成本率 COR 已经把「预期赔款」算进去了，")
    print(f"      所以不能先算 PREM×(1−COR) 再减一次真实赔款 —— 那是扣两遍。")
    print(f"      正确口径是增量：毛利 = 保费 − COR × 真实赔款")
    print(f"      救回一单毛利 = {PREM:,.0f} − {COR:.0%} × {good_cost:,.0f}"
          f" = {m_each:>7,.0f} 元")

    gross = m_each * tp
    # 误伤的成本：这个人本来不该收，现在收了。他的毛利贡献
    #   = PREM − COR × 误伤组真实赔款，可能为负。
    #   注意这里用的是「误伤组真实赔款」而不是「错杀组真实赔款」——
    #   否则等于把两种人的成本混在一起。
    fpv_all = rej[flag & ~true_good]._true_premium.mean() if fp > 0 else good_cost
    m_fp = PREM - COR * fpv_all
    fp_pnl = m_fp * fp
    net = gross + fp_pnl
    print(f"\n  按当前召回 {recall:.0%} 计：")
    print(f"    救回 {tp:,} 件，年毛利        {gross:>14,.0f} 元")
    print(f"    误伤 {fp:,} 件，年毛利        {fp_pnl:>14,.0f} 元"
          f"（单均 {m_fp:,.0f} 元）")
    print(f"    净增益                {net:>14,.0f} 元")
    print(f"\n  >>> 全额召回（{n_good:,} 件）年毛利可达 "
          f"{m_each*n_good:,.0f} 元。")
    print("      对一家中等规模公司，这大约等于一整支销售队伍一年的成本。")
    print(f"      而当前召回 {recall:.0%} 就已经拿到 {net:,.0f} 元 ——")
    print(f"      漏掉的那 {fn:,} 件里还躺着 {(m_each-rej[(~flag)&true_good]._true_premium.mean())*fn:,.0f} 元。")

    # ---- 分档：只要高置信的那批 ------------------------------------------
    print("\n【更稳妥的打法：按预测风险分档，看每一档的真实质量】")
    print(f"  {'档位（预测从低到高）':<20}{'件数':>7}{'真实均值':>10}"
          f"{'好司机占比':>11}{'单均毛利':>10}{'年毛利':>14}")
    order = np.argsort(pred)
    cuts = [0, .05, .10, .20, .30, .50, 1.0]
    tpv = rej._true_premium.values
    bands = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        sel = order[int(len(pred) * lo):int(len(pred) * hi)]
        if len(sel) == 0:
            continue
        n = len(sel)
        tm = float(tpv[sel].mean())
        good = float(true_good[sel].mean())
        m1 = PREM - COR * tm
        g = m1 * n
        print(f"  最低 {lo*100:>3.0f}% - {hi*100:>3.0f}%{n:>8,}{tm:>10,.0f}"
              f"{good:>10.1%}{m1:>10,.0f}{g:>14,.0f}")
        bands.append(dict(lo=lo, hi=hi, n=n, true_mean=tm, good_rate=good,
                          margin_each=m1, gross=float(g)))
    print(f"\n  >>> 读表要点：单均毛利 = 保费 − COR × 该档真实赔款。")
    print("      只有当某档真实赔款 < 保费/COR = "
          f"{PREM/COR:,.0f} 元时，这一档才赚钱。")
    print("      注意：越靠后的档虽然风险更高，但因为「基数大」，")
    print("      年毛利的绝对值反而更高。真正要看的不是「赚不赚」，")
    print("      而是【每单位人工复核成本换来的毛利】—— 这就要选阈值了。")

    # ---- 阈值选择：这是精算人真正要做的决策 ------------------------------
    # ★ 这里必须跟「随机圈选」对比，否则结论会失真。
    #   如果只看「单均毛利」，每一档都是正的、性价比都在 50 倍上下，
    #   看起来模型好坏都一样 —— 因为毛利主要由保费规模决定，
    #   而不是由「挑对人」决定。
    #   真正衡量模型价值的是【同样的复核投入，谁赚得多】。
    print("\n【圈选阈值怎么定？把人工复核当成一笔投资来算】")
    UNIT_COST = 80 * 0.5
    print(f"  假设每个待复核件需要 0.5 小时人工，按 80 元/小时计，单件成本 "
          f"{UNIT_COST:,.0f} 元。")
    print("  关键：必须和「随机圈同样多的人」比。同一笔复核预算，")
    print("        模型挑的人和瞎挑的人，赚的钱差多少 —— 这才是模型的价值。")
    order2 = np.argsort(pred)
    print(f"\n  {'预测阈值':>9}{'圈出':>6}{'真实均值':>10}{'好司机占比':>11}"
          f"{'年毛利':>12}{'随机同样多':>12}{'模型增益':>12}")
    thrs = []
    rand_unit = PREM - COR * float(tpv.mean())
    for q in [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 1.0]:
        thr_v = float(np.quantile(pred, q))
        sel = order2[:max(int(len(pred) * q), 1)]
        n = len(sel)
        tm = float(tpv[sel].mean())
        m1 = PREM - COR * tm
        tot = m1 * n
        base_tot = rand_unit * n
        gain = tot - base_tot
        thrs.append(dict(thr=thr_v, q=q, n=n, true_mean=tm,
                         good_rate=float(true_good[sel].mean()),
                         margin=m1, gross=float(tot),
                         rand_gross=float(base_tot), gain=float(gain),
                         cost=float(UNIT_COST * n)))
        print(f"  {thr_v:>9,.0f}{n:>6,}{tm:>10,.0f}{true_good[sel].mean():>10.1%}"
              f"{tot:>12,.0f}{base_tot:>12,.0f}{gain:>+12,.0f}")
    best_pure = max(thrs, key=lambda r: r["good_rate"])
    best_gain = max(thrs, key=lambda r: r["gain"])
    print(f"\n  >>> 读法一 ·【圈纯度】最高的是「预测 ≤ {best_pure['thr']:,.0f} 元」：")
    print(f"      圈 {best_pure['n']:,} 件，里面真正的好司机占 "
          f"{best_pure['good_rate']:.1%}")
    print(f"      （随机圈是 {true_good.mean():.1%}，只圈最低 20% 的话是 50%）。")
    print("      这是「圈得准」—— 人工复核的人力不浪费在一半必然不合格的人身上。")
    print(f"\n  >>> 读法二 ·【模型增益】在「预测 ≤ {best_gain['thr']:,.0f} 元」"
          f"（圈 {best_gain['n']:,} 件）处最大：")
    print(f"      比随机圈同样多的人，多赚 {best_gain['gain']:,.0f} 元。")
    print("      这条曲线先升后降，是个典型的倒 U ——")
    print("      圈太少，人力没用满；圈太多，增益被边际质量摊薄。")
    print("      >>> 圈选阈值不是拍出来的，是这条曲线上的最大值。")
    print("      这就是精算最熟悉的东西：一条以分位数为横轴的累计收益曲线，")
    print("      找拐点，而不是找一个「看起来合理」的整数。")
    print(f"\n  >>> 顺带回答一个常见疑问：为什么不用「承保人群中位数 "
          f"{med:,.0f} 元」当阈值？")
    print(f"      因为那个口径回答的是「谁比现有客户更好」（面子），")
    print(f"      而这里要回答的是「谁值得花人工去救」（里子）。")
    print(f"      按中位数只圈出 {int((pred <= med).sum()):,} 件，")
    print(f"      而按上面的曲线，圈 {best_gain['n']:,} 件时增益更大。")
    pd.DataFrame(thrs).to_csv(os.path.join(OUT, "threshold_" + key + ".csv"),
                               index=False, encoding="utf-8-sig")

    # ---- 分渠道的召回与误伤 ----------------------------------------------
    print("\n【分渠道看：模型有没有优先救回线上渠道那些被冤枉的人？】")
    print(f"  {'渠道':<10}{'拒保件':>8}{'真实错杀':>9}{'圈出':>7}"
          f"{'召回率':>9}{'精确率':>9}{'净增益':>14}")
    by_ch = []
    for nm in ["代理渠道", "直销渠道", "线上渠道"]:
        m = (rej.channel_nm == nm).values
        g = int((m & true_good).sum())
        fl = int((m & flag).sum())
        hit = int((m & flag & true_good).sum())
        pnl = m_each * hit + (PREM - COR * tpv[m & flag].mean()) * (fl - hit) if fl else 0.0
        by_ch.append(dict(channel=nm, n=int(m.sum()), n_good=g, n_flag=fl,
                          recall=hit / max(g, 1), precision=hit / max(fl, 1),
                          pnl=float(pnl)))
        print(f"  {nm:<10}{int(m.sum()):>8,}{g:>9,}{fl:>7,}"
              f"{hit/max(g,1):>9.1%}{hit/max(fl,1):>9.1%}{pnl:>14,.0f}")
    print("  >>> 线上渠道的召回率如果显著高于代理/直销，说明模型确实")
    print("      学到了「风险本身」，而不是学到了「你是谁」。这正是模型 A")
    print("      相对规则核保最大的价值。")

    # ---- 稳健子集版本：只在近点上线 ---------------------------------------
    near = ~far
    fl_n = flag & near
    tp_n = int((fl_n & true_good).sum())
    fp_n = int((fl_n & ~true_good).sum())
    fpn_n = fl_n & ~true_good
    m_fp_n = PREM - COR * (tpv[fpn_n].mean() if fp_n else good_cost)
    net_n = m_each * tp_n + m_fp_n * fp_n
    print("\n【保守版方案：只对「近点」放宽核保，远点维持原规则】")
    print(f"  覆盖件 {int(near.sum()):,} 件 / 圈出 {int(fl_n.sum()):,} 件"
          f"（占全部拒保件 {fl_n.sum()/len(rej):.1%}）")
    print(f"  抓到错杀 {tp_n:,} 件（占真实错杀 {tp_n/max(n_good,1):.1%}），"
          f"误伤 {fp_n:,} 件（精确率 {tp_n/max(int(fl_n.sum()),1):.1%}）")
    print(f"  救回毛利 {m_each*tp_n:,.0f} 元 / 误伤毛利 {m_fp_n*fp_n:,.0f} 元"
          f" / 净增益 {net_n:,.0f} 元")
    print(f"  相比全量方案少拿 {net-net_n:,.0f} 元，"
          f"但外推风险基本清零。")
    print("  >>> 这通常才是第一年真正能落地的方案：")
    print("      先在「模型有把握」的地方要业绩，剩下的继续走人工。")

    pd.DataFrame(bands).to_csv(os.path.join(OUT, "bands_" + key + ".csv"),
                               index=False, encoding="utf-8-sig")
    pd.DataFrame(by_ch).to_csv(os.path.join(OUT, "by_channel_" + key + ".csv"),
                               index=False, encoding="utf-8-sig")

    return dict(tp=tp, fp=fp, fn=fn, tn=tn, n_flag=n_flag, n_flag_near=int(fl_n.sum()),
                recall=recall, precision=precision, gross=gross, net=net,
                net_near=net_n, n_good=n_good, thr=float(med))


# ==============================================================================
# 步骤 8：选择偏差的四种修法
# ==============================================================================
def step8_bias(df, scores, key="A"):
    f = scores[key]["f"]
    hr("步骤 8 / 8    选择偏差的四种修法：不加权 / 仅IPW / 仅结果模型 / 双重稳健")
    aud = df[(df.accept == 0) & (df.audit == 1)].copy().reset_index(drop=True)
    rej = df[df.accept == 0].copy().reset_index(drop=True)
    target = rej._true_premium.mean()
    print(f"被拒保人群真实平均纯保费（真值，只有模拟器知道）= {target:,.1f} 元")
    print(f"审计样本 {len(aud):,} 件，占被拒保件 {len(aud)/len(rej):.1%}")
    print("这是唯一能「看见」拒保人群真实风险的窗口。")

    # 结果模型 μ(x) 覆盖【全体】被拒保件 —— 残差校正才是 DR 的关键
    Xr, _ = build_design(rej, use_channel=f["use_ch"])
    mu_all = pp_predict(f, Xr)
    Xa, _ = build_design(aud, use_channel=f["use_ch"])
    mu_aud = pp_predict(f, Xa)

    y = aud._true_premium.values
    w = aud.audit_weight.values.astype(float)

    naive = y.mean()                                     # ① 不加权
    ipw = np.average(y, weights=w)                       # ② 仅 IPW
    res = mu_all.mean()                                  # ③ 仅结果模型
    dr = res + np.average((y - mu_aud), weights=w)       # ④ 双重稳健

    print(f"\n  {'方法':<30}{'估计值':>11}{'偏差':>11}{'偏差率':>10}")
    tbl = []
    for nm, v in [("① 不加权（直接取平均）", naive),
                  ("② 仅 IPW（1/抽样概率）", ipw),
                  ("③ 仅结果模型（模型外推）", res),
                  ("④ 双重稳健 DR（外推+残差）", dr)]:
        print(f"  {nm:<28}{v:>11,.1f}{v-target:>+11,.1f}{(v-target)/target:>10.1%}")
        tbl.append(dict(method=nm, est=float(v), bias=float(v - target),
                        rel_bias=float((v - target) / target)))

    print("\n【怎么读这张表】")
    print(f"  ① 不加权    偏差 {(naive-target)/target:+.1%}。审计样本有偏，直接用就偏。")
    print(f"  ② 仅 IPW    偏差 {(ipw-target)/target:+.1%}。修正了「渠道比例」这类已知抽样机制，")
    print("              但修不了「配合度」这类不可观测的机制。")
    print(f"  ③ 结果模型  偏差 {(res-target)/target:+.1%}。只要模型本身学对了，权重错了也还行。")
    print(f"  ④ DR        偏差 {(dr-target)/target:+.1%}。模型能解释的被模型拿走，")
    print("              剩下的残差才交给权重去修 —— 这才是「双重」。")

    print("\n【为什么叫「双重」】")
    print("  它用了两件东西：① 一个结果模型 μ(x)；② 一组抽样权重 w。")
    print("  DR = mean_all[ μ(x) ]  +  Σ wᵢ(yᵢ − μ(xᵢ)) / Σ wᵢ")
    print("       └── 模型外推到全体 ──┘└── 残差交给权重 ──┘")
    print("  括号里是残差 —— 模型能解释掉的，模型自己解释掉；")
    print("  解释不掉的（抽样机制带偏的部分），交给权重去修。")
    print("  两个机制各管一半，所以叫双重。")
    print("\n  >>> 核心承诺：「模型对」或「权重对」，只要有一个对，结果就无偏。")
    print("      这是极强的稳健性保证，也是因果推断的主流做法。")

    print("\n【一个非常容易搞混的细节 —— 本案例真踩过】")
    print("  如果只对【审计样本】算 DR，那么 yᵢ − μ(xᵢ) 在求和时被 μ 抵消，")
    print("  残差项恒等于 0，DR 就退化成了 IPW —— 双重稳健就白叫了。")
    print("  所以第一项必须外推到【全体】被拒保件，这才是 DR 的灵魂。")
    print("  代码对照：")
    print("    ✗ dr = np.average(mu + (y - mu), weights=w)      # 残差被抵消")
    print("    ✓ dr = mu_all.mean() + np.average(y - mu_aud, weights=w)")

    print("\n【本案例的诚实之处 —— 一个必须说清的概念边界】")
    print("  模拟器里 p_audit 是我们自己在抽样时定的，所以「已知」；")
    print("  而「配合度」这个不可观测因素，也是模拟器显式塞进去的。")
    print("  于是出现一个教学上的矛盾：机制在模拟器里已知，")
    print("  IPW 却修正不了它 —— 这恰恰是对的。")
    print("  >>> IPW 只能修正【你能写下来】的抽样机制。")
    print("      现实中「谁愿意配合审计」往往没有记录，权重只能估。")
    print("      DR 之所以主流，正是因为它给了你一条「权重估错了也还能救」的退路。")

    pd.DataFrame(tbl).to_csv(os.path.join(OUT, "bias_" + key + ".csv"),
                              index=False, encoding="utf-8-sig")
    return dict(naive=naive, ipw=ipw, res=res, dr=dr, target=target,
                table=tbl)
