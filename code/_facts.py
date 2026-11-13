# -*- coding: utf-8 -*-
"""
事实表抽取器 —— 整个站点的【唯一数字来源】。

为什么要有这个文件：
  上一轮踩过一次：页面里写「拒掉 15% 好客户」，
  而真实数据已经是 25.7%。硬编码数字一定会腐烂。
  所以 13 个页面里的每一个数字，都必须从这里出，
  页面生成时用 facts.json 填充，禁止手写。

用法：
  python _facts.py          # 打印摘要并写出 out/facts.json
"""
import os
import re
import json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")

F = {}


def r(x, nd=0):
    return round(float(x), nd)


# ----------------------------------------------------------------- 规模
df = pd.read_csv(os.path.join(DATA, "drivers.csv"))
sc = pd.read_csv(os.path.join(OUT, "rejected_scored.csv"))
sc.columns = [c.lstrip("\ufeff") for c in sc.columns]

# ★ 必须按 driver_id 对齐，不能直接按行取。
#   导出清单是按预测升序排的（复核清单本来就该这么排），
#   而 drivers.csv 保持生成顺序。两者行序完全不同。
#   上一版就是在这里直接 sc[...].values 配 rej[...].values，
#   算出 AUC=0.508（等于随机），差点把整套结论推翻。

acc = df[df.accept == 1]
rej = df[df.accept == 0]
aud = df[(df.accept == 0) & (df.audit == 1)]
sc = sc.set_index("driver_id").loc[rej.driver_id.values].reset_index()

F["n_total"] = int(len(df))
F["n_acc"] = int(len(acc))
F["n_rej"] = int(len(rej))
F["n_aud"] = int(len(aud))
F["pct_acc"] = r(len(acc) / len(df) * 100, 1)
F["pct_rej"] = r(len(rej) / len(df) * 100, 1)
F["pct_aud"] = r(len(aud) / len(rej) * 100, 1)

# ----------------------------------------------------------------- 真值口径
F["true_prem_acc"] = r(acc._true_premium.mean())
F["true_prem_rej"] = r(rej._true_premium.mean())
F["true_prem_med_acc"] = r(acc._true_premium.median())
F["true_prem_med_rej"] = r(rej._true_premium.median())
GOOD = float(acc._true_premium.median())
F["good_threshold"] = r(GOOD)

# ----------------------------------------------------------------- 错杀
true_good = rej._true_premium.values <= GOOD
F["n_wrongly_killed"] = int(true_good.sum())
F["pct_killed_of_rej"] = r(true_good.sum() / len(rej) * 100, 1)
F["pct_killed_of_all"] = r(true_good.sum() / len(df) * 100, 1)
F["true_prem_killed"] = r(rej._true_premium.values[true_good].mean())

# 拒保人群风险梯度
q = np.percentile(rej._true_premium, [10, 50, 90])
F["rej_p10"], F["rej_p50"], F["rej_p90"] = r(q[0]), r(q[1]), r(q[2])

# ----------------------------------------------------------------- 渠道错杀率
CH = ["代理渠道", "直销渠道", "线上渠道"]
kill_by_ch = []
for i, nm in enumerate(CH):
    m = (rej.channel == i).values
    kill = float((rej._true_premium.values[m] <= GOOD).mean())
    kill_by_ch.append(dict(channel=nm, n=int(m.sum()),
                           n_good=int((m & (rej._true_premium.values <= GOOD)).sum()),
                           kill_rate=r(kill * 100, 1)))
F["kill_by_channel"] = kill_by_ch
F["kill_ratio_online_vs_agent"] = r(
    kill_by_ch[2]["kill_rate"] / kill_by_ch[0]["kill_rate"], 1)

# ----------------------------------------------------------------- 模型表现
pa = sc["模型A_预测纯保费"].values
pb = sc["模型B_预测纯保费"].values
t = rej._true_premium.values
good = t <= GOOD


def auc(y, s):
    o = np.argsort(s)
    rk = np.empty(len(s), float)
    ss = s[o]
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        rk[o[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    n1 = float(y.sum())
    n0 = float(len(y) - n1)
    return (rk[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


F["auc_A"] = r(auc(good, -pa), 3)
F["auc_B"] = r(auc(good, -pb), 3)

# 圈最低 20% 的纯度
for k, p in [("A", pa), ("B", pb)]:
    idx = np.argsort(p)[:int(len(p) * 0.2)]
    F["purity20_" + k] = r(good[idx].mean() * 100, 1)
    F["mean20_" + k] = r(t[idx].mean())
F["purity20_base"] = r(good.mean() * 100, 1)

# 校准：预测/真实
F["calib_A"] = r(pa.mean() / t.mean(), 3)
F["calib_B"] = r(pb.mean() / t.mean(), 3)
F["pred_mean_A"] = r(pa.mean())
F["pred_mean_B"] = r(pb.mean())

# 各档真实均值（排序质量对照）
cuts = [(0, .1), (.1, .2), (.2, .4), (.4, .7), (.7, 1.0)]
band_true = {}
for k, p in [("A", pa), ("B", pb)]:
    idx = np.argsort(p)
    band_true[k] = [r(t[idx[int(len(t) * lo):int(len(t) * hi)]].mean())
                    for lo, hi in cuts]
F["band_true"] = band_true

# ----------------------------------------------------------------- 阈值倒 U
th = pd.read_csv(os.path.join(OUT, "threshold_A.csv"))
peak = th.loc[th.gain.idxmax()]
F["thr_curve"] = [dict(q=r(row.q * 100, 0), n=int(row.n),
                       thr=r(row.thr), true_mean=r(row.true_mean),
                       gain=r(row.gain))
                  for _, row in th.iterrows()]
F["thr_peak_n"] = int(peak.n)
F["thr_peak_gain"] = r(peak.gain)
F["thr_peak_true_mean"] = r(peak.true_mean)

# ----------------------------------------------------------------- 分档
bd = pd.read_csv(os.path.join(OUT, "bands_A.csv"))
F["bands"] = [dict(lo=r(row.lo * 100, 0), hi=r(row.hi * 100, 0), n=int(row.n),
                   true_mean=r(row.true_mean), good_rate=r(row.good_rate * 100, 1),
                   margin=r(row.margin_each))
              for _, row in bd.iterrows()]

# ----------------------------------------------------------------- 分渠道召回
bc = pd.read_csv(os.path.join(OUT, "by_channel_A.csv"))
F["by_channel"] = [dict(channel=row.channel, n=int(row.n), n_good=int(row.n_good),
                        n_flag=int(row.n_flag), recall=r(row.recall * 100, 1),
                        precision=r(row.precision * 100, 1))
                   for _, row in bc.iterrows()]

# ----------------------------------------------------------------- 偏差四法
bs = pd.read_csv(os.path.join(OUT, "bias_A.csv"))
F["bias"] = [dict(method=row.method, est=r(row.est, 1), bias=r(row.bias, 1),
                  rel=r(row.rel_bias * 100, 1)) for _, row in bs.iterrows()]
F["bias_true"] = r(rej._true_premium.mean(), 1)

# ----------------------------------------------------------------- 外推风险
far = sc["是否远点"].astype(str).values
F["n_far"] = int(sum(1 for v in far if v.startswith("远点")))
pr = sc["复核优先级"].values
F["prio"] = {}
for v in sorted(set(pr)):
    F["prio"][str(v)] = int((pr == v).sum())

# 清单前 5 条：必须按预测升序取，对齐后 sc 已回到 drivers.csv 的原始顺序
# 注意「风险分位」列本身已经是百分数（0-100），不要再乘 100
top5 = sc.sort_values("模型A_预测纯保费").head(5)
F["top5"] = [dict(id=int(row["driver_id"]), car=str(row["车型"]),
                  ch=str(row["渠道"]), pred=r(row["模型A_预测纯保费"]),
                  pct=r(row["风险分位"], 1))
             for _, row in top5.iterrows()]

# ----------------------------------------------------------------- 外推域分域指标
# 关键教学点：内插域（承保测试集）的表现 ≠ 外推域（拒保人群）的表现。
# 纯度从 96.6% 掉到 77.6%，这个落差就是「外推风险」的量化证据。
far_mask = np.array([v.startswith("远点") for v in sc["是否远点"].astype(str).values])
# ★ 注意：导出的清单里只有【模型A】的外推距离，
#   所以近/远点分域只能对 A 做。B 用的是 13 维空间（含渠道两个维度），
#   它的距离数值与 A 不可直接比大小 —— 强行套 A 的掩码会得出假的近远点。
#   这里对 B 只报告全体指标。诚实优先于对称。
ext = {}
for k, p in [("A", pa), ("B", pb)]:
    d = {}
    d["auc_all"] = r(auc(good, -p), 3)
    d["pred_mean"] = r(p.mean())
    d["calib"] = r(p.mean() / t.mean(), 3)
    idx = np.argsort(p)[:int(len(p) * 0.2)]
    d["purity20_all"] = r(good[idx].mean() * 100, 1)
    if k == "A":
        d["auc_near"] = r(auc(good[~far_mask], -p[~far_mask]), 3)
        d["auc_far"] = r(auc(good[far_mask], -p[far_mask]), 3)
        d["n_near"] = int((~far_mask).sum())
        d["n_far"] = int(far_mask.sum())
        d["purity20_near"] = r(good[idx][~far_mask[idx]].mean() * 100, 1)
    ext[k] = d
F["extrap"] = ext
F["purity_drop"] = r(F["extrap"]["A"]["purity20_near"] - 96.6, 1)

# ----------------------------------------------------------------- 内插域（从日志解析）
# 为什么不重算：重算需要重跑训练，成本高。日志是流水线产物，也算信源。
# 解析失败会直接抛错 —— 这样如果流水线改了输出格式，这里会立刻报警，
# 而不是让页面继续引用一个已经腐烂的数字。
LOG = os.path.join(OUT, "run_log.txt")
with open(LOG, encoding="utf-8") as f:
    log = f.read()

interp = {}
for tag, key in [("模型A（不含渠道）", "A"), ("模型B（含渠道）", "B")]:
    m = re.search(re.escape(tag) + r"\s*·\s*最终选定：.*?AUC\s*=\s*([\d.]+)"
                  r".*?真正好司机\s*=\s*([\d.]+)%", log, re.S)
    if not m:
        raise RuntimeError(f"日志里找不到 {tag} 的最终指标，格式可能已变")
    interp[key] = dict(auc=r(float(m.group(1)), 3), purity=r(float(m.group(2)), 1))
F["interp"] = interp

# 组合对照表（内插域）
combos = []
m = re.search(r"组合\s+AUC\s+圈最低20%纯度\s+均值偏差\s*\n"
              r"(.*?)\n\s*常数基线", log, re.S)
for line in m.group(1).strip().split("\n"):
    mm = re.match(r"\s*([①②③][^\d]+?)\s{2,}([\d.]+)\s+([\d.]+)%\s+([-\d.]+)%\s*$",
                  line)
    if mm:
        combos.append(dict(name=mm.group(1).strip(), auc=r(float(mm.group(2)), 3),
                           purity=r(float(mm.group(3)), 1),
                           dev=r(float(mm.group(4)), 1)))
m2 = re.search(r"常数基线\s+([\d.]+)\s+([\d.]+)%\s+([-\d.]+)%", log)
combos.append(dict(name="常数基线", auc=r(float(m2.group(1)), 3),
                   purity=r(float(m2.group(2)), 1), dev=r(float(m2.group(3)), 1)))
F["combos"] = combos

# 训练/测试衰减（过拟合诊断）
ov = []
m = re.search(r"组合\s+训练 AUC\s+测试 AUC\s+衰减\s*\n(.*?)\n\s*衰减远大于", log, re.S)
for line in m.group(1).strip().split("\n"):
    mm = re.match(r"\s*([①②③][^\d]+?)\s{2,}([\d.]+)\s+([\d.]+)\s+([-\d.]+)%\s*$",
                  line)
    if mm:
        ov.append(dict(name=mm.group(1).strip(), train=r(float(mm.group(2)), 3),
                       test=r(float(mm.group(3)), 3), decay=r(float(mm.group(4)), 1)))
F["overfit"] = ov
if len(combos) < 4 or len(ov) < 3:
    raise RuntimeError(f"组合表解析不全：combos={len(combos)} overfit={len(ov)}")

# 直接对纯保费建模的「撞墙」对照
m = re.search(r"模型\s+测试集 deviance\s+vs 常数基线\s*\n(.*?)\n\s*>>>", log, re.S)
wall = []
for line in m.group(1).strip().split("\n"):
    mm = re.match(r"\s*(.+?)\s+([\d.]+)\s+([\d.]+)%", line)
    if mm:
        wall.append(dict(name=mm.group(1).strip(), dev=r(float(mm.group(2)), 1),
                         pct=r(float(mm.group(3)), 1)))
F["dev_wall"] = wall

# 承保测试集规模
m = re.search(r"训练集\s*([\d,]+)\s*件\s*/\s*测试集\s*([\d,]+)\s*件", log)
F["n_train"] = int(m.group(1).replace(",", ""))
F["n_test"] = int(m.group(2).replace(",", ""))

# ----------------------------------------------------------------- 承保率体检
cov = {}
for col, names in [("car_type", ["经济型轿车", "SUV", "新能源车", "性能车"]),
                   ("region", ["东部", "北部", "南部", "西部", "中部"]),
                   ("use_type", ["家用", "营运"]),
                   ("channel", ["代理", "直销", "线上"])]:
    cov[col] = []
    for i, nm in enumerate(names):
        m = (df[col] == i).values
        a = int((m & (df.accept == 1).values).sum())
        cov[col].append(dict(name=nm, n=int(m.sum()), acc=a,
                             rate=r(a / max(int(m.sum()), 1) * 100, 1)))
F["coverage"] = cov

# ----------------------------------------------------------------- 写出
with open(os.path.join(OUT, "facts.json"), "w", encoding="utf-8") as f:
    json.dump(F, f, ensure_ascii=False, indent=1)

# ----------------------------------------------------------------- 摘要
print("=" * 70)
print("事实表已写出：out/facts.json")
print("=" * 70)
print(f"规模      总 {F['n_total']:,} / 承保 {F['n_acc']:,} ({F['pct_acc']}%) "
      f"/ 拒保 {F['n_rej']:,} ({F['pct_rej']}%) / 审计 {F['n_aud']} ({F['pct_aud']}%)")
print(f"真值      承保 {F['true_prem_acc']} 元 / 拒保 {F['true_prem_rej']} 元 "
      f"/ 好司机线 {F['good_threshold']} 元")
print(f"错杀      {F['n_wrongly_killed']:,} 件 = 拒保的 {F['pct_killed_of_rej']}% "
      f"= 全部的 {F['pct_killed_of_all']}%")
print("渠道错杀  " + " / ".join(f"{d['channel']} {d['kill_rate']}%"
                                for d in F["kill_by_channel"])
      + f"  → 线上是代理的 {F['kill_ratio_online_vs_agent']} 倍")
print(f"训练集    {F['n_train']:,} 件 / 测试集 {F['n_test']:,} 件")
print("内插域（承保测试集，模型熟悉的那些人）：")
for k in ["A", "B"]:
    d = F["interp"][k]
    print(f"          模型{k}  AUC {d['auc']}   圈最低20%纯度 {d['purity']}%")
print("外推域（拒保人群，模型没见过标签的那些人）：")
for k in ["A", "B"]:
    d = F["extrap"][k]
    extra = (f"  近点 {d['auc_near']} ({d['n_near']:,}件)  "
             f"远点 {d['auc_far']} ({d['n_far']:,}件)  "
             f"纯度 {d['purity20_all']}% / 近点 {d['purity20_near']}%"
             if k == "A" else f"  纯度 {d['purity20_all']}%  （不分域）")
    print(f"          模型{k}  AUC {d['auc_all']}  预测均值 {d['pred_mean']} "
          f"校准 {d['calib']}{extra}")
print(f"          >>> 纯度落差 {F['purity_drop']:+.1f} 个百分点 —— "
      f"这就是外推风险的价签")
print("撞墙对照（直接对纯保费做 GLM）：")
for d in F["dev_wall"]:
    print(f"          {d['name']:<22} deviance {d['dev']:>10,.0f}  "
          f"是常数基线的 {d['pct']}%")
print(f"阈值峰值  圈 {F['thr_peak_n']:,} 件，增益 {F['thr_peak_gain']:,.0f} 元")
print(f"偏差修正  真值 {F['bias_true']} 元")
for d in F["bias"]:
    print(f"          {d['method']}  {d['est']:>8.1f}  偏差 {d['bias']:>+7.1f} "
          f"({d['rel']:+.1f}%)")
print(f"外推      远点 {F['n_far']:,} 件  优先级分布 {F['prio']}")
print("=" * 70)
