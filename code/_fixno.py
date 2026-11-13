# -*- coding: utf-8 -*-
"""把正文里残留的旧「第 NN 页」引用，统一改成 navmap 的新页序。

旧编号：段内编号 ch01=35 … ch13=47；新编号：连续页序 ch01=23 … ch13=35（差 12）
"""
import re, os
from navmap import NAV

NEW = {n[0]: n[2] for n in NAV if n[1]}

# 上一版用的是「段内编号」(ch01=35…ch13=47)，现在改回连续页序，统一减 12
OLD2NEW = {f"{n}": f"{n - 12}" for n in range(35, 48)}

LOG = []

# 1) 纯文本：按映射表换（此时还没有任何「正确的 35~47」，不会误伤）
BARE = re.compile(r'第\s?(\d\d)\s?页')

def fix_bare(m):
    new = OLD2NEW.get(m.group(1))
    if not new or new == m.group(1):
        return m.group(0)
    LOG.append((m.group(0), f"第 {new} 页"))
    return f"第 {new} 页"

# 2) 带链接的：页号一律以 href 指向的文件为准
LINK = re.compile(r'(<a href="(ch\d\d)\.html[^"]*">)(第 )?(\d\d)(?=[^<]*</a>)')

def fix_link(m):
    new = NEW.get(m.group(2))
    if not new or m.group(4) == new:
        return m.group(0)
    LOG.append((m.group(0), m.group(1) + (m.group(3) or "") + new))
    return m.group(1) + (m.group(3) or "") + new

root = os.path.dirname(os.path.abspath(__file__))
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".py") or fn.startswith("_fix") or fn == "navmap.py":
        continue
    p = os.path.join(root, fn)
    src = open(p, encoding="utf-8").read()
    out = LINK.sub(fix_link, BARE.sub(fix_bare, src))
    if out != src:
        open(p, "w", encoding="utf-8").write(out)
        print(f"[改] {fn}")

print(f"\n本轮 {len(LOG)} 处：")
for a, b in LOG:
    print(f"  {a}   ->   {b}")
