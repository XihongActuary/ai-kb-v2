# -*- coding: utf-8 -*-
"""
参数扫描：为 crude_score 找一组「梯度成立」的系数。

判据（三条同时满足）：
  1. 每一类特征水平的承保率都在 5%~70% 之间 —— 训练集必须见过它们，
     且不能是「全放行」这种没有区分度的状态。
  2. 拒保人群真实纯保费的 P10 < 承保人群中位数 < P90 —— 风险呈梯度。
  3. 线上渠道错杀率明显高于代理/直销 —— 错杀主因必须是渠道偏见。
"""
import itertools
import numpy as np


def score_of(a, cv, ct, rg, mi, ut, ch, P):
    s = P["base"]
    s = s + P["k_use"] * (ut == 1) * 20
    s = s + P["k_car3"] * (ct == 3) * 20
    s = s + P["k_car1"] * (ct == 1) * 20
    s = s + P["k_reg3"] * (rg == 3) * 20
    s = s + P["k_age"] * np.maximum(a - P["age_hi"], 0)
    s = s + P["k_young"] * np.maximum(P["age_lo"] - a, 0)
    s = s + P["k_mile"] * np.log(np.clip(mi, 1500, None) / 15500) * 20
    s = s - P["k_val"] * (cv - 21)
    s = s + P["k_ch"] * (ch == 2)
    return s


def true_prem(a, cv, ct, rg, mi, ut, ch, rng, CAR_FREQ, CAR_SEV,
               REGION_RISK, REGION_SEV, CAT_LOAD):
    eta = (0.012 * (a - 38)
           + 0.30 * (ct == 3) + 0.086 * (ct == 1)
           - 0.10 * (ct == 2) + 0.13 * (rg == 3)
           + 0.186 * (ut == 1)
           + 0.42 * np.log(np.clip(mi, 1500, None) / 15500)
           - 0.16 * np.log(np.clip(cv, 4, None) / 21))
    freq = 0.075 * np.exp(eta)
    sev = 12000 * CAR_SEV[ct] * REGION_SEV[rg] * np.exp(0.18 * (cv - 21) / 21)
    return freq * sev + CAT_LOAD


def evaluate(P, feats, tp, names):
    a, cv, ct, rg, mi, ut, ch = feats
    s = score_of(a, cv, ct, rg, mi, ut, ch, P)
    thr = float(np.quantile(s, 0.56))
    acc = s <= thr
    # 1. 各水平承保率
    rates = {}
    for col, arr, n_lv in [("car_type", ct, 4), ("region", rg, 5),
                           ("use_type", ut, 2), ("channel", ch, 3)]:
        rates[col] = [float(acc[arr == i].mean()) for i in range(n_lv)]
    ok1 = all(0.05 <= r <= 0.70 for v in rates.values() for r in v)
    # 2. 梯度
    rej = ~acc
    q = np.percentile(tp[rej], [10, 50, 90])
    amed = float(np.median(tp[acc]))
    ok2 = q[0] < amed < q[2]
    # 3. 线上错杀率显著更高
    med = amed
    wg = []
    for i in range(3):
        m = rej & (ch == i)
        wg.append(float((tp[m] <= med).mean()) if m.sum() else 0.0)
    ok3 = wg[2] > wg[0] * 1.4 and wg[2] > wg[1] * 1.4
    return ok1 and ok2 and ok3, rates, (amed, q), wg, thr


def main():
    rng = np.random.default_rng(20261003)
    N = 60000
    age = np.clip(rng.normal(38, 12, N), 18, 75).round().astype(int)
    car_value = np.exp(rng.normal(np.log(21), 0.62, N)).round(1)
    car_value = np.clip(car_value, 4, 95)
    car_type = rng.choice(4, N, p=[0.44, 0.33, 0.19, 0.04])
    region = rng.choice(5, N, p=[0.29, 0.20, 0.24, 0.16, 0.11])
    use_type = rng.choice(2, N, p=[0.89, 0.11])
    p_online = 0.16 + 0.006 * (38 - age) + 0.20 * (car_type == 0) + 0.05 * (car_type == 2)
    channel = np.where(rng.random(N) < np.clip(p_online, 0.05, 0.55), 2,
                       np.where(rng.random(N) < 0.42, 0, 1))
    mileage = np.exp(rng.normal(np.log(15500), 0.50, N)).round(0)
    mileage = np.clip(mileage, 1800, 62000).astype(int)
    feats = (age, car_value, car_type, region, mileage, use_type, channel)

    CAR_FREQ = np.array([1.00, 1.10, 0.96, 1.34])
    CAR_SEV = np.array([0.92, 1.05, 1.22, 1.75])
    REGION_RISK = np.array([1.00, 0.94, 1.09, 1.16, 0.97])
    REGION_SEV = np.array([1.06, 0.98, 1.12, 0.90, 1.00])
    CAT_LOAD = 0.0025 * np.exp(np.log(62000.0) + 0.5 * 0.85 ** 2)
    tp = true_prem(age, car_value, car_type, region, mileage, use_type, channel,
                   rng, CAR_FREQ, CAR_SEV, REGION_RISK, REGION_SEV, CAT_LOAD)

    best = None
    n_ok = 0
    grid = itertools.product(
        [26.0, 28.0],            # base
        [0.20, 0.26, 0.32],      # k_use  营运
        [0.16, 0.24],            # k_car3 性能车
        [0.10, 0.16],            # k_car1 SUV
        [0.12, 0.18],            # k_reg3 西部
        [0.26, 0.36],            # k_age  高龄
        [0.22, 0.30],            # k_young 低龄
        [0.05, 0.07],            # k_mile
        [0.025, 0.035],          # k_val
        [6.0, 7.0, 8.0],         # k_ch  渠道偏见
    )
    n = 0
    for (base, ku, k3, k1, kr, ka, ky, km, kv, kch) in grid:
        P = dict(base=base, k_use=ku, k_car3=k3, k_car1=k1, k_reg3=kr,
                 k_age=ka, k_young=ky, k_mile=km, k_val=kv, k_ch=kch,
                 age_hi=58, age_lo=26)
        ok, rates, grad, wg, thr = evaluate(P, feats, tp, None)
        n += 1
        if not ok:
            continue
        n_ok += 1
        # 打分：偏好渠道错杀差距大、梯度宽、各水平承保率居中
        spread = grad[2][2] - grad[1][0]
        balance = min(min(v) for v in rates.values()) * 10
        score = (wg[2] - max(wg[0], wg[1])) * 100 + spread / 100.0 + balance
        if best is None or score > best[0]:
            best = (score, P, rates, grad, wg, thr)
    print(f"扫描 {n} 组，同时满足三条判据的 {n_ok} 组")
    if best is None:
        print("没有组合同时满足三条判据，需要放宽约束或调整真实风险系数")
        return
    score, P, rates, grad, wg, thr = best
    print("\n=== 最优组合 ===")
    for k, v in P.items():
        print(f"  {k:8s} = {v}")
    print(f"\n阈值 = {thr:.2f}")
    print("各水平承保率：")
    for col, v in rates.items():
        print(f"  {col:10s} " + "  ".join(f"{x:.1%}" for x in v))
    amed, q = grad
    print(f"\n承保人群中位数 {amed:,.0f} 元")
    print(f"拒保人群 P10/P50/P90 = {q[0]:,.0f} / {q[1]:,.0f} / {q[2]:,.0f} 元")
    print(f"错杀率 代理={wg[0]:.1%} 直销={wg[1]:.1%} 线上={wg[2]:.1%}")


if __name__ == "__main__":
    main()
