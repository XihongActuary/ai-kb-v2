# -*- coding: utf-8 -*-
"""
场景一 · 关键图绘制
所有图都由真实数据生成，不用示意图。
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
os.makedirs(IMG, exist_ok=True)

# ---------------- 品牌配色（水墨五色）----------------
PAPER = "#f5f1e6"
INK = "#2b2a26"
CINNABAR = "#b53d2e"
AMBER = "#bb8a1f"
JADE = "#2f6b5a"
GREY = "#8a8578"
LIGHT = "#d9d3c2"

# ---------------- 中文字体 ----------------
FP = "C:/Windows/Fonts/msyh.ttc"
FS = "C:/Windows/Fonts/msyhbd.ttc"
for p in (FP, FS):
    try:
        font_manager.fontManager.addfont(p)
    except Exception:
        pass
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(os.path.join(DATA, "drivers.csv"))


def bg(ax):
    """宣纸底 + 去掉边框"""
    ax.set_facecolor(PAPER)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=INK, labelsize=11, length=0)


# ==================================================================
# 图1：选择偏差漏斗 —— 问题的根源
# ==================================================================
def fig1_funnel():
    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=150)
    fig.patch.set_facecolor(PAPER)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    acc = (df.accept == 1).sum()
    rej = (df.accept == 0).sum()
    med = df[df.accept == 1]._true_premium.median()
    wk = ((df.accept == 0) & (df._true_premium <= med)).sum()

    def box(x, y, w, h, fc, ec, title, n, note, tc="white"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    fc=fc, ec=ec, lw=1.6))
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
                fontsize=15, color=tc, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.30, n, ha="center", va="center",
                fontsize=21, color=tc, fontweight="bold")
        if note:
            ax.text(x + w / 2, y - 0.42, note, ha="center", va="top",
                    fontsize=10.5, color=INK, alpha=.75)

    # 顶层：全体
    box(0.6, 7.6, 8.8, 1.5, "none", INK, "全部投保申请", f"{len(df):,} 人",
        "每个人都有真实风险，但只有一个「真值」", INK)
    ax.add_patch(FancyArrowPatch((5, 7.55), (5, 7.05), arrowstyle="-|>",
                                 mutation_scale=22, color=INK, lw=1.6))

    # 中层：两个分支
    box(0.5, 4.6, 4.3, 2.1, JADE, JADE, "已承保", f"{acc:,} 人", None)
    box(5.2, 4.6, 4.3, 2.1, CINNABAR, CINNABAR, "被拒保", f"{rej:,} 人", None)
    ax.text(0.5, 4.22, "有出险记录 → 能训练模型", ha="left", va="center",
            fontsize=11, color="white", alpha=.92)
    ax.text(5.2, 4.22, "无出险记录 → 模型从未见过", ha="left", va="center",
            fontsize=11, color="white", alpha=.92)
    ax.text(0.5, 3.55, "标签可见", ha="left", fontsize=10.5, color=JADE,
            alpha=.85, fontweight="bold")
    ax.text(5.2, 3.55, "标签不可见", ha="left", fontsize=10.5, color=CINNABAR,
            alpha=.85, fontweight="bold")

    # 错杀分块：独立放在右侧下方，虚线表示「从拒保群中筛出」
    ax.add_patch(FancyArrowPatch((7.35, 4.55), (7.35, 3.15), arrowstyle="-|>",
                                 mutation_scale=18, color=CINNABAR, lw=1.5,
                                 ls="--", alpha=.7))
    box(5.2, 1.5, 4.3, 1.6, "#f3e2de", CINNABAR, "其中被错杀", f"{wk:,} 人",
        "真实风险低于承保人群的中位数", CINNABAR)

    ax.text(5, 0.42, "模型只学会了「当年被放行的人如何出险」，\n"
                     "却要回答「当年被拒的人会不会出险」",
            ha="center", va="center", fontsize=13, color=CINNABAR,
            fontweight="bold", linespacing=1.7)

    ax.text(5, 9.55, "图1  问题的根源：你只能看见被你放行过的人",
            ha="center", fontsize=17, color=INK, fontweight="bold")

    p = os.path.join(IMG, "fig1_01_funnel.png")
    plt.savefig(p, facecolor=PAPER, bbox_inches="tight")
    plt.close()
    print("saved", p)


# ==================================================================
# 图2：渠道偏见 —— 谁被错杀得最多
# ==================================================================
def fig2_channel():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.8), dpi=150)
    fig.patch.set_facecolor(PAPER)
    fig.suptitle("图2  偏见长什么样：同样一张保单，线上渠道被拒得更多、更冤",
                 fontsize=16, color=INK, fontweight="bold", y=0.98)

    names = ["代理渠道", "直销渠道", "线上渠道"]
    colors = [JADE, AMBER, CINNABAR]

    # 左：错杀率
    ax = axes[0]
    bg(ax)
    rej = df[df.accept == 0]
    med = df[df.accept == 1]._true_premium.median()
    rates = [len(rej[(rej.channel_nm == n) & (rej._true_premium <= med)]) /
             len(rej[rej.channel_nm == n]) for n in names]
    bars = ax.bar(names, rates, color=colors, width=.55, zorder=3)
    for b, r in zip(bars, rates):
        ax.text(b.get_x() + b.get_width() / 2, r + .018, f"{r:.1%}",
                ha="center", fontsize=15, color=INK, fontweight="bold")
    ax.set_ylim(0, .56)
    ax.set_ylabel("被错杀率（真实纯保费低于承保中位数）", fontsize=11, color=INK)
    ax.set_title("错杀率：线上渠道是代理渠道的 2.1 倍", fontsize=13,
                 color=CINNABAR, fontweight="bold", pad=12)
    ax.grid(axis="y", color=LIGHT, lw=.8, zorder=0)
    # 对比标注
    ax.annotate("", xy=(2, rates[2]), xytext=(0, rates[0]),
                arrowprops=dict(arrowstyle="->", color=CINNABAR, lw=2,
                                connectionstyle="arc3,rad=-.25"))
    ax.text(1.0, max(rates) * .96, "2.1 倍", fontsize=13, color=CINNABAR,
            fontweight="bold")

    # 右：真实风险 vs 规则打分（相关性对比）
    ax2 = axes[1]
    bg(ax2)
    sub = df[df.accept == 0]
    ax2.scatter(sub.crude_score, sub._true_premium, s=9, alpha=.16,
                color=CINNABAR, edgecolors="none")
    on = sub[sub.channel_nm == "线上渠道"]
    ax2.scatter(on.crude_score, on._true_premium, s=9, alpha=.30,
                color=AMBER, edgecolors="none")
    # 真实风险趋势线
    xs = np.linspace(sub.crude_score.min(), sub.crude_score.max(), 50)
    coef = np.polyfit(sub.crude_score, np.log(sub._true_premium), 1)
    ax2.plot(xs, np.exp(np.polyval(coef, xs)), color=JADE, lw=2.4,
             label="真实风险（对数拟合）")
    ax2.set_xlabel("核保规则打分（越高越容易被拒）", fontsize=11, color=INK)
    ax2.set_ylabel("真实纯保费（元）", fontsize=11, color=INK)
    ax2.set_title("规则分能测出部分风险，但把「线上」当成了危险", fontsize=13,
                  color=INK, fontweight="bold", pad=12)
    ax2.legend(frameon=False, fontsize=11, loc="upper left")
    ax2.grid(color=LIGHT, lw=.8, zorder=0)
    ax2.text(0.97, 0.06, "点越靠右下 = 分数高但实际风险低 = 越可能被错杀",
             transform=ax2.transAxes, ha="right", fontsize=10, color=INK, alpha=.7)

    plt.tight_layout()
    p = os.path.join(IMG, "fig1_02_channel.png")
    plt.savefig(p, facecolor=PAPER, bbox_inches="tight")
    plt.close()
    print("saved", p)


# ==================================================================
# 图3：分布错位 —— 模型学不到的东西
# ==================================================================
def fig3_shift():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4), dpi=150)
    fig.patch.set_facecolor(PAPER)
    fig.suptitle("图3  被错杀的人长什么样：他们的风险分布与训练数据不重叠",
                 fontsize=16, color=INK, fontweight="bold", y=0.98)

    acc = df[df.accept == 1]
    rej = df[df.accept == 0]
    med = acc._true_premium.median()
    wk = rej[rej._true_premium <= med]

    # 左：真实纯保费分布
    ax = axes[0]
    bg(ax)
    bins = np.linspace(0, 2200, 60)
    ax.hist(acc._true_premium, bins=bins, alpha=.62, color=JADE,
            label=f"已承保（训练数据）{len(acc):,}", density=True)
    ax.hist(wk._true_premium, bins=bins, alpha=.62, color=CINNABAR,
            label=f"被错杀（模型没见过）{len(wk):,}", density=True)
    ax.axvline(med, color=INK, ls="--", lw=1.6)
    ax.text(med + 40, ax.get_ylim()[1] * .88, "承保人群中位数", fontsize=10.5, color=INK)
    ax.set_xlabel("真实纯保费（元）", fontsize=11, color=INK)
    ax.set_ylabel("概率密度", fontsize=11, color=INK)
    ax.legend(frameon=False, fontsize=10.5)
    ax.set_title("训练数据里没有这一块人", fontsize=13, color=CINNABAR,
                 fontweight="bold", pad=12)
    ax.grid(axis="y", color=LIGHT, lw=.8, zorder=0)

    # 右：年龄 × 里程 散点，看错杀者落在哪
    ax2 = axes[1]
    bg(ax2)
    ax2.scatter(acc.age, acc.mileage / 1000, s=8, alpha=.20, color=JADE,
                edgecolors="none", label="已承保")
    ax2.scatter(wk.age, wk.mileage / 1000, s=10, alpha=.34, color=CINNABAR,
                edgecolors="none", label="被错杀")
    ax2.set_xlabel("年龄", fontsize=11, color=INK)
    ax2.set_ylabel("年行驶里程（千公里）", fontsize=11, color=INK)
    ax2.set_title("错杀者多为年轻、低里程、经济车型", fontsize=13,
                  color=INK, fontweight="bold", pad=12)
    ax2.legend(frameon=False, fontsize=10.5)
    ax2.grid(color=LIGHT, lw=.8, zorder=0)
    ax2.text(0.97, 0.05, "低风险特征明显，却被规则拒之门外",
             transform=ax2.transAxes, ha="right", fontsize=10, color=CINNABAR)

    plt.tight_layout()
    p = os.path.join(IMG, "fig1_03_shift.png")
    plt.savefig(p, facecolor=PAPER, bbox_inches="tight")
    plt.close()
    print("saved", p)


if __name__ == "__main__":
    fig1_funnel()
    fig2_channel()
    fig3_shift()
