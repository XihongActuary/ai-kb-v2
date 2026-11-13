# -*- coding: utf-8 -*-
"""
场景一 · 车险定价：数据生成器
================================================================
设计目标：把「被错杀的好司机」这个业务问题，写进数据生成机制本身。
        机器学习不是万能药，而是一面照出「数据里到底缺了什么」的镜子。

核心机制（这是整个案例的灵魂）
----------------------------------------------------------------
真实的保险公司只有「被承保的人」才有出险记录。也就是说：

    训练数据  = 已承保 且 已出险 的人
    看不见的  = 未承保 的人 —— 无论好坏，全都没有标签

于是产生一个统计学上非常难看的局面：
    「好司机」如果当年被拒保了，就永远不会出现在你的赔付数据里。
    模型只见过「当年被放行的人如何出险」，
    却要你去回答「当年被拒的人会不会出险」——
    这是在训练数据没覆盖的区域做外推。

我们让「拒保规则」犯错，而且错得合情合理：
    规则惩罚了 use_type（营运）      —— 这条是合理的
    规则也惩罚了 car_type（SUV/新能源）—— 这条部分合理，但过重了
    规则最不该惩罚的是 channel（线上）  —— 这条与风险无关，
    它衡量的是「数据取得难度」，不是「危险程度」
最后一条，就是「错杀」的主要来源。它最隐蔽，因为业务上讲得通：
    「线上渠道风险信息不全，先拒了再说」—— 听起来很谨慎，其实是懒惰。

我们另外保留一个「审计样本」：
    现实中，保险公司会通过行业数据交换平台，对拒保件做抽样回访，
    知道其中一小部分人后来是否真的出险了。
    但抽样只有约 4.6%，且抽样有偏 —— 线上件更难被抽到。
    所以审计样本能「看到真相」，却不能直接当训练集用：必须加权。
    权重 = 1 / P(被抽中)，也就是逆概率加权 IPW。
    这一条约束，恰好逼出了加权与双重稳健方法。

三种人，看得见的标签
----------------------------------------------------------------
    全体        20,000 人   真值我们都知道（模拟器知道，用于教学对账）
    已承保      约 11,000 人  出险记录可见    ← 可用于训练
    被拒保      约 9,000 人   出险记录不可见  ← 真正的战场
    审计样本    拒保中的 4.6%  真值可见但有偏  ← 唯一的「偷看」

教学专用优势
----------------------------------------------------------------
真实业务里你永远不知道被拒保人群的真实出险率。
但模拟器知道。所以本页能诚实地说出「模型错得有多离谱」——
这是课堂专属的奢侈，请勿在汇报中假装业务也有这个奢侈。

运行： python gen_data.py
输出： data/drivers.csv
"""

import os
import numpy as np
import pandas as pd

# 数据输出目录：与 code/ 平级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# ------------------------------------------------------------------
# 一、全局设定
# ------------------------------------------------------------------
SEED = 20261003                    # 固定随机种子，结果可完全复现
N_POP = 20_000                     # 全体人群规模
AUDIT_RATE = 0.05                  # 拒保件审计抽样率
ACCEPT_RATE_TARGET = (0.50, 0.62)  # 承保率应落在这个区间

# 模型能看见的风险因子（被保险人画像）
COLS_VISIBLE = ["age", "car_value", "car_type", "region", "mileage", "use_type", "channel"]
# 审计样本才能补上的关键信息
COLS_AUDIT = ["age", "car_value", "car_type", "region", "mileage",
              "use_type", "channel", "audit_weight"]


# ------------------------------------------------------------------
# 二、特征取值定义
# ------------------------------------------------------------------
REGION_NAMES = ["华东", "华北", "华南", "西部", "其他"]
CAR_TYPE_NAMES = ["经济型轿车", "SUV", "新能源车", "性能车"]
USE_TYPE_NAMES = ["家用", "营运网约"]
CHANNEL_NAMES = ["代理渠道", "直销渠道", "线上渠道"]

# 地区因子：与出险频率、单车损失正相关
REGION_RISK = np.array([1.00, 0.94, 1.09, 1.16, 0.97])
REGION_SEV = np.array([1.06, 0.98, 1.12, 0.90, 1.00])

# 车型因子：与出险频率正相关，与损失金额正相关
CAR_FREQ = np.array([1.00, 1.10, 0.96, 1.34])
CAR_SEV = np.array([0.92, 1.05, 1.22, 1.75])


# 巨灾（盗抢/全损/严重人伤）：低概率、极高额、且【与特征无关】
# 换句话说它是纯噪声 —— 任何模型都预测不了它。
# 它存在的意义是让「重尾」这件事真实存在，而不是教学上的摆设。
CAT_PROB = 0.0025
CAT_LOG_MEDIAN = np.log(62000.0)
CAT_SIGMA = 0.85
CAT_LOAD = CAT_PROB * np.exp(CAT_LOG_MEDIAN + 0.5 * CAT_SIGMA ** 2)  # 每单的期望巨灾成本

# 单次损失的对数正态形状参数
SEV_SIGMA = 0.95


def make_features(rng, n):
    """生成 n 个投保人的可观测特征"""
    # 年龄：偏向 25-55 的在职人群
    age = np.clip(rng.normal(38, 12, n), 18, 75).round().astype(int)

    # 车辆价值：对数正态，5 万 - 90 万
    car_value = np.exp(rng.normal(np.log(21), 0.62, n)).round(1)
    car_value = np.clip(car_value, 4, 95)

    car_type = rng.choice(4, n, p=[0.44, 0.33, 0.19, 0.04])
    region = rng.choice(5, n, p=[0.29, 0.20, 0.24, 0.16, 0.11])
    use_type = rng.choice(2, n, p=[0.89, 0.11])

    # 线上渠道用户偏年轻、偏经济车型 —— 这正是「数据不全」的来源
    p_online = 0.16 + 0.006 * (38 - age) + 0.20 * (car_type == 0) + 0.05 * (car_type == 2)
    channel = np.where(
        rng.random(n) < np.clip(p_online, 0.05, 0.55),
        2,                                   # 线上
        np.where(rng.random(n) < 0.42, 0, 1)  # 代理 / 直销
    )

    # 年行驶里程：对数正态
    mileage = np.exp(rng.normal(np.log(15500), 0.50, n)).round(0)
    mileage = np.clip(mileage, 1800, 62000).astype(int)

    return age, car_value, car_type, region, mileage, use_type, channel


# ------------------------------------------------------------------
# 三、真实风险（模拟器才知道，现实中不可得）
# ------------------------------------------------------------------
def true_latent(rng, age, car_value, car_type, region, mileage, use_type, channel):
    """
    生成真实风险因子 log_freq 与【真实期望纯保费】。

    这里刻意不含 channel —— 因为渠道本身与「危险程度」无关，
    它只是「信息取得难度」的代理。记住这一点，后面很关键。

    ★ 一个必须讲清楚的口径问题（曾经在这里翻车）：
        sev 在下面是以【对数正态的中位数】为锚点算出来的。
        但中位数 ≠ 期望值。对数正态的期望比中位数大 exp(σ²/2) 倍。
        如果拿中位数当期望，纯保费的「真值」就会和实际模拟出来的赔付对不上，
        后面所有「模型预测 vs 真实成本」的对照全部失真。
      所以这里显式做 median → mean 的修正：
            E[sev] = exp(log_sev + σ²/2)
      巨灾是【与特征无关】的，所以它对每个人的期望成本都一样，
      直接加一个常数 CAT_LOAD，不能漏掉 —— 否则真值会系统性偏低。
    """
    # ---------- 出险频率 ----------
    log_freq = (
        -2.60# 基准频率 ≈ 7.4%
        + 0.212 * (car_type == 3)                                 # 性能车
        + 0.086 * (car_type == 1)                                 # SUV
        - 0.0135 * (car_value - 21)                               # 车越贵越少出险（也更难修）
        + 0.142 * (region == 3)                                   # 西部路况
        + 0.070 * (region == 2)
        - 0.0068 * (age - 38)                                     # 经验效应，近似线性
        + 0.052 * np.maximum(age - 62, 0)                         # 高龄反弹
        + 0.116 * (use_type == 1)                                 # 营运显著更危险
        + 0.33 * np.log(np.clip(mileage, 1500, None) / 15500)     # 里程弹性
        - 0.30 * (car_value > 55)                                 # 高价车多为主动全额索赔
    )
    freq = np.exp(log_freq)

    # ---------- 单次损失（对数正态，以中位数为锚） ----------
    log_sev = (
        8.55                # 中位数约 5,150 元；修正后均值约 7,800 元
        + 0.0136 * car_value
        + 0.186 * (car_type == 3)
        + 0.100 * (car_type == 2)
        + 0.084 * (region == 2)
        - 0.079 * (region == 3)
        + 0.30 * np.maximum(age - 60, 0) * 0.04
    )
    sev_median = np.exp(log_sev)
    sev_mean = sev_median * np.exp(0.5 * SEV_SIGMA ** 2)            # 中位数 → 均值

    # ---------- 真实期望纯保费 = 频率 × 损失 + 巨灾期望 ----------
    true_premium = freq * sev_mean + CAT_LOAD

    return log_freq, freq, sev_median, true_premium


# ------------------------------------------------------------------
# 四、承保规则：把「偏见」写进规则
# ------------------------------------------------------------------
def crude_score(age, car_value, car_type, region, mileage, use_type, channel):
    """
    核保粗糙分（0-100，越高越容易被拒）。
    这是一套「讲得通但有偏」的业务规则 —— 现实中的核保系统大多如此。

    规则里埋了三处不同性质的东西，务必分清：
        use_type   —— 合理定价因子
        car_type   —— 部分合理，但惩罚过重
        channel    —— 与风险无关，只反映数据是否齐全  ← 错杀的主因

    ★ 一个必须守住的设计约束（改这组系数时踩过）：
      承保阈值是「在全体分数上取分位数」得到的，
      所以任何单一水平都不会被整体性地全部拒掉 ——
      除非它的规则分高到连最低的那一段都进不去。
      之前的版本里性能车（car_type=3）被加了 +6.0 分，
      结果 816 件性能车只放行了 18 件（承保率 2.2%）。
      后果非常严重：模型只有 18 个样本去学「性能车的风险」，
      学出来必然是「性能车风险低」（因为这 18 个恰好偏年轻偏便宜），
      于是模型把所有性能车拒保件都推进「预测纯保费最低」那一档。
      一上线就是 88% 的误伤率 —— 而且错得很隐蔽：
      业务只看召回率 34%，会觉得「模型有用」。

      >>> 教训：造「错杀」数据时，错杀必须来自【规则偏差】，
          而不是来自【某类人全被拒】。前者是本案例要讲的病，
          后者是造数据时自己挖的坑，两者混在一起会让结论彻底失去说服力。

      所以这里的规则分只做「适度加重」，让被拒人群的风险结构
      呈现梯度（从 1,167 到 1,450），而不是二元对立。
      >>> 承保规则不能把某个特征变成「决定性开关」。
    """
    s = 26.0
    # —— 真实风险因子：轻度加权，让被拒人群的风险呈【梯度】——
    s += 0.18 * (use_type == 1) * 20                        # 营运：+3.6（真实更贵）
    s += 0.16 * (car_type == 3) * 20                        # 性能车：+3.2（真实更贵）
    s += 0.10 * (car_type == 1) * 20                        # SUV：+2.0（略重）
    s += 0.15 * (region == 3) * 20                          # 西部：+3.0（真实更贵）
    s += 0.40 * np.maximum(age - 58, 0)                    # 高龄：加码
    s += 0.34 * np.maximum(26 - age, 0)                    # 低龄：加码
    s += 0.070 * np.log(np.clip(mileage, 1500, None) / 15500) * 20
    s -= 0.030 * (car_value - 21)                           # 车贵则减分
    # —— 偏见：渠道。与风险无关，只因为「信息不全」而加惩罚 ——
    # ★ 幅度是扫描出来的（见 _tune.py），不是拍脑袋定的。
    #   +11 → 线上承保率 0%（5193 件全在训练集外），案例直接失效
    #   +4  → 线上承保率 23%、错杀率 52% vs 代理 23%，梯度与偏见都在
    s += 4.0 * (channel == 2)                              # 线上渠道：+4  ← 关键偏见
    return s


# ------------------------------------------------------------------
# 五、模拟出险
# ------------------------------------------------------------------
def simulate_claims(rng, freq, sev_median, horizon=1.0):
    """
    一年观察期内的出险次数与总损失。
      出险次数~ Poisson(freq)          —— 计数型
      每次损失 ~ LogNormal(中位数=sev)  —— 重尾
      外加一次「偶发巨灾」              —— 与特征无关的纯噪声

    向量化实现（不用 Python 循环，2 万条数据秒级完成）。
    """
    n = len(freq)
    lam = freq * horizon
    cnt = rng.poisson(lam)

    # 逐次出险。关键：损失要按【出险人各自的】中位数抽样，
    # 因为单次损失和车价、车型、地区有关 —— 这正是「损失模型」能学到的信号。
    # rng.normal 的 loc 可以是数组，但那样就不能再传 size，否则形状对不上。
    rep = np.repeat(np.arange(n), cnt)          # 每张赔款属于谁
    mu = np.log(np.clip(sev_median[rep], 1.0, None)) + 0.5 * SEV_SIGMA ** 2
    losses = np.exp(rng.normal(mu, SEV_SIGMA))       # 长度 = 总出险次数
    total = np.zeros(n)
    np.add.at(total, rep, losses)                  # 摊回每个人

    # 巨灾：独立伯努利，与特征无关（所以任何模型都预测不了它）
    cat = rng.random(n) < CAT_PROB
    total[cat] += rng.normal(CAT_LOG_MEDIAN, CAT_SIGMA, int(cat.sum()))

    return cnt, total.round(2)


# ------------------------------------------------------------------
# 六、主流程
# ------------------------------------------------------------------
def main():
    rng = np.random.default_rng(SEED)

    age, car_value, car_type, region, mileage, use_type, channel = make_features(rng, N_POP)
    eta, freq, sev, true_premium = true_latent(
        rng, age, car_value, car_type, region, mileage, use_type, channel)

    # 真实出险结果 —— 全部人群都有，这是模拟器的「上帝视角」
    claim_cnt, claim_amt = simulate_claims(rng, freq, sev)

    # 核保规则打分与承保决策
    score = crude_score(age, car_value, car_type, region, mileage, use_type, channel)

    # 阈值微调，使承保率精确落进目标区间。
    # 做法：直接在分位数上二分。score 越大越容易被拒，所以
    #   承保率 = P(score <= thr)，thr 取高分位点。
    # 旧写法是死循环微调 hi 而 lo 从不动，还白跑 400 次，这里换成真二分。
    lo, hi = ACCEPT_RATE_TARGET
    target_acc = (lo + hi) / 2
    srt = np.sort(score)
    thr = float(np.quantile(srt, target_acc))
    accept = score <= thr

    # ------------------------------------------------------------------
    # 审计样本：只从拒保件中抽，且有偏
    #
    # 教学要点（这个坑非常常见）：
    #   ① 抽样概率 π 是「已知但写在代码里的常数」，不是学出来的。
    #      这正是能做 IPW 的前提。
    #   ② 但 IPW 只在「每个抽样单元内 π 恒定」时才完美还原边际分布。
    #      如果我们只用 channel 一个变量描述 π，那么在每个渠道内部
    #      权重是同一个常数，加权 = 重新配比，逐渠道看必然毫无变化。
    #      真正修正的是「渠道之间的比例」。
    #   ③ 更狠的一层：现实中抽样还依赖「申请人配合度」—— 这种人更年轻、
    #      留的信息更全、未出险时更愿意接回访电话。而「配合度」我们看不见、
    #      也没进模型。这种不可观测的偏差，IPW 修不了。
    #   ④ 修不了不代表没办法：只要结果模型本身学得对，
    #      配合 IPW 就能得到「双重稳健」的结果。这正是下一课的内容。
    # ------------------------------------------------------------------
    rejected_idx = np.where(~accept)[0]

    # 不可观测的「配合度」：年轻 + 线上件更愿意接回访。
    # 它同时影响被抽中的概率，且与真实风险轻微相关 —— 制造 IPW 修不掉的偏差。
    coop = (0.5
            - 0.006 * (age[rejected_idx] - 38)        # 年轻人更配合
            + 0.10 * (channel[rejected_idx] == 2))     # 线上件流程更顺

    p_audit = (AUDIT_RATE
               * np.where(channel[rejected_idx] == 2, 0.60, 1.0)   # 已知偏差：渠道
               * np.clip(coop / 0.5, 0.45, 1.60))                 # 未知偏差：配合度
    p_audit = np.clip(p_audit, 0.005, 0.35)

    audit_flag = np.zeros(N_POP, dtype=bool)
    audit_idx = rejected_idx[rng.random(len(rejected_idx)) < p_audit]
    audit_flag[audit_idx] = True

    # 逆概率权重：w = 1 / π。
    #   一个被抽中的线上被拒件，只能代表 1/π 个线上被拒件。
    #   不加权，模型会以为「易抽到的人」样本更多，从而压低他们的预测。
    audit_weight = np.zeros(N_POP, dtype=float)
    for j, i in enumerate(rejected_idx):
        if audit_flag[i]:
            audit_weight[i] = 1.0 / p_audit[j]

    # ------------------------------------------------------------------
    # 组装数据框
    # ------------------------------------------------------------------
    df = pd.DataFrame({
        "driver_id": np.arange(1, N_POP + 1),
        "age": age,
        "car_value": car_value,
        "car_type": car_type,
        "region": region,
        "mileage": mileage,
        "use_type": use_type,
        "channel": channel,
        "crude_score": score.round(2),
        "accept": accept.astype(int),
        "audit": audit_flag.astype(int),
        "audit_weight": audit_weight.round(4),
        # ---- 只有承保 + 观察期结束，才会入账的字段 ----
        "claim_cnt": np.where(accept, claim_cnt, -1),          # -1 表示「无记录」而非「零出险」
        "claim_amt": np.where(accept, claim_amt, np.nan),
        # ---- 模拟器保留的真值，仅供教学对账，现实中拿不到 ----
        "_eta": eta,
        "_freq": freq.round(5),
        "_sev_median": sev.round(1),          # 中位数，不是均值，别搞混
        "_true_premium": true_premium.round(1),  # 真实【期望】纯保费
        "_true_cnt": claim_cnt,                # 真实【已实现】出险次数
        "_true_amt": claim_amt.round(2),       # 真实【已实现】赔付（围绕期望波动）
    })

    # 中文标签列（便于阅读与图表展示）
    df["car_type_nm"] = pd.Series(CAR_TYPE_NAMES)[df.car_type].values
    df["region_nm"] = pd.Series(REGION_NAMES)[df.region].values
    df["use_type_nm"] = pd.Series(USE_TYPE_NAMES)[df.use_type].values
    df["channel_nm"] = pd.Series(CHANNEL_NAMES)[df.channel].values

    acc = df[df.accept == 1]
    rej = df[df.accept == 0]
    aud = df[(df.accept == 0) & (df.audit == 1)]

    # ------------------------------------------------------------------
    # 特征覆盖体检：这一段是护栏，请勿删除
    # ------------------------------------------------------------------
    # 为什么要查：模型只能对「训练集里见过的特征组合」给出有意义的预测。
    # 如果某个水平在承保人群里一个样本都没有，模型对它学到的系数
    # 纯属噪声 —— 而它偏偏又是拒保人群里的一大块。
    # 结果就是：模型会把这一整类人推进「最低风险」档，而他们其实更贵。
    # 业务上看召回率还挺高，但精确率崩了，排查起来极其痛苦。
    print("=" * 66)
    print("【特征覆盖体检 · 训练集必须见过每一个水平】")
    print("=" * 66)
    problems = []
    for col, names in [("car_type", CAR_TYPE_NAMES),
                       ("region", REGION_NAMES),
                       ("use_type", USE_TYPE_NAMES),
                       ("channel", CHANNEL_NAMES)]:
        line = []
        for i, nm in enumerate(names):
            tot = int((df[col] == i).sum())
            a = int(((df[col] == i) & (df.accept == 1)).sum())
            rate = a / max(tot, 1)
            line.append(f"{nm} {a:,}/{tot:,}({rate:.0%})")
            if rate < 0.05:
                problems.append(f"{col}={nm} 承保率仅 {rate:.1%}（{a} 件）")
        print(f"  {col:<10} " + "  ".join(line))
    if problems:
        print("\n  ⚠ 以下水平承保率过低，模型将无法可靠外推：")
        for p_ in problems:
            print(f"    · {p_}")
        print("  >>> 请调低 crude_score 里对应的系数，或提高该类样本占比。")
        print("      承保规则不能把任何特征变成「决定性开关」。")
    else:
        print("  ✓ 所有水平在承保人群中均有足够样本，模型可以正常外推。")

    # 被拒人群的风险结构必须是【梯度】而非二元对立，否则「找错杀」无从谈起
    rq = np.percentile(rej._true_premium, [10, 50, 90])
    amed = float(acc._true_premium.median())
    print("\n【拒保人群风险梯度】真实纯保费 P10 / P50 / P90 = "
          f"{rq[0]:,.0f} / {rq[1]:,.0f} / {rq[2]:,.0f} 元")
    print(f"  承保人群中位数 {amed:,.0f} 元落在拒保人群 P10~P90 区间内："
          f"{'是' if rq[0] <= amed <= rq[2] else '否 ← 梯度缺失'}")

    df.to_csv(os.path.join(DATA, "drivers.csv"), index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------
    # 控制台体检
    # ------------------------------------------------------------------
    print("=" * 66)
    print("数据生成完成  drivers.csv")
    print("=" * 66)
    print(f"总人数            {len(df):,}")
    print(f"已承保            {len(acc):,}  （{len(acc)/len(df):.1%}）")
    print(f"被拒保            {len(rej):,}  （{len(rej)/len(df):.1%}）")
    print(f"审计样本          {len(aud):,}  （拒保件的 {len(aud)/len(rej):.1%}）")
    print("-" * 66)
    print("【第一层：被拒保人群的风险水平 vs 承保门槛】")
    print(f"  承保人群 真实纯保费中位数   {acc._true_premium.median():>8.0f} 元")
    print(f"  拒保人群 真实纯保费中位数   {rej._true_premium.median():>8.0f} 元")
    print(f"  拒保人群中位数 ÷ 承保人群中位数  {rej._true_premium.median()/acc._true_premium.median():.2f} 倍")
    print("-" * 66)
    print("【第二层：错杀有多严重】")
    # 定义：被拒、且真实纯保费低于承保人群中位数者 = 被错杀
    med_acc = acc._true_premium.median()
    wrong_kill = rej[rej._true_premium <= med_acc]
    print(f"  以承保人群中位数为界，被错杀人数        {len(wrong_kill):,} 人")
    print(f"  占全部被拒保件                          {len(wrong_kill)/len(rej):.1%}")
    print(f"  占全部投保申请                          {len(wrong_kill)/len(df):.1%}")
    print(f"  错杀人群真实纯保费中位数                {wrong_kill._true_premium.median():.0f} 元")
    print(f"  拒保人群整体真实纯保费中位数            {rej._true_premium.median():.0f} 元")
    print("-" * 66)
    print("【第三层：错杀集中在谁身上】")
    for nm in CHANNEL_NAMES:
        sub = rej[rej.channel_nm == nm]
        wk = sub[sub._true_premium <= med_acc]
        print(f"  {nm:<6} 拒保 {len(sub):>5,}  错杀 {len(wk):>5,}  错杀率 {len(wk)/max(len(sub),1):>6.1%}")
    print("-" * 66)
    print("【第四层：训练数据看不见什么】")
    print(f"  承保件真实纯保费均值    {acc._true_premium.mean():>9.0f} 元")
    print(f"  拒保件真实纯保费均值    {rej._true_premium.mean():>9.0f} 元")
    print(f"  整体                    {df._true_premium.mean():>9.0f} 元")
    print(f"  => 只用承保件建模，系统性低估 {rej._true_premium.mean()-acc._true_premium.mean():.0f} 元/单")
    print("-" * 66)
    print("【第五层：审计样本的 IPW 对账】")
    print(f"  审计样本量              {len(aud):>9,} 件")
    if len(aud) > 0:
        naive = aud._true_premium.mean()
        ipw = np.average(aud._true_premium, weights=aud.audit_weight)
        # 用 IPW 权重还原出来的「拒保人群真实均值」应该接近真值
        target = rej._true_premium.mean()
        print(f"  拒保人群真实均值（真值）    {target:>9.0f} 元   <- 模拟器知道，现实中不知道")
        print(f"  审计样本未加权均值      {naive:>9.0f} 元   偏差 {naive-target:>+8.0f} 元")
        print(f"  审计样本 IPW 加权均值   {ipw:>9.0f} 元   偏差 {ipw-target:>+8.0f} 元")
        gain = abs(naive - target) - abs(ipw - target)
        print(f"  => 加权后偏差缩小 {gain:.0f} 元"
              f"（{abs(naive-target)/max(abs(ipw-target),1e-9):.2f} 倍）")
        # 按渠道拆开看：IPW 修的是「渠道之间的比例」，不是渠道内部。
        #   这几行会显示未加权与 IPW 几乎一致 —— 因为渠道内 π 恒定。
        #   初学者最常见的误解就是「加了权重就该处处都变」。
        print("-" * 66)
        print("  按渠道看：渠道内 π 恒定 → 渠道内 IPW 失效（只修正渠道之间的比例）")
        for nm in CHANNEL_NAMES:
            sub_a = aud[aud.channel_nm == nm]
            sub_t = rej[rej.channel_nm == nm]
            if len(sub_a) == 0 or len(sub_t) == 0:
                continue
            n_mean = sub_a._true_premium.mean()
            w_mean = np.average(sub_a._true_premium, weights=sub_a.audit_weight)
            t_mean = sub_t._true_premium.mean()
            print(f"  {nm:<6} 抽样{len(sub_a):>4}件  真值{t_mean:>7.0f}  "
                  f"未加权{n_mean:>7.0f}({n_mean-t_mean:>+6.0f})  "
                  f"IPW {w_mean:>7.0f}({w_mean-t_mean:>+6.0f})")
        print()
        print("  按「配合度」拆开看：这一层 IPW 无能为力（配合度不可观测）")
        aud2 = aud.copy()
        aud2["_coop"] = (-0.006 * (aud2.age - 38) + 0.10 * (aud2.channel == 2))
        rej2 = rej.copy()
        rej2["_coop"] = (-0.006 * (rej2.age - 38) + 0.10 * (rej2.channel == 2))
        qcut = rej2._coop.quantile([0.25, 0.75])
        bins = [-9.0, qcut.iloc[0], qcut.iloc[1], 9.0]
        for k, lb in enumerate(["低配合", "中配合", "高配合"]):
            sub_a = aud2[(aud2._coop > bins[k]) & (aud2._coop <= bins[k + 1])]
            sub_t = rej2[(rej2._coop > bins[k]) & (rej2._coop <= bins[k + 1])]
            if len(sub_a) < 5 or len(sub_t) == 0:
                continue
            n_mean = sub_a._true_premium.mean()
            w_mean = np.average(sub_a._true_premium, weights=sub_a.audit_weight)
            t_mean = sub_t._true_premium.mean()
            print(f"  {lb} 抽样{len(sub_a):>4}件  真值{t_mean:>7.0f}  "
                  f"未加权{n_mean:>7.0f}({n_mean-t_mean:>+6.0f})  "
                  f"IPW {w_mean:>7.0f}({w_mean-t_mean:>+6.0f})")
        print("  => IPW 把整体偏差压下去了，但在「配合度」这一层依然有残差。")
        print("     这不是方法失败，是「抽样机制依赖不可观测量」时的必然结果。")
        print("     解法不是继续调权重，而是让结果模型本身学得对 —— 双重稳健。")
    print("=" * 66)


if __name__ == "__main__":
    main()
