# -*- coding: utf-8 -*-
"""
AI 实践库 · 站点自检

检查七类问题：
  1. HTML 标签闭合（div/table/tr/td/h*/p/a/span/aside/main）
  2. 内部链接与图片、iframe 引用的文件真实存在
  3. 页内锚点与 id 对得上
  4. 必须有 viewport meta（公众号时代踩过的坑：移动端截断）
  5. 残留乱码（U+FFFD）
  6. 关键数字与 out/facts.json 一致（数字腐烂报警）
  7. 动画页自包含（不引用外部 http 资源）

用法：python _check.py   → 全绿输出 0 failures，否则列出问题
"""
import os
import re
import io
import json
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = json.load(open(os.path.join(ROOT, "out", "facts.json"), encoding="utf-8"))

fails = []
notes = []


class Checker(HTMLParser):
    VOID = {"meta", "link", "img", "br", "hr", "input", "source", "wbr"}
    def __init__(self):
        super().__init__()
        self.stack = []
        self.ids = set()
        self.hrefs = []
        self.srcs = []
        self.has_viewport = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and d.get("href", "").startswith("#"):
            self.hrefs.append(d["href"][1:])
        if tag in ("img", "iframe") and d.get("src"):
            self.srcs.append(d["src"])
        if tag == "meta" and d.get("name") == "viewport":
            self.has_viewport = True
        if tag not in self.VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack:
            fails.append(f"多余的 </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    t = self.stack.pop()
                    fails.append(f"未闭合 <{t}>")
                if self.stack:
                    self.stack.pop()
            else:
                fails.append(f"未 opened 的 </{tag}>")


PAGES = sorted(f for f in os.listdir(ROOT)
               if f.endswith(".html") and not f.startswith("anim_"))
ANIMS = sorted(f for f in os.listdir(ROOT) if f.startswith("anim_"))
print(f"页面 {len(PAGES)} 个：{', '.join(PAGES)}")
print(f"动画 {len(ANIMS)} 个：{', '.join(ANIMS)}")
print("=" * 66)

for fn in PAGES:
    txt = io.open(os.path.join(ROOT, fn), encoding="utf-8").read()
    c = Checker()
    c.feed(txt)
    for t in c.stack:
        fails.append(f"{fn}: 未闭合 <{t}>")
    if not c.has_viewport:
        fails.append(f"{fn}: 缺 viewport meta")
    if "\ufffd" in txt:
        fails.append(f"{fn}: 残留乱码 U+FFFD")
    for h in c.hrefs:
        if h and h not in c.ids:
            fails.append(f"{fn}: 页内锚点 #{h} 无对应 id")
    for s in c.srcs:
        if s.startswith("http"):
            fails.append(f"{fn}: 引用了外部资源 {s}")
            continue
        if not os.path.exists(os.path.join(ROOT, s)):
            fails.append(f"{fn}: 引用不存在 {s}")
    # 关键数字一致性抽查（每页都要出现的核心事实）
    for label, needle in [
        ("错杀数", f"{F['n_wrongly_killed']:,}"),
        ("拒保件数", f"{F['n_rej']:,}"),
        ("好司机线", f"{F['good_threshold']:,.0f} 元"),
    ]:
        if fn not in ("index",) and needle not in txt.replace("&nbsp;", " "):
            notes.append(f"{fn}: 未出现{label}「{needle}」（如非相关页可忽略）")

# 动画自包含
for fn in ANIMS:
    txt = io.open(os.path.join(ROOT, fn), encoding="utf-8").read()
    if re.search(r'(src|href)\s*=\s*["\']https?:', txt):
        fails.append(f"{fn}: 动画引用了外部资源，不满足自包含")
    if "\ufffd" in txt:
        fails.append(f"{fn}: 残留乱码")

# facts 与页面交叉验证（核心数字必须至少出现在某一页）
alltxt = "".join(io.open(os.path.join(ROOT, f), encoding="utf-8").read()
                 for f in PAGES)
for label, needle in [
    ("AUC_A 内插", f"{F['interp']['A']['auc']}"),
    ("纯度 内插A", f"{F['interp']['A']['purity']}%"),
    ("纯度 外推全体", f"{F['extrap']['A']['purity20_all']}%"),
    ("纯度 外推近点", f"{F['extrap']['A']['purity20_near']}%"),
    ("线上错杀率", f"{F['kill_by_channel'][2]['kill_rate']}%"),
    ("DR 估计", f"{F['bias'][3]['est']:,.1f}"),
    ("阈值峰值增益", f"{F['thr_peak_gain']:,.0f}"),
    ("渠道错杀倍数", str(F['kill_ratio_online_vs_agent'])),
]:
    if needle not in alltxt:
        fails.append(f"全部页面都找不到核心数字「{needle}」（{label}）——数字腐烂？")

print()
for n in notes:
    print("  [提示]", n)
print()
print("=" * 66)
if fails:
    print(f"发现 {len(fails)} 个问题：")
    for f_ in fails:
        print("  [FAIL]", f_)
else:
    print("检查全部通过：0 failures")
print("=" * 66)
