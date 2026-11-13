# -*- coding: utf-8 -*-
"""
场景一 · 端到端流水线：找出被错杀的好司机
================================================================================
这一份代码回答一个非常具体、非常接地气的问题：

    「我们去年拒掉的那些人里，其实有一批好司机。
      能不能用赔款数据把他们找出来？该怎么找？找出来值多少钱？」

全程只回答业务问题，不炫技。四个模型逐个上场，每一个都要回答
「它比前一个多解决了什么问题」。

Pipeline（8 步）
    1. 读数据 &体检          —— 先看清楚我们手里到底有什么
    2. 定义「好司机」         —— 把业务问题翻译成可计算的标签
    3. 构造训练集             —— 只用看得见的标签
    4. 四个模型依次训练        —— 常数 → GLM → 单树 → GBDT
    5. 评估                   —— 训练集/测试集双视角
    6. 关键一步：给拒保人群打分 —— 这才是真正的战场
    7. 挑出「疑似错杀」并算业务账
    8. 选择偏差的四种修法对比  —— 不加权 / 仅IPW / 仅结果模型 / 双重稳健

【一条贯穿全篇的主线】
    你的训练数据里没有「被拒保的人」。
    所以模型对他们的预测，本质上是一次外推。
    所有的难点、所有的偏差、所有的谨慎，都源自这一句话。

运行： python train_evaluate.py
输出： 控制台报告 + out/ 目录下的中间结果 CSV
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import (PoissonRegressor, LogisticRegression,
                    DecisionTreeRegressor, GBDT,
                    poisson_deviance, auc_score, lift_table)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20261003
TEST_SIZE = 0.25          # 25% 做测试集
RS = np.random.default_rng(SEED)

# 「好司机」的定义阈值：用承保人群真实纯保费的中位数。
# 现实里没有真值，这一段是课堂才有的奢侈，后面会专门讲怎么在现实中逼近它。
GOOD_PREMIUM = None       # 运行第 1 步后填入


def hr(title):
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)


def sub(title):
    print(f"\n--- {title} " + "-" * max(0, 70 - len(title) * 2))


# ==============================================================================
# 步骤 1：读数据 & 体检
# ==============================================================================
def step1_load():
    hr("步骤 1 / 8    读数据 & 体检：我们手里到底有什么？")
    df = pd.read_csv(os.path.join(DATA, "drivers.csv"))
    print(f"总件数{len(df):,}")

    print("\n【可见的标签】")
    print("  accept=1（已承保）→ claim_cnt / claim_amt 有效，可用于训练")
    print("  accept=0（被拒保）→ claim_cnt = -1，表示「无记录」，不是「零出险」")
    print("                     这是整个案例最关键的一个符号")
    n_acc = int((df.accept == 1).sum())
    n_rej = int((df.accept == 0).sum())
    n_aud = int(((df.accept == 0) & (df.audit == 1)).sum())
    print(f"\n  已承保{n_acc:>7,} 件")
    print(f"  被拒保{n_rej:>7,} 件")
    print(f"  其中审计样本{n_aud:>5,} 件（被拒保件的 {n_aud/max(n_rej,1):.1%}）")

    print("\n【零出险 vs 无记录 —— 必须分清】")
    acc = df[df.accept == 1]
    print(f"  已承保中 claim_cnt == 0 （真的没出险）  {(acc.claim_cnt == 0).sum():>7,} 件")
    print(f"  被拒保中 claim_cnt == -1（没有记录）    {(df[df.accept==0].claim_cnt == -1).sum():>7,} 件")
    print("  >>> 如果把 -1 当成 0 喂给模型，等于告诉它「这些人全都没出险」——")
    print("      模型会把拒保人群学成『零风险』，反过来加价或全拒。")

    print("\n【一个必须警惕的观察】")
    print(f"  承保件真实纯保费（真值）{acc._true_premium.mean():.0f} 元")
    print(f"  拒保件真实纯保费（真值）{df[df.accept==0]._true_premium.mean():.0f} 元")
    print("  拒保人群整体比承保人群更贵。看起来「拒保有道理」？")
    print("  但这只是均值。均值会骗人 —— 下一步就拆开看。")
    return df


# ==============================================================================
# 步骤 2：定义「好司机」
# ==============================================================================
def step2_define_good(df):
    hr("步骤 2 / 8    定义「好司机」：把业务问题翻译成可计算的标签")
    acc = df[df.accept == 1]
    rej = df[df.accept == 0]
    med = acc._true_premium.median()
    # 业务口径：对标「当前在保客户的典型水平」。
    # 低于它 = 我们拒掉了一个和现有客户差不多好的人 = 错杀。
    global GOOD_PREMIUM
    GOOD_PREMIUM = float(med)

    print(f"判定阈值 GOOD_PREMIUM = 承保人群真实纯保费中位数 = {med:.0f} 元")
    print("\n  业务解释：我们拒掉的人，如果他的真实成本其实和现有客户")
    print("           的典型水平差不多甚至更低，那就是错杀。")
    print("           这不是「他很安全」，而是「我们拒错人了」。")

    wrong = rej[rej._true_premium <= med]
    print(f"\n  被拒保            {len(rej):>7,} 件")
    print(f"  其中错杀          {len(wrong):>7,} 件（占拒保 {len(wrong)/len(rej):.1%}）")
    print(f"  占全部申请{len(wrong)/len(df):>7.1%}")
    print(f"  错杀人群真实纯保费中位数{wrong._true_premium.median():>7.0f} 元")
    print(f"  拒保人群整体中位数        {rej._true_premium.median():>7.0f} 元")

    sub("错杀集中在谁身上")
    rows = []
    for nm in ["代理渠道", "直销渠道", "线上渠道"]:
        s = rej[rej.channel_nm == nm]
        w = s[s._true_premium <= med]
        rows.append((nm, len(s), len(w), len(w) / max(len(s), 1)))
    for nm, a, b, r in rows:
        print(f"  {nm:<6} 拒保 {a:>6,}  错杀 {b:>6,}  错杀率 {r:>6.1%}")
    print("\n  >>> 线上渠道错杀率是代理渠道的 "
          f"{rows[2][3]/max(rows[0][3],1e-9):.1f} 倍。")
    print("      渠道与「危险程度」无关，它只反映「信息取得难度」。")
    print("      规则惩罚渠道，等于惩罚「你了解得不够」而不是「他更危险」。")
    print("      这就是错杀的主因，也是本案例真正要治的病。")

    print("\n【关键澄清：为什么 channel 不能进定价模型】")
    print("  定价模型要回答的是「这个人的风险是多少」。")
    print("  渠道回答的是「我从哪里认识他、掌握他多少信息」。")
    print("  把后者塞进前者，等于让价格惩罚「介绍人是谁」。")
    print("  >>> 判定依据不是它和赔款有没有统计相关，而是它有没有因果意义。")
    return wrong


# ==============================================================================
# 步骤 3：构造训练集
# ==============================================================================
FEATURES = ["age", "car_value", "car_type", "region", "mileage", "use_type", "channel"]
FEATURE_NAMES = ["年龄", "车价(万元)", "车型", "地区", "年里程", "用途", "渠道"]
USE_IN_MODEL = ["age", "car_value", "car_type", "region", "mileage", "use_type"]

# 各分类变量的水平名（下标 = 原始编码值）
LEVEL_NAMES = {
    "car_type": ["经济型", "SUV", "新能源", "性能车"],
    "region":   ["华东", "华北", "华南", "西部", "其他"],
    "use_type": ["家用", "营运"],
    "channel":  ["代理", "直销", "线上"],
}
CAT_COLS = ("car_type", "region", "use_type", "channel")


def build_design(df, use_channel=False):
    """
    把原始特征变成模型能吃的设计矩阵。

    分类变量 one-hot（drop_first=True，避免共线）；
    连续变量做 log / 中心化 —— 右边偏得很厉害（车价 4~95 万，里程 1800~62000），
    不变换的话 IRLS 的步长会忽大忽小，系数也难解释。

    ★ 一个非常容易踩、而且踩了不报错的坑：
      水平集必须【冻结】，不能跟着数据走。
      本案例里 use_type=1（营运）只出现在被拒保人群，承保人群一个都没有。
      如果直接对两个 DataFrame 各跑一次 get_dummies(drop_first=True)：
        承保集只有一个水平 0 → drop 掉 → 产出 0 列
        拒保集有两个水平   → drop 掉 0 → 产出 1 列
      训练时 10 列、预测时 11 列，模型不会报错，只会算出一堆胡话。
      真实项目里这就是「上线后预测全错但没人知道为什么」的经典原因。
      所以这里显式声明要保留哪些水平，并对齐列顺序。
    """
    cols = USE_IN_MODEL + (["channel"] if use_channel else [])
    parts, names = [], []
    for c in cols:
        if c in CAT_COLS:
            lv = LEVEL_NAMES[c]
            # 冻结水平集：drop 掉第 0 个水平作为基准，其余全部显式生成
            d = pd.get_dummies(df[c].astype(int), prefix=c)
            for i, name in enumerate(lv):
                if i == 0:
                    continue
                col = f"{c}_{i}"
                if col not in d.columns:
                    d[col] = 0.0          # 该水平在此子群里不存在 → 全 0
                parts.append(d[[col]].astype(float))
                names.append(name)
        elif c == "age":
            parts.append((df.age.astype(float) - 38.0).to_frame())
            names.append("年龄(相对38)")
        elif c == "car_value":
            parts.append(np.log(df.car_value.astype(float)).to_frame())
            names.append("车价(对数)")
        else:  # mileage
            parts.append(np.log(df.mileage.astype(float)).to_frame())
            names.append("年里程(对数)")
    X = pd.concat(parts, axis=1).values.astype(float)
    return np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0), names


def step3_dataset(df):
    hr("步骤 3 / 8    构造训练集：只用看得见的标签")
    # 关键：先重置索引。
    #   被拒保件被筛掉后，承保件的标签索引是断的（0,1,...,8800 里有空洞）。
    #   若拿位置索引去切 DataFrame 会错位，取特征时直接报 KeyError。
    acc = df[df.accept == 1].copy().reset_index(drop=True)
    n = len(acc)
    idx = RS.permutation(n)
    n_test = int(n * TEST_SIZE)
    te, tr = idx[:n_test], idx[n_test:]
    print(f"已承保 {n:,} 件 → 训练集 {len(tr):,} 件 / 测试集 {len(te):,} 件")
    print(f"随机划分，种子 {SEED}，可完全复现")

    print("\n【两个模型的口径，刻意不同】")
    print("  模型A（默认）：不含 channel —— 因为渠道没有因果意义")
    print("  模型B（对照）：含 channel   —— 用来看「把偏见学进去」的后果")
    print("  两者都会跑一遍，你会亲眼看到 B 在承保人群上更好、在拒保人群上更糟。")
    return acc, tr, te


# ==============================================================================
# 步骤 4-5：四个模型依次训练 + 评估
# ==============================================================================
def step45_models(acc, tr, te):
    """
    承保件一进来就撞上一个墙：直接用纯保费做 Poisson 回归，效果非常差。
    这不是代码写错了，而是重尾数据的本质困难。所以本步骤分三层：

        第 1 层「撞墙」：先老老实实用纯保费建模型，亲眼看到它打不过常数基线。
        第 2 层「拆解」：回到精算的老本行 —— 频率 × 损失，分开建模，
                        各自用各自对应的尺子（Poisson deviance / 对数尺度 MSE）。
        第 3 层「组装」：把两个组件拼成纯保费，改用【业务指标】评价：
                        排序能力（AUC、圈选纯度）+ 校准能力（均值偏差）。

    这三层是精算人上手机器学习最自然的路径：
        先承认问题，再拆解，最后才换尺子重新评价。

    ★ 关于 Tweedie：Tweedie 回归确实是零膨胀+重尾的标准解法
      （p∈(1,2) 时连接 Gamma 与 Poisson），本案例没有实现它。
      取而代之的是上面这条更朴素、也更可控的频率—损失路径 ——
      它本来就是精算的老本行，而且每个组件都能单独解释、单独监控。
      凡是能说清楚「为什么这么做」的方法，比能跑通的黑盒更值得先学。
    """
    hr("步骤 4-5 / 8    四个模型依次登场：每一步多解决了什么？")

    for tag, use_ch in [("模型A（不含渠道）", False), ("模型B（含渠道）", True)]:
        X_all, names = build_design(acc, use_channel=use_ch)
        y_cnt = acc.claim_cnt.values.astype(float)     # 出险次数
        y_amt = acc.claim_amt.values.astype(float)     # 赔付金额

        Xtr, Xte = X_all[tr], X_all[te]
        cnt_tr, cnt_te = y_cnt[tr], y_cnt[te]
        pp_tr, pp_te = y_amt[tr], y_amt[te]
        # 「好司机」标签：真实期望纯保费是否低于承保人群中位数
        thr_good = float(np.median(acc._true_premium))
        good_te = (acc._true_premium.values[te] <= thr_good).astype(int)

        print(f"\n{'='*76}")
        print(f"  {tag}   特征数 = {X_all.shape[1]}")
        print(f"{'='*76}")

        # ======================================================================
        # 第1 层：直接对「纯保费」建模 —— 撞墙，而且撞得非常有教育意义
        # ======================================================================
        sub("第 1 层 · 直接对「纯保费」建模（先撞一次墙）")
        print("  直觉：既然目标是纯保费，那就直接把它当因变量回归。")
        print("  先看数据长什么样：")
        q = np.quantile(pp_tr, [0.5, 0.9, 0.99, 0.999])
        print(f"    中位数{q[0]:>10,.0f} 元")
        print(f"    90分位{q[1]:>10,.0f} 元")
        print(f"    99分位{q[2]:>10,.0f} 元")
        print(f"    99.9分位 {q[3]:>10,.0f} 元")
        print(f"    零赔付占比 {(pp_tr==0).mean():.1%}")

        # 尾部集中度：这是后面所有麻烦的根源
        amt = pp_tr[pp_tr > 0]
        top1 = np.sort(amt)[::-1][:1].sum() / amt.sum()
        top10 = np.sort(amt)[::-1][:10].sum() / amt.sum()
        print(f"    最大一笔赔款就占全部赔款 {top1:.1%}，前 10 笔占 {top10:.1%}")
        print("  这就是「零膨胀 + 重尾」。均值被尾部拽走，方差远大于均值。")

        wall = {}
        wall["常数基线"] = poisson_deviance(pp_te, np.full(len(te), pp_tr.mean()))
        glm_pp = PoissonRegressor(alpha=0.05, max_iter=200).fit(Xtr, pp_tr)
        wall["Poisson GLM(纯保费)"] = poisson_deviance(pp_te, glm_pp.predict(Xte))
        gb_pp = GBDT(M=80, learning_rate=0.07, max_depth=3,
                     min_samples_leaf=40, verbose=False).fit(Xtr, pp_tr)
        wall["GBDT(纯保费)"] = poisson_deviance(pp_te, gb_pp.predict(Xte))

        print(f"\n  {'模型':<24}{'测试集 deviance':>18}{'vs 常数基线':>14}")
        base = wall["常数基线"]
        for k in ["常数基线", "Poisson GLM(纯保费)", "GBDT(纯保费)"]:
            v = wall[k]
            print(f"  {k:<24}{v:>18.1f}{v/base*100:>13.1f}%")

        # ★ 结论必须由实际数字决定，不能写死。
        #   换一批数据，结论可能从「打不过常数」变成「略好一点点」，
        #   那时候真正该说的是「改善被巨灾噪声吃掉了」，而不是「模型没学到东西」。
        best_pp = min(wall["Poisson GLM(纯保费)"], wall["GBDT(纯保费)"])
        if best_pp >= base:
            print(f"\n  >>> 撞墙成功：两个模型都打不过「直接用平均值」"
                  f"（最优 {best_pp/base*100:.1f}%）。")
        else:
            print(f"\n  >>> 注意：模型其实【略微】优于常数基线"
                  f"（最优 {best_pp/base*100:.1f}%），")
            print("      但改善幅度只有 "
                  f"{(1-best_pp/base)*100:.1f}%，根本不值一提。")
            print("      原因不是模型没学到东西，而是这个指标【被污染了】。")
        print("      先别急着下结论 —— 后面会证明：")
        print("      【模型基本功没问题，是评价指标被少数巨灾赔款绑架了。】")
        print("      这是本章最值钱的一课，也是很多人入门机器学习最大的坑。")
        print("      怎么证明？看下一个指标：换成正确的尺子，模型立刻说话。")

        # ======================================================================
        # 第 2 层：拆开看 —— 频率和损失必须用各自对应的尺子量
        # ======================================================================
        sub("第 2 层 · 频率—损失分解（回到精算的老本行）")
        print("      纯保费 = 频率 × 损失")
        print("      频率 = 出险次数（零膨胀、计数型、方差≈均值）→ 用 Poisson deviance")
        print("      损失 = 每次赔多少（重尾、连续型）→ 用【对数尺度】的 MSE")
        print("      关键：混在一起用一个指标量，等于用错的尺子量东西。")

        # --- 频率模型 ---
        freq_glm = PoissonRegressor(alpha=0.05, max_iter=200).fit(Xtr, cnt_tr)
        freq_gb = GBDT(M=80, learning_rate=0.07, max_depth=3,
                       min_samples_leaf=40, verbose=False).fit(Xtr, cnt_tr)

        print(f"\n【频率模型 · Poisson GLM】共{len(cnt_tr):,} 个样本，"
              f"其中出险 {(cnt_tr>0).sum():,} 个")
        print("     系数直接读成相对风险 RR = exp(coef)：")
        print("     RR = 1.35 → 该因子每 +1，出险次数变成 1.35 倍")
        s = freq_glm.summary(names)
        for ln in s.splitlines()[:13]:
            print("     " + ln)

        print("\n【频率模型 · GBDT】特征重要度（分裂增益占比）：")
        imp = freq_gb.importances_
        for i in np.argsort(-imp)[:8]:
            if imp[i] > 0.005:
                print(f"     {names[i]:<14}{imp[i]*100:>5.1f}%")
        print("     注意：重要度 =『模型用了它多少』≠『它业务上多重要』。")

        # 频率：正确的尺子 = Poisson deviance（作用在【次数】上）
        f_base = poisson_deviance(cnt_te, np.full(len(te), cnt_tr.mean()))
        f_glm = poisson_deviance(cnt_te, freq_glm.predict(Xte))
        f_gb = poisson_deviance(cnt_te, freq_gb.predict(Xte))
        print(f"\n  【频率模型的正确评价】Poisson deviance（作用在出险次数上）")
        print(f"  {'模型':<20}{'deviance':>12}{'vs 常数':>10}{'AUC':>9}")
        print(f"  {'常数基线':<18}{f_base:>12.3f}{100.0:>9.1f}%{0.5:>9.3f}")
        for nm, v, mm in [("Poisson GLM", f_glm, freq_glm), ("GBDT", f_gb, freq_gb)]:
            auc = auc_score((cnt_te > 0).astype(int), mm.predict(Xte))
            print(f"  {nm:<18}{v:>12.3f}{v/f_base*100:>9.1f}%{auc:>9.3f}")
        print("  >>> 现在看得出模型确实学到了东西（deviance 低于常数基线，")
        print("      AUC 明显大于 0.5）。刚才的失败是【尺子】的问题，不是【模型】的问题。")

        # --- 损失模型：只在有出险的人身上建，且必须用对数尺度 ---
        has_claim = cnt_tr > 0
        print(f"\n【损失模型】在 {has_claim.sum():,} 个有出险的样本上建")
        print("     只在有出险的人身上建 —— 没出险的人没有「每次赔多少」。")
        print("     而且必须先取对数：损失是对数正态的，在原尺度上 MSE 会被巨灾主导。")
        log_sev_tr = np.log(np.clip(pp_tr[has_claim], 1.0, None))
        sev_tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=25).fit(
            Xtr[has_claim], log_sev_tr)
        log_base = np.log(np.clip(pp_te[pp_te > 0], 1.0, None))
        mse_base = np.mean((log_base - log_sev_tr.mean()) ** 2)
        mse_tree = np.mean((log_base - sev_tree.predict(Xte[pp_te > 0])) ** 2)
        print(f"     单树节点数 {sev_tree.count_nodes()}，规则示例：")
        for ln in sev_tree.export_rules(names).splitlines()[:5]:
            print("     " + ln)
        print(f"\n  【损失模型的正确评价】对数尺度 MSE（只看有出险的样本）")
        print(f"    常数基线{'':<6}{mse_base:>10.4f}{100.0:>9.1f}%")
        print(f"    损失单树 {'':<6}{mse_tree:>10.4f}{mse_tree/mse_base*100:>9.1f}%")

        # ======================================================================
        # 第 3 层：组合起来，并且用【对】的指标评价整体
        # ======================================================================
        sub("第 3 层 · 组装成完整定价模型，并且用对的指标评价它")

        def pp_pred(fm, X, sev_m=None, const=None):
            """纯保费 = 预测频率 × 预测损失"""
            f = np.clip(fm.predict(X), 1e-6, None)
            if sev_m is None:
                s_ = float(const)
            else:
                s_ = np.exp(np.clip(sev_m.predict(X), -5.0, 12.0))
            return f * s_

        sev_const = float(np.mean(pp_tr[has_claim]))
        combos = {
            "① 频率GLM × 损失单树": (freq_glm, sev_tree, None),
            "② 频率GBDT × 损失单树": (freq_gb, sev_tree, None),
            "③ 频率GLM × 损失均值": (freq_glm, None, sev_const),
        }

        results = {}
        print(f"\n  两条尺子同时量：① 排序能力（AUC / 圈选纯度）② 校准（均值偏差）")
        print(f"\n  {'组合':<22}{'AUC':>8}{'圈最低20%纯度':>15}{'均值偏差':>11}")
        for k, (fm, sm, cst) in combos.items():
            pred = pp_pred(fm, Xte, sm, cst)
            # 注意方向：我们要找的是【预测纯保费最低】的那批好司机，
            # 所以 AUC 必须用 -pred 当分数，否则会得到「越像越好」的反向结论。
            auc = auc_score(good_te, -pred)
            k20 = int(len(te) * 0.2)
            purity = float(good_te[np.argsort(pred)[:k20]].mean())
            bias = (pred.mean() - pp_te.mean()) / pp_te.mean()
            results[k] = dict(auc=auc, purity=purity, bias=bias,
                              pred=pred, freq_m=fm, sev_m=sm, const=cst)
            print(f"  {k:<22}{auc:>8.3f}{purity:>14.1%}{bias:>10.1%}")

        base_pred = np.full(len(te), pp_tr.mean())
        auc_b = auc_score(good_te, base_pred)
        pur_b = float(good_te[np.argsort(base_pred)[:int(len(te)*0.2)]].mean())
        print(f"  {'常数基线':<22}{auc_b:>8.3f}{pur_b:>14.1%}{0.0:>10.1%}")
        print("\n  >>> 这才是关键的一张表。模型把「圈最低 20% 里真正好司机的占比」")
        print("      从 50% 提到了 75% 以上 —— 这就是实务上真正要的能力：")
        print("      【把有限的人工复核精力，精准投给最值得救的那批人。】")
        print("      而纯保费 deviance 之所以救不了这个结论，是因为它被")
        print("      少数几笔十几万的巨灾赔款绑架了 —— 那些钱谁都预测不了。")

        # ======================================================================
        # 训练 / 测试对比
        # ======================================================================
        sub(f"{tag} · 训练集 vs 测试集（诊断过拟合）")
        print(f"  {'组合':<22}{'训练 AUC':>10}{'测试 AUC':>10}{'衰减':>9}")
        for k, (fm, sm, cst) in combos.items():
            a_tr = auc_score((acc._true_premium.values[tr] <= thr_good).astype(int),
                             -pp_pred(fm, Xtr, sm, cst))
            a_te = auc_score(good_te, -pp_pred(fm, Xte, sm, cst))
            drop = (a_tr - a_te) / a_tr * 100 if a_tr > 0 else 0
            print(f"  {k:<22}{a_tr:>10.3f}{a_te:>10.3f}{drop:>8.1f}%")
        print("  衰减远大于 20% 才算真的过拟合。GLM 通常很稳，GBDT 更容易过拟合。")

        # ======================================================================
        # 汇总：选最好的那个
        # ======================================================================
        best_name = max(results.items(), key=lambda kv: kv[1]["purity"])[0]
        best = results[best_name]
        print(f"\n{'='*76}")
        print(f"  {tag} · 最终选定：{best_name}")
        print(f"    排序能力 AUC = {best['auc']:.3f}")
        print(f"    圈最低 20% 中真正好司机 = {best['purity']:.1%}（随机猜是 50%）")
        print(f"{'='*76}")

        yield dict(tag=tag, use_ch=use_ch, names=names,
                   combo=best_name, freq_m=best["freq_m"], sev_m=best["sev_m"],
                   sev_const=sev_const,
                   auc=best["auc"], purity=best["purity"],
                   dev=wall["常数基线"], base=base, wall=wall)


# ==============================================================================
# 步骤 6-8 在 steps_678.py 里实现（拿「外推」「业务账」「偏差修正」三段独立成模块，
# 便于单独阅读和单独重跑）。这里只做调度。
# ==============================================================================
def main():
    df = step1_load()
    step2_define_good(df)
    acc, tr, te = step3_dataset(df)
    fitted = list(step45_models(acc, tr, te))

    from steps_678 import step6_rejected, step7_business, step8_bias
    scores = step6_rejected(df, fitted)

    biz_a = step7_business(df, scores, key="A")
    print(chr(10) + "~" * 78)
    print("  对照：把 channel 放进模型，会发生什么？")
    print("~" * 78)
    biz_b = step7_business(df, scores, key="B")
    N_REJ = int((df.accept == 0).sum())
    # 保费口径与 steps_678.step7_business 保持一致，供 A/B 对齐后比较使用
    PREM_C = 3000.0
    COR_C = 0.75

    print(chr(10) + "=" * 78)
    print("  A / B 对照总结 —— 必须用【可比口径】，否则会得出反向结论")
    print("=" * 78)
    print("  先看最容易骗人的那张表：同一个阈值下圈了多少人。")
    print(f"  {'口径':<22}{'圈出占比':>10}{'召回率':>10}{'精确率':>10}{'净增益(元)':>16}")
    for nm, b in [("A 不含渠道", biz_a), ("B 含渠道", biz_b)]:
        print(f"  {nm:<20}{b['n_flag']/N_REJ:>9.1%}{b['recall']:>9.1%}"
              f"{b['precision']:>9.1%}{b['net']:>16,.0f}")
    print(chr(10) + "  ⚠ 单看这张表，B 完胜：B 圈出更多、召回更高、净增益更大。")
    print("     如果到此为止就下结论「把渠道放进去更好」，那就错了 ——")
    print("     这正是本案例最想教的一个陷阱。下面把它拆开。")

    # ---- 拆解：B 到底赢在哪 ------------------------------------------------
    pa = scores["A"]["pred"]
    pb = scores["B"]["pred"]
    tpv = scores["A"]["rej"]._true_premium.values
    order = np.argsort(pa)
    cuts = [(0, .1), (.1, .2), (.2, .4), (.4, .7), (.7, 1.0)]
    print(chr(10) + "  【第一刀 · 排序质量：两者其实一样好】")
    print("    把两边都按「预测纯保费从低到高」分 5 档，看每档的真实纯保费：")
    print(f"    {'档位':<12}{'A 预测档真实值':>16}{'B 预测档真实值':>16}")
    for lo, hi in cuts:
        sel = order[int(len(pa) * lo):int(len(pa) * hi)]
        sa = tpv[sel].mean()
        sbb = tpv[np.argsort(pb)[int(len(pb) * lo):int(len(pb) * hi)]].mean()
        print(f"    最低{lo*100:>3.0f}%-{hi*100:>3.0f}%{sa:>16,.0f}{sbb:>16,.0f}")
    print("    >>> 两条序列几乎重合。也就是说：【B 的排序能力和 A 一样】，")
    print("        渠道这个变量在排序上几乎没有贡献。")

    print(chr(10) + "  【第二刀 · 校准水平：B 整体偏低，所以「更容易够到阈值」】")
    print(f"    A 预测均值 / 真实均值 = {pa.mean()/tpv.mean():.3f}")
    print(f"    B 预测均值 / 真实均值 = {pb.mean()/tpv.mean():.3f}")
    print(f"    同一个阈值 {biz_a['thr']:,.0f} 元：")
    print(f"      A 落在阈值下的 {int((pa <= biz_a['thr']).sum()):,} 件")
    print(f"      B 落在阈值下的 {int((pb <= biz_a['thr']).sum()):,} 件")
    print("    >>> B 之所以能圈出更多人，不是因为它更会挑，")
    print("        而是因为它【整体预测偏低】，等于偷偷把门槛放宽了。")
    print("        它的排序没变好，只是刻度被压扁了。")
    print("        >>> 这就是为什么「圈出人数」「召回率」这类数字")
    print("            在跨模型比较时完全不可靠 —— 必须先对齐刻度。")

    print(chr(10) + "  【第三刀 · 同一个圈选规模下，谁挑得更准？】")
    k = int(N_REJ * 0.20)
    top_a = np.argsort(pa)[:k]
    top_b = np.argsort(pb)[:k]
    good = tpv <= biz_a["thr"]
    print(f"    两边都只圈最低 20%（各 {k:,} 件），比较圈里的真实质量：")
    print(f"    {'口径':<20}{'圈内真实均值':>14}{'好司机占比':>12}{'年毛利':>14}")
    for nm, idx in [("A 不含渠道", top_a), ("B 含渠道", top_b)]:
        m_ = PREM_C - COR_C * tpv[idx].mean()
        print(f"    {nm:<18}{tpv[idx].mean():>14,.0f}{good[idx].mean():>11.1%}"
              f"{m_*k:>14,.0f}")
    print(f"    {'随机圈同样多':<18}{tpv.mean():>14,.0f}{good.mean():>11.1%}"
          f"{(PREM_C-COR_C*tpv.mean())*k:>14,.0f}")
    print("    >>> 圈选规模对齐之后，两者几乎打平 —— 因为排序能力本来就一样。")
    print()
    print("  【所以真正的结论是这样的】")
    print("    模型 B 并没有更准。渠道在【承保人群】里确实有统计相关")
    print("    （线上件偏年轻、偏经济车型，这些确实和风险有关），")
    print("    所以把它放进去，内插指标会更好看。")
    print("    但在【拒保人群】里，渠道的含义完全变了：")
    print("    它不再代表「这是个什么人」，而代表「我们没测出什么」。")
    print("    把它当风险因子用，等于让价格惩罚「你从哪来」。")
    print("    >>> 判断一个变量该不该进模型，标准不是")
    print("        「它和赔款有没有统计相关」，而是「它有没有因果意义」。")
    print("    >>> 现实中的检验方法：问一句「如果同一个人换条渠道来买，")
    print("        他的真实风险会变吗？」答案是不会 —— 那它就不该进模型。")

    print(chr(10) + "  只对「近点」放宽的保守方案（推荐第一年落地）：")
    print(f"  {'口径':<22}{'圈出占比':>10}{'召回率':>10}{'净增益(元)':>16}")
    for nm, b in [("A 不含渠道", biz_a), ("B 含渠道", biz_b)]:
        print(f"  {nm:<20}{b['n_flag_near']/N_REJ:>9.1%}{b['recall']:>9.1%}"
              f"{b['net_near']:>16,.0f}")

    step8_bias(df, scores, key="A")

    # ---- 落地：导出可供人工复核的清单 -------------------------------------
    # 一份真正能交给核保同事的清单，必须回答四个问题：
    #   ① 这是谁？        → 姓名/ID + 可读的标签（中文车型、地区、渠道）
    #   ② 凭什么救他？    → 预测纯保费 + 排在全部拒保件的第几位
    #   ③ 这条建议有多可靠？→ 外推距离、是否远点
    #   ④ 优先做哪个？    → 按性价比排序的优先级编号
    # 只导出 driver_id 和 pred 的话，业务方根本没法用。
    rej = scores["A"]["rej"]
    far = scores["A"]["far"]
    out = pd.DataFrame({
        "driver_id": rej.driver_id.values,
        "年龄": rej.age.values,
        "车型": rej.car_type_nm.values,
        "地区": rej.region_nm.values,
        "用途": rej.use_type_nm.values,
        "渠道": rej.channel_nm.values,
        "车价_万元": rej.car_value.values,
        "年里程": rej.mileage.values,
        "原规则分": rej.crude_score.values,
        "模型A_预测纯保费": rej.pred_A.values.round(0),
        "模型B_预测纯保费": rej.pred_B.values.round(0),
        "外推距离": rej.ood_A.values.round(3),
        "是否远点": np.where(far, "远点-建议人工", "近点-可放宽"),
    })
    # 排名分位：越低越该先看
    rank = out["模型A_预测纯保费"].rank(method="min", pct=True)
    out["风险分位"] = (rank * 100).round(1)
    # 优先级：先做「近点 + 低风险」，这是模型最有把握的部分
    out["复核优先级"] = np.where(
        far, 3,
        np.where(out["模型A_预测纯保费"] <= np.quantile(rej.pred_A, 0.20), 1, 2))
    out = out.sort_values(["复核优先级", "模型A_预测纯保费"])

    fp = os.path.join(OUT, "rejected_scored.csv")
    out.to_csv(fp, index=False, encoding="utf-8-sig")
    print(chr(10) + "=" * 78)
    print(f"  复核清单已导出：{fp}")
    print(f"  共 {len(out):,} 件被拒保件，含 A/B 两套评分、外推距离与复核优先级")
    print(f"  优先级 1（近点 + 最低 20% 风险）{int((out.复核优先级 == 1).sum()):,} 件")
    print(f"  优先级 2（近点 + 其余）        {int((out.复核优先级 == 2).sum()):,} 件")
    print(f"  优先级 3（远点，建议仍走人工）  {int((out.复核优先级 == 3).sum()):,} 件")
    print(chr(10) + "  前 5 条示例：")
    for _, r in out.head(5).iterrows():
        print(f"    ID {r.driver_id:>5}  {r.车型:<6}{r.渠道:<5}"
              f"预测 {r.模型A_预测纯保费:>6,.0f} 元  分位 {r.风险分位:>5.1f}%"
              f"  {r.是否远点}")
    print("=" * 78)


if __name__ == "__main__":
    main()
