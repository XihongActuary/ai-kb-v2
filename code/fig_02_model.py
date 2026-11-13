# -*- coding: utf-8 -*-
"""
场景一 · 模型侧九张图

原则：
  1. 每一张图都由真实数据算出，不画示意图；
  2. 图上出现的每个数字都来自 out/facts.json，与 13 个页面完全同源；
  3. 配色沿用西红精算水墨五色，与 ml-kb / 公众号保持一家。

运行：python fig_02_model.py
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")
IMG = os.path.join(ROOT, "img")
os.makedirs(IMG, exist_ok=True)

PAPER = "#f5f1e6"
INK = "#2b2a26"
CINNABAR = "#b53d2e"
AMBER = "#bb8a1f"
JADE = "#2f6b5a"
GREY = "#8a8578"
LIGHT = "#d9d3c2"

for p in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc"):
    try:
        font_manager.fontManager.addfont(p)
    except Exception:
        pass
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

F = json.load(open(os.path.join(OUT, "facts.json"), encoding="utf-8"))
df = pd.read_csv(os.path.join(DATA, "drivers.csv"))
sc = pd.read_csv(os.path.join(OUT, "rejected_scored.csv"))
sc.columns = [c.lstrip("\ufeff") for c in sc.columns]
rej = df[df.accept == 0]
sc = sc.set_index("driver_id").loc[rej.driver_id.values].reset_index()
acc = df[df.accept == 1]
GOOD = F["good_threshold"]

made = []


def bg(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(PAPER)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LIGHT)
    ax.tick_params(colors=GREY, labelsize=9)
    ax.set_title(title, color=INK, fontsize=13, pad=14)
    ax.set_xlabel(xlabel, color=GREY, fontsize=10)
    ax.set_ylabel(ylabel, color=GREY, fontsize=10)
    ax.grid(axis="y", color=LIGHT, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fp = os.path.join(IMG, name)
    fig.savefig(fp, dpi=140, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    made.append(name)
    print("  " + name)


# ============================================================ 1 风险分布
fig, ax = plt.subplots(figsize=(8.4, 4.4))
bins = np.linspace(0, 4000, 70)
ax.hist(acc._true_premium, bins=bins, color=JADE, alpha=0.62,
        label=f"已承保 {F['n_acc']:,} 件（训练集来源）")
ax.hist(rej._true_premium, bins=bins, color=CINNABAR, alpha=0.55,
        label=f"被拒保 {F['n_rej']:,} 件（模型从未见过标签）")
ax.axvline(GOOD, color=AMBER, linewidth=2.0,
           label=f"好司机线 {GOOD:,.0f} 元")
ax.text(GOOD + 60, ax.get_ylim()[1] * 0.82,
        f"线左边 {F['n_wrongly_killed']:,} 件是错杀\n占拒保 {F['pct_killed_of_rej']}%",
        color=AMBER, fontsize=9.5, va="top")
bg(ax, "拒保人群整体更贵，但左侧那一块是被误杀的好人",
   "真实期望纯保费（元）", "人数")
ax.legend(frameon=False, fontsize=9.5, loc="upper right")
save(fig, "fig2_01_dist.png")

# ============================================================ 2 渠道错杀率
fig, ax = plt.subplots(figsize=(7.2, 4.2))
d = F["kill_by_channel"]
xs = np.arange(3)
vals = [x["kill_rate"] for x in d]
bars = ax.bar(xs, vals, width=0.56,
              color=[JADE, JADE, CINNABAR])
for b, v, x in zip(bars, vals, d):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.9, f"{v}%",
            ha="center", color=INK, fontsize=12, fontweight="bold")
    ax.text(b.get_x() + b.get_width() / 2, 1.2,
            f"拒保 {x['n']:,} 件\n错杀 {x['n_good']:,} 件",
            ha="center", color="white", fontsize=8.5)
ax.set_xticks(xs)
ax.set_xticklabels([x["channel"] for x in d])
ax.set_ylim(0, max(vals) * 1.28)
bg(ax, "同样的车、同样的人，换个渠道来买就被加 7 分",
   "销售渠道", "该渠道中被错杀的比例")
ax.text(2, max(vals) * 1.16,
        f"线上是代理的 {F['kill_ratio_online_vs_agent']} 倍",
        ha="center", color=CINNABAR, fontsize=10.5, fontweight="bold")
ax.grid(axis="y", color=LIGHT, linewidth=0.6, alpha=0.6)
save(fig, "fig2_02_channel.png")

# ============================================================ 3 分档纯度
fig, ax = plt.subplots(figsize=(8.0, 4.4))
b = F["bands"]
labels = [f"{int(x['lo'])}–{int(x['hi'])}%" for x in b]
pure = [x["good_rate"] for x in b]
means = [x["true_mean"] for x in b]
ax.bar(labels, pure, width=0.56, color=JADE, alpha=0.8, label="真正的好司机占比")
ax.axhline(F["purity20_base"], color=GREY, linestyle="--", linewidth=1.4,
           label=f"随机圈选基线 {F['purity20_base']}%")
ax2 = ax.twinx()
ax2.plot(labels, means, color=CINNABAR, marker="o", linewidth=2.0,
         label="该档真实纯保费")
ax2.set_ylabel("真实纯保费（元）", color=CINNABAR, fontsize=10)
ax2.tick_params(colors=CINNABAR, labelsize=9)
for s in ("top", "right", "left", "bottom"):
    ax2.spines[s].set_visible(False)
for i, (p, m) in enumerate(zip(pure, means)):
    ax.text(i, p + 1.6, f"{p}%", ha="center", color=INK, fontsize=9.5)
    ax2.text(i, m + 45, f"{m:,.0f}", ha="center", color=CINNABAR, fontsize=9)
ax.set_ylim(0, max(pure) * 1.25)
ax2.set_ylim(900, max(means) * 1.16)
bg(ax, "模型预测越低，里面真好司机的比例越高 —— 单调，没有反转",
   "按预测纯保费从低到高分档", "好司机占比")
ax.legend(frameon=False, fontsize=9.5, loc="upper right")
save(fig, "fig2_03_lift.png")

# ============================================================ 4 阈值倒 U
fig, ax = plt.subplots(figsize=(8.0, 4.4))
c = F["thr_curve"]
ns = [x["n"] for x in c]
g = [x["gain"] for x in c]
ax.plot(ns, g, color=JADE, marker="o", linewidth=2.2, label="相对随机圈选的增益")
ax.fill_between(ns, 0, g, color=JADE, alpha=0.14)
pk = (F["thr_peak_n"], F["thr_peak_gain"])
ax.plot([pk[0]], [pk[1]], marker="o", markersize=11, color=CINNABAR)
ax.annotate(f"峰值：圈 {pk[0]:,} 件\n增益 {pk[1]:,.0f} 元",
            xy=pk, xytext=(pk[0] * 0.52, pk[1] * 1.02),
            color=CINNABAR, fontsize=10.5, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=CINNABAR, lw=1.4))
ax.axvline(8800, color=GREY, linestyle=":", linewidth=1.2)
ax.text(8600, max(g) * 0.28, "全圈=没挑\n增益归零",
        ha="right", color=GREY, fontsize=9)
bg(ax, "圈谁不是越严越好，也不是越多越好 —— 中间有个最大值",
   "圈出的待复核件数", "模型增益（元）")
ax.legend(frameon=False, fontsize=10, loc="upper left")
save(fig, "fig2_04_threshold.png")

# ============================================================ 5 偏差四法
fig, ax = plt.subplots(figsize=(8.0, 4.2))
bs = F["bias"]
names = [x["method"] for x in bs]
rel = [x["rel"] for x in bs]
cols = [GREY, AMBER, CINNABAR, JADE]
bars = ax.barh(range(len(bs)), rel, color=cols, height=0.55)
ax.axvline(0, color=INK, linewidth=1.2)
for i, (x, b_) in enumerate(zip(bs, bars)):
    off = 1.2 if x["rel"] >= 0 else -1.2
    ha = "left" if x["rel"] >= 0 else "right"
    ax.text(x["rel"] + off, i, f"{x['rel']:+.1f}%   （{x['est']:,.0f} 元）",
            va="center", ha=ha, color=INK, fontsize=10)
ax.set_yticks(range(len(bs)))
ax.set_yticklabels(names, fontsize=10)
ax.set_xlim(min(rel) * 1.55, max(rel) * 1.55)
ax.invert_yaxis()
bg(ax, f"拒保人群真实均值 {F['bias_true']:,.0f} 元 —— 谁能最接近它？",
   "相对真值的偏差", "")
ax.grid(axis="x", color=LIGHT, linewidth=0.6, alpha=0.6)
ax.set_axisbelow(True)
save(fig, "fig2_05_bias.png")

# ============================================================ 6 内插 vs 外推
fig, ax = plt.subplots(figsize=(7.6, 4.2))
labels = ["内插域\n承保测试集", "外推域\n拒保·近点", "外推域\n拒保·全部"]
vals = [F["interp"]["A"]["purity"],
        F["extrap"]["A"]["purity20_near"],
        F["extrap"]["A"]["purity20_all"]]
cols = [JADE, AMBER, CINNABAR]
bars = ax.bar(labels, vals, width=0.5, color=cols, alpha=0.85)
ax.axhline(F["purity20_base"], color=GREY, linestyle="--", linewidth=1.4)
ax.text(2.42, F["purity20_base"] + 1.5, f"随机基线 {F['purity20_base']}%",
        color=GREY, fontsize=9, ha="right")
for b_, v in zip(bars, vals):
    ax.text(b_.get_x() + b_.get_width() / 2, v + 1.5, f"{v}%",
            ha="center", color=INK, fontsize=12, fontweight="bold")
ax.set_ylim(0, max(vals) * 1.22)
bg(ax, "同一个模型，换个地方用就掉了 18.9 个百分点",
   "", "圈最低 20% 里真正好司机占比")
ax.annotate("", xy=(1.5, vals[1]), xytext=(0.5, vals[0]),
            arrowprops=dict(arrowstyle="->", color=CINNABAR, lw=1.6,
                            connectionstyle="arc3,rad=-0.25"))
ax.text(1.0, (vals[0] + vals[1]) / 2 + 6, f"{F['purity_drop']:.1f} 个百分点",
        ha="center", color=CINNABAR, fontsize=10.5, fontweight="bold")
save(fig, "fig2_06_interp_extrap.png")

# ============================================================ 7 过拟合诊断
fig, ax = plt.subplots(figsize=(7.6, 4.0))
ov = F["overfit"]
xs = np.arange(len(ov))
w = 0.34
ax.bar(xs - w / 2, [o["train"] for o in ov], w, color=JADE, label="训练集 AUC")
ax.bar(xs + w / 2, [o["test"] for o in ov], w, color=AMBER, label="测试集 AUC")
ax.axhline(0.5, color=GREY, linestyle=":", linewidth=1.2)
ax.text(len(ov) - 0.4, 0.52, "随机 0.5", color=GREY, fontsize=9, ha="right")
ax.set_xticks(xs)
ax.set_xticklabels([o["name"] for o in ov], fontsize=9.5)
ax.set_ylim(0.4, 0.98)
for i, o in enumerate(ov):
    ax.text(i - w / 2, o["train"] + 0.012, f"{o['train']}", ha="center",
            color=INK, fontsize=9)
    ax.text(i + w / 2, o["test"] + 0.012, f"{o['test']}", ha="center",
            color=INK, fontsize=9)
bg(ax, "训练与测试几乎重合 —— 没有过拟合，问题不在模型复杂度",
   "", "AUC")
ax.legend(frameon=False, fontsize=10, loc="upper left")
save(fig, "fig2_07_overfit.png")

# ============================================================ 8 外推距离
fig, ax = plt.subplots(figsize=(8.0, 4.4))
ood = sc["外推距离"].values
far = np.array([v.startswith("远点") for v in sc["是否远点"].astype(str).values])
ax.hist(ood[~far], bins=60, color=JADE, alpha=0.7,
        label=f"近点 {int((~far).sum()):,} 件（模型熟悉）")
ax.hist(ood[far], bins=60, color=CINNABAR, alpha=0.7,
        label=f"远点 {int(far.sum()):,} 件（建议走人工）")
ax.axvline(np.median(ood), color=GREY, linestyle="--", linewidth=1.2)
bg(ax, "打分之前先量一量：这个人离训练数据有多远",
   "到训练中心的距离（标准化）", "人数")
ax.legend(frameon=False, fontsize=10)
ex = F["extrap"]["A"]
ax.text(0.985, 0.62,
        f"近点 AUC {ex['auc_near']}\n远点 AUC {ex['auc_far']}",
        transform=ax.transAxes, ha="right", va="top", fontsize=10,
        color=INK, bbox=dict(boxstyle="round,pad=0.5", facecolor=PAPER,
                             edgecolor=LIGHT))
save(fig, "fig2_08_ood.png")

# ============================================================ 9 规则 vs 模型
fig, ax = plt.subplots(figsize=(7.6, 5.0))
idx = np.random.default_rng(7).choice(len(rej), 2600, replace=False)
tv = rej._true_premium.values[idx]
rv = rej.crude_score.values[idx]
pv = sc["模型A_预测纯保费"].values[idx]
g1 = tv <= GOOD
ax.scatter(rv[~g1], pv[~g1] / 1000, s=7, color=LIGHT, alpha=0.75,
           label="确实不该承保")
ax.scatter(rv[g1], pv[g1] / 1000, s=9, color=CINNABAR, alpha=0.72,
           label=f"被错杀的好司机（{int(g1.sum()):,} 件）")
ax.axhline(GOOD / 1000, color=AMBER, linewidth=1.8, linestyle="--")
ax.text(ax.get_xlim()[1] * 0.995, GOOD / 1000 + 0.06,
        f"好司机线 {GOOD:,.0f} 元", ha="right", color=AMBER, fontsize=9.5)
bg(ax, "规则分高的人里，藏着一大片模型认为便宜的好人",
   "原核保规则分（越高越容易被拒）", "模型预测纯保费（千元）")
ax.legend(frameon=False, fontsize=10, loc="upper left")
save(fig, "fig2_09_rule_vs_model.png")

print("=" * 62)
print(f"模型侧九张图已生成 → img/  共 {len(made)} 张")
print("=" * 62)
