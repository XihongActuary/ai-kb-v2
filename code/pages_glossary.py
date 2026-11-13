# -*- coding: utf-8 -*-
"""AI 实践库 · 术语表（中英双语 · 大白话）"""
from terms import TERMS, CATS, ALIASES


def p_glossary(F):
    h = ["""
<h1><span class="thin">工具 · 随查随用</span>
术语表 · 中英双语大白话</h1>
<p class="lead">遇到看不懂的词，回来这里查。
每个词都配了「一句话大白话」和「一个生活类比」——
<b>没有任何一条是用术语解释术语的</b>。如果发现哪条你看不懂，那就是我们写错了。</p>

<div class="note jade"><b>怎么用这张表：</b>上面方框里输入中文或英文，实时过滤。
<b>正文里凡是带虚线下划线的词，点一下就直接落到这一条的对应位置</b>，
鼠标停在上面还会先浮出一句大白话解释，多数时候不必离开正在读的那页。
每条末尾的链接可以跳到它「在本案例里被真正用到」的那一页——
术语不悬空，看它怎么被用一次，比背十遍定义管用。</div>

<div class="gsearch">
<input id="q" type="text" placeholder="输入中文或英文，例如：IPW / 外推 / 过拟合 / GBDT">
<span class="cnt" id="cnt"></span>
</div>
"""]

    for cat, desc in CATS:
        items = [t for t in TERMS if t["cat"] == cat]
        h.append(f'<h2 id="c-{cat}">{cat}<span class="cat-desc">{desc}</span></h2>')
        h.append('<div class="gloss">')
        for t in items:
            ab = (f'<span class="g-abbr">{t["abbr"]}</span>' if t["abbr"] else "")
            links = "".join(
                f'<a href="{p}.html">{p.upper()}</a>' for p in t["pages"])
            ali = " ".join(ALIASES.get(t["id"], []))
            h.append(f"""<div class="g-item" id="term-{t['slug']}" data-k="{t['zh']} {t['en']} {t['abbr'] or ''} {ali} {t['plain']}">
  <div class="g-head">{ab}<span class="g-zh">{t['zh']}</span>
    <span class="g-en">{t['en']}</span><a class="g-anchor" href="#term-{t['slug']}" title="复制这一条的链接">#</a></div>
  <div class="g-plain">{t['plain']}</div>
  <div class="g-ana"><b>打个比方 ·</b> {t['analogy']}</div>
  <div class="g-pages">本案例出现在：{links}</div>
</div>""")
        h.append("</div>")

    h.append("""
<a class="g-back" id="gback" href="index.html">↩ 回到刚才那一页</a>
<script>
var q=document.getElementById("q"), cnt=document.getElementById("cnt");
var items=[].slice.call(document.querySelectorAll(".g-item"));
function run(){
  var v=(q.value||"").trim().toLowerCase(), n=0;
  items.forEach(function(it){
    var hit = !v || it.getAttribute("data-k").toLowerCase().indexOf(v)>=0;
    it.style.display = hit ? "" : "none";
    if(hit) n++;
  });
  cnt.textContent = v ? ("命中 "+n+" 条") : ("共 "+items.length+" 条");
}
q.addEventListener("input", run);
run();

// 从正文点术语跳进来时：滚到那一条并高亮，同时给一个「回到刚才那一页」的出口
(function(){
  var back=document.getElementById("gback");
  function focus(){
    if(!location.hash) return;
    var el=null;
    try{ el=document.querySelector(location.hash); }catch(e){}
    if(!el) return;
    items.forEach(function(it){ it.classList.remove("hit"); });
    el.classList.add("hit");
    el.scrollIntoView({block:"center"});
    back.style.display="inline-block";
  }
  focus();
  window.addEventListener("hashchange", focus);
  back.addEventListener("click", function(e){
    // 有来路就原路返回，直接打开本页时退回知识地图
    if(history.length>1){ e.preventDefault(); history.back(); }
  });
})();
</script>

<div class="quote q-talk"><span class="q-tag">说人话</span>
<p>如果你把这张表从头读到尾，你会发现一件有意思的事：
<b>机器学习里真正难的词不超过十个，剩下都是同一件事换了个说法。</b>
之所以看着唬人，是因为每个领域都给同一件事起了自己的名字——
精算叫「费率因子」，统计叫「回归系数」，机器学习叫「特征权重」，说的是同一个东西。</p></div>

<div class="quote q-warn"><span class="q-tag">特别提醒</span>
<p>记住一条防身技巧：<b>任何解释里出现「本质上」「某种意义上」「简单来说」却越说越绕的，
基本可以判定为作者自己也没搞懂。</b>遇到这种，换一本书看，别怀疑自己。</p></div>
""")
    return "".join(h)
