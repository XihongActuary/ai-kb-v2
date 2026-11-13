# -*- coding: utf-8 -*-
"""把 code/*.py 生成可独立打开的源码浏览页 src/<name>.html。

为什么单独做这一步：
  B10「端到端七步」里每一步都要指向真实代码。给一个裸 .py 链接，
  读者要么下载、要么在浏览器里看到一大坨没行号的文本，等于没给。
  生成带行号锚点的页面后，链接可以精确到「第 120–168 行」，
  点开是新窗口、直接落在那段代码上。

两个对外接口：
  build_all(ROOT)            构建时调用，产出 src/*.html
  span(ROOT, file, a, b)     定位「第几行到第几行」，行号现算，不写死

除 code/*.py 之外，三个动画 anim_*.html 里的 <script> 也进 src/：
  动画是纯前端算法，讲「这段数学怎么写出来」时，链到动画自己的源码
  比链到 Python 更贴题；行号同样现算。
"""

import os
import re
import io

CODE_DIR = "code"
OUT_DIR = "src"

# 三个动画：文件名 → 一句话说明（写进源码页顶部）
ANIM = {
    "anim_glm": "Poisson GLM 的 IRLS 迭代",
    "anim_tree": "决策树怎么挑分裂点",
    "anim_gbdt": "GBDT 逐轮补残差",
}

KW = ("def class return if elif else for while in not and or import from as "
      "with try except finally raise lambda None True False assert yield "
      "global pass break continue is del self print").split()

JS_KW = ("var let const function return if else for while do break continue new "
         "typeof null true false this switch case default throw try catch finally "
         "delete instanceof void with Math document").split()

SKIP = ("_build", "_check", "_scan_svg")   # 脚手架，不作为「项目代码」展示

# 收集范围从 .py 扩到 .js：两个动画脚本（复算数字 / 无头自检）也是案例代码，
# 之前只收 .py，它们在「代码入口」页里就没有可点的源码页。
# 名单写死而非靠后缀判断：生成器内部一律用「不带扩展名」的名字，
# 否则 build_all 里 f[:-3] 剥掉 .js 之后再判断后缀就永远为假。
JS_FILES = {"_animfacts", "test_anim"}


def _is_js(fname):
    return fname in ANIM or fname in JS_FILES


def _path_of(root, fname):
    """源码路径：动画走 _anim_text，js 用同名 .js，其余按 python 模块补全。"""
    if fname in ANIM:
        return None
    ext = ".js" if fname in JS_FILES else ".py"
    return os.path.join(root, CODE_DIR, fname + ext)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hl(line, state, js=False):
    """极简高亮：注释 / 字符串 / 关键字 / 数字 / 函数名。
    state 用于跨行跟踪三引号字符串；js=True 时按 JS 的 // 注释与关键字走。"""
    out = []
    i, n = 0, len(line)
    kw = JS_KW if js else KW

    if state["doc"]:
        end = line.find(state["doc"])
        if end < 0:
            return f'<span class="ds">{_esc(line)}</span>'
        out.append(f'<span class="ds">{_esc(line[:end + len(state["doc"])])}</span>')
        i = end + len(state["doc"])
        state["doc"] = None

    while i < n:
        c = line[i]
        if c == "#" and not js:
            out.append(f'<span class="cm">{_esc(line[i:])}</span>')
            break
        if js and c == "/" and line[i:i + 2] == "//":
            out.append(f'<span class="cm">{_esc(line[i:])}</span>')
            break
        if js and c == "/" and line[i:i + 2] == "/*":
            end = line.find("*/", i + 2)
            if end >= 0:                      # 单行块注释 /* … */
                out.append(f'<span class="cm">{_esc(line[i:end + 2])}</span>')
                i = end + 2
                continue
            out.append(f'<span class="cm">{_esc(line[i:])}</span>')
            state["doc"] = "*/"
            break
        if c in "\"'":
            tri = line[i:i + 3]
            if tri in ('"""', "'''"):
                end = line.find(tri, i + 3)
                if end < 0:
                    out.append(f'<span class="ds">{_esc(line[i:])}</span>')
                    state["doc"] = tri
                    break
                out.append(f'<span class="ds">{_esc(line[i:end + 3])}</span>')
                i = end + 3
                continue
            m = re.match(r'(?:[rbfu]{0,2})(?:"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', line[i:])
            if m:
                out.append(f'<span class="st">{_esc(m.group(0))}</span>')
                i += m.end()
                continue
            out.append(_esc(c))
            i += 1
            continue
        m = re.match(r"\d[\d_.]*", line[i:])
        if m and not line[i - 1:i].isalnum():
            out.append(f'<span class="nm">{m.group(0)}</span>')
            i += m.end()
            continue
        m = re.match(r"(?:def|class)\s+([A-Za-z_]\w*)", line[i:])
        if m and not js:
            out.append(f'<span class="kw">{m.group(0)[:m.group(0).index(m.group(1))]}'
                       f'</span><span class="fn">{m.group(1)}</span>')
            i += m.end()
            continue
        m = re.match(r"(?:function)\s+([A-Za-z_]\w*)", line[i:])
        if m and js:
            out.append(f'<span class="kw">function </span>'
                       f'<span class="fn">{m.group(1)}</span>')
            i += m.end()
            continue
        m = re.match(r"[A-Za-z_$]\w*", line[i:])
        if m and (i == 0 or not (line[i - 1].isalnum() or line[i - 1] == "_")):
            w = m.group(0)
            cls = "kw" if w in kw else ("bi" if w[0].isupper() else "")
            out.append(f'<span class="{cls}">{w}</span>' if cls else w)
            i += m.end()
            continue
        out.append(_esc(c))
        i += 1
    return "".join(out)


def _render(name, text, others, js=False, note=""):
    lines = text.split("\n")
    state = {"doc": None}
    rows = []
    for k, ln in enumerate(lines, 1):
        code = _hl(ln, state, js) or "&nbsp;"
        rows.append(f'<tr id="L{k}"><td class="ln"><a href="#L{k}">{k}</a></td>'
                    f'<td class="src">{code}</td></tr>')

    # 顶部函数索引
    pat = r"(?:function)\s+([A-Za-z_]\w*)" if js else r"(?:def|class)\s+([A-Za-z_]\w*)"
    idx = []
    for k, ln in enumerate(lines, 1):
        m = re.match(pat, ln.strip())
        if m:
            idx.append(f'<a href="#L{k}">{m.group(1)}</a>')
    nav = " · ".join(f'<a href="{f}.html">{f}</a>' for f in others)
    if name in ANIM:
        ext = "html"
    elif name in JS_FILES:
        ext = "js"
    else:
        ext = "py"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}.{ext} — 源码 · AI 实践库</title>
<style>
  body {{ margin: 0; background: #f5f1e6; color: #2b2a26;
         font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }}
  .bar {{ position: sticky; top: 0; z-index: 5; background: #2b2a26; color: #e8e2d0;
          padding: 10px 18px; font-size: 13px; line-height: 1.9; }}
  .bar b {{ font-family: Georgia, "Songti SC", serif; font-size: 15px; letter-spacing: 1px; }}
  .bar a {{ color: #d9cfa8; text-decoration: none; margin-right: 6px; }}
  .bar a:hover {{ color: #fff; text-decoration: underline; }}
  .bar .back {{ color: #e8a87c; }}
  .idx {{ background: #fbf8ef; border-bottom: 1px solid #ddd5c2; padding: 10px 18px;
          font-size: 13px; line-height: 2; }}
  .idx a {{ display: inline-block; margin-right: 12px; color: #2f6b5a; text-decoration: none; }}
  .idx a:hover {{ text-decoration: underline; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
  td.ln {{ width: 52px; text-align: right; padding: 0 12px 0 8px; color: #a9a294;
           user-select: none; vertical-align: top; font-variant-numeric: tabular-nums; }}
  td.ln a {{ color: inherit; text-decoration: none; }}
  td.src {{ padding-right: 16px; white-space: pre-wrap; word-break: break-all;
            font-family: Consolas, "Courier New", monospace; line-height: 1.65; }}
  tr:hover td {{ background: #efe9d8; }}
  tr.mark td {{ background: #f7e6b8; }}
  tr.mark td.ln {{ background: #e8c98a; color: #6d3518; font-weight: bold; }}
  .cm {{ color: #9a927b; }} .st {{ color: #6f7f4f; }} .ds {{ color: #6f7f4f; }}
  .kw {{ color: #b53d2e; }} .fn {{ color: #2f6b5a; font-weight: bold; }}
  .nm {{ color: #9a6f12; }} .bi {{ color: #3a6b8a; }}
  .tip {{ padding: 8px 18px; font-size: 12.5px; color: #8a8578; }}
</style>
</head>
<body>
<div class="bar">
  <b>{name}.{ext}</b> &nbsp;·&nbsp; 共 {len(lines)} 行 &nbsp;·&nbsp;
  <a class="back" href="../code.html">← 回到代码入口</a>
  &nbsp;·&nbsp; <a href="../index.html">总览</a>
  <div>切换文件：{nav}</div>
</div>
<div class="idx">{' '.join(idx) if idx else '<span style="color:#8a8578">（本文件无函数定义）</span>'}</div>
<div class="tip">{note}链接里的行号在构建时从真实文件算出，改代码后重建即可自动对齐。</div>
<table>
{''.join(rows)}
</table>
<script>
(function () {{
  var m = /L(\\d+)(?:-L(\\d+))?/.exec(location.hash || '');
  if (!m) return;
  var a = +m[1], b = m[2] ? +m[2] : a;
  for (var i = a; i <= b; i++) {{
    var r = document.getElementById('L' + i);
    if (r) r.className = 'mark';
  }}
  var t = document.getElementById('L' + a);
  if (t) t.scrollIntoView({{ block: 'center' }});
}})();
</script>
</body>
</html>"""


def _anim_text(root, name):
    """取 anim_*.html 里 <script> 的内容，去掉首尾空行。"""
    txt = io.open(os.path.join(root, name + ".html"), encoding="utf-8").read()
    m = re.search(r"<script[^>]*>([\s\S]*?)</script>", txt)
    body = m.group(1) if m else ""
    if body.startswith(">"):          # 正则把 <script> 的尖括号也吃了
        body = body[1:]
    return body.strip("\n").strip("\r")


def build_all(root):
    cdir = os.path.join(root, CODE_DIR)
    odir = os.path.join(root, OUT_DIR)
    if not os.path.isdir(odir):
        os.makedirs(odir)
    # 不自动删旧文件：构建脚本在这里 rm 风险太大（src/ 里可能有手写的补充页）。
    # 改成全量覆盖写，最后把「新清单里没有的」打出来交给人工处置。
    # 注：.py 与 .js 都是三个字符，[:-3] 刚好剥掉扩展名
    names = sorted(f[:-3] for f in os.listdir(cdir)
                   if f.endswith((".py", ".js")))
    for nm in names:
        text = io.open(_path_of(root, nm) or "", encoding="utf-8").read()
        io.open(os.path.join(odir, nm + ".html"), "w", encoding="utf-8").write(
            _render(nm, text, names, js=_is_js(nm)))

    # 三个动画：把 <script> 里的算法源码也做成可链接的页面
    anims = [a for a in ANIM if os.path.exists(os.path.join(root, a + ".html"))]
    for nm in anims:
        io.open(os.path.join(odir, nm + ".html"), "w", encoding="utf-8").write(
            _render(nm, _anim_text(root, nm), names + anims, js=True,
                    note=f"这是 {nm}.html 里 &lt;script&gt; 的算法源码（{ANIM[nm]}），"
                         "行号相对 script 开头。"))

    # 孤儿报告：源码文件删了、对应的浏览页却还在。不做自动删除，只报出来。
    written = {nm + ".html" for nm in names + anims}
    orphan = sorted(f for f in os.listdir(odir)
                    if f.endswith(".html") and f not in written)
    if orphan:
        print("  ⚠ src/ 里有孤儿页面（源文件已不存在，需手工确认后删除）："
              + "、".join(orphan))
    return names + anims


# ------------------------------------------------- 行号定位（构建时现算）
_LINES = {}


def _lines(root, fname):
    if fname not in _LINES:
        if fname in ANIM:
            _LINES[fname] = _anim_text(root, fname).split("\n")
        else:
            _LINES[fname] = io.open(_path_of(root, fname),
                                    encoding="utf-8").read().split("\n")
    return _LINES[fname]


def span(root, fname, start, end=None, nth=0):
    """返回 (起始行, 结束行)，1-based 闭区间。

    start : 子串，第 nth 次出现的那一行作为起点（同名方法用它区分）
    end   : 子串；不传就用「下一个同层或更外层的 def / class」的前一行
    """
    ls = _lines(root, fname)
    hit = [i for i, l in enumerate(ls) if start in l]
    if not hit:
        return None
    s = hit[nth] if nth < len(hit) else hit[-1]
    if end:
        j = next((i for i in range(s + 1, len(ls)) if end in ls[i]), len(ls) - 1)
        return (s + 1, j)

    # 不传 end 时：结束于「下一个同层或更外层的 def / class」。
    # 对类里的方法（有缩进）要按缩进比较，否则会一直吞到下一个 class。
    nxt = (r"^\s*(function |/\* -{3,}|// -{3,})" if _is_js(fname)
           else r"^\s*(def |class |# =====)")
    ind = len(ls[s]) - len(ls[s].lstrip())
    for i in range(s + 1, len(ls)):
        l = ls[i]
        if not l.strip():
            continue
        cur = len(l) - len(l.lstrip())
        if cur > ind:                      # 更深的一层，属于本段
            continue
        if re.match(nxt, l):
            return (s + 1, i)
    return (s + 1, len(ls))


def link(root, fname, start, end=None, label="", nth=0):
    """给 B10 用的：一个指向源码片段的链接（新窗口打开）。"""
    r = span(root, fname, start, end, nth)
    if not r:
        return f'<code>{fname}</code>'
    a, b = r
    txt = label or fname
    ln = f"L{a}" if a == b else f"L{a}–{b}"      # 单行时不显示成 L281–281
    return (f'<a class="codelink" href="src/{fname}.html#L{a}-L{b}" '
            f'target="_blank" rel="noopener">{txt}'
            f'<span class="cl-ln">{ln}</span></a>')
