"""扫描站点内嵌 SVG：检查 rect 互相重叠 / 文字溢出 viewBox。"""
import re, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def est_w(s, fs):
    w = 0.0
    for ch in s:
        w += fs * (1.0 if ord(ch) > 0x2000 else 0.55)
    return w


def _split_g(body, dx=0.0, dy=0.0):
    """把 <g transform="translate(dx,dy)"> 里的元素坐标还原成绝对坐标。

    不这么做的话，同一段图元被复制四次（translate 不同），
    扫描器会看到四个「一模一样的 rect」互相重叠 —— 全是误报。
    """
    out = []
    for m in re.finditer(r'<g transform="translate\(([-\d.]+),\s*([-\d.]+)\)">(.*?)</g>',
                         body, re.S):
        inner = m.group(3)
        out.append(_shift(inner, dx + float(m.group(1)), dy + float(m.group(2))))
        out.append(_split_g(re.sub(r'<g transform="translate[^>]*>.*?</g>', "", inner, flags=re.S),
                            dx, dy))
    return "\n".join(out)


def _shift(s, dx, dy):
    def mv(m):
        return f'{m.group(1)}="{float(m.group(2)) + dx:.1f}"'
    def mvy(m):
        return f'{m.group(1)}="{float(m.group(2)) + dy:.1f}"'
    s = re.sub(r'(x)="([-\d.]+)"', lambda m: mv(m), s)
    s = re.sub(r'(y)="([-\d.]+)"', lambda m: mvy(m), s)
    return s


for fp in sorted(glob.glob(os.path.join(BASE, "*.html"))):
    src = open(fp, encoding="utf-8").read()
    for m in re.finditer(r'<svg viewBox="0 0 ([\d.]+) ([\d.]+)"(.*?)</svg>', src, re.S):
        W, H, body = float(m.group(1)), float(m.group(2)), m.group(3)
        name = os.path.basename(fp)
        # 有 <g transform> 的：只扫还原后的绝对坐标，避免重复计数
        body += _split_g(body)
        body = re.sub(r'<g transform="translate[^>]*>.*?</g>', "", body, flags=re.S)
        rects = []
        for r in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', body):
            x, y, w, h = tuple(map(float, r.groups()))
            # 铺满整块画布的是背景板，它「包住」所有元素属于设计，不是缺陷
            if x <= 0 and y <= 0 and w >= W - 1 and h >= H - 1:
                continue
            rects.append((x, y, w, h))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                ax, ay, aw, ah = rects[i]
                bx, by, bw, bh = rects[j]
                ox = min(ax + aw, bx + bw) - max(ax, bx)
                oy = min(ay + ah, by + bh) - max(ay, by)
                if ox > 1 and oy > 1:
                    print(f"[OVERLAP] {name} rect{rects[i]} vs {rects[j]}  ({ox:.0f}x{oy:.0f})")
        for t in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)"([^>]*)>(.*?)</text>', body):
            x, y, fs, attr, s = float(t.group(1)), float(t.group(2)), float(t.group(3)), t.group(4), t.group(5)
            s = re.sub(r"<[^>]+>", "", s)
            w = est_w(s, fs)
            anchor = "middle" if "middle" in attr else ("end" if '"end"' in attr else "start")
            x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
            x1 = x0 + w
            if x0 < -2 or x1 > W + 2 or y > H + 2:
                print(f"[OUT] {name} text<{s}> x={x} fs={fs} span=[{x0:.0f},{x1:.0f}] W={W:.0f} H={H:.0f}")
print("scan done")
