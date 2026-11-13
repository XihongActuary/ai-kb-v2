// 三个动画的冒烟测试（正式资产，不是临时脚本）：
//   1. stub 掉 DOM/Canvas，执行动画脚本，确认运行时不抛错；
//   2. 画布尺寸从 HTML 里读真实值（三个动画都叫「cv」，缓存必须每次覆盖，否则串味）；
//   3. 拦截所有绘制调用，抓出画到画布外的图元 —— 越界的点是直接消失的，肉眼最难发现。
// 用法：node code/test_anim.js —— 改完任何一个动画都必须跑。
const fs = require('fs');
const path = require('path');

/* ---- 绘制越界检查：伪造 canvas context，抓出画到画布外的图元 ---- */
let TAG = '?';
const OUT = [];
function charW(s, fs) {
  let w = 0;
  for (const ch of String(s)) w += fs * (ch.charCodeAt(0) > 0x2000 ? 1.0 : 0.55);
  return w;
}
function makeCtx(w, h) {
  const st = { font: '12px sans-serif' };
  const fs = () => parseFloat((st.font.match(/([\d.]+)px/) || [0, 12])[1]) || 12;
  const note = (k, x, y) => OUT.push(`${TAG} ${k}(${(+x).toFixed(1)},${(+y).toFixed(1)}) 画布 ${w}x${h}`);
  return new Proxy({}, {
    get: (t, k) => {
      if (k === 'canvas') return { width: w, height: h };
      return (...a) => {
        /* 注意：fillText 的签名是 (text, x, y)，其余图元是 (x, y, ...) */
        if (k === 'fillText' || k === 'strokeText') {
          const x = a[1], y = a[2];
          if (typeof x === 'number' && typeof y === 'number') {
            if (y < -2 || y > h + 2) note(k + '「' + a[0] + '」', x, y);
            else {
              const x1 = x + charW(a[0], fs());
              if (x < -2 || x1 > w + 2) note(k + '溢出「' + a[0] + '」', x1, y);
            }
          }
          return undefined;
        }
        if (k === 'moveTo' || k === 'lineTo') {
          const [x, y] = a;
          if (typeof x === 'number' && typeof y === 'number' && (x < -2 || x > w + 2 || y < -2 || y > h + 2))
            note(k, x, y);
        }
        if (k === 'arc') {
          const [x, y, r] = a;
          if (typeof x === 'number' && (x - r < -2 || x + r > w + 2 || y - r < -2 || y + r > h + 2))
            note('arc r=' + (+r).toFixed(1), x, y);
        }
        if (k === 'fillRect' || k === 'strokeRect') {
          const [x, y, ww, hh] = a;
          if (typeof x === 'number' && (x < -2 || x + ww > w + 2 || y < -2 || y + hh > h + 2))
            note(k + ' ' + (+ww).toFixed(0) + 'x' + (+hh).toFixed(0), x, y);
        }
        return undefined;
      };
    },
    set: (t, k, v) => { st[k] = v; return true; }
  });
}

const ctxProxy = makeCtx(560, 420);

function el(id) {
  return {
    id, width: 560, height: 420,
    textContent: '', innerHTML: '', value: '900',
    className: '', onclick: null, onchange: null, style: {},
    getContext() { return makeCtx(this.width, this.height); },
    appendChild() {}, addEventListener() {},
    setAttribute() {}, getAttribute() { return 'x'; },
    querySelectorAll: () => []
  };
}

const cache = {};
// 画布尺寸从 HTML 里读真实值，否则 stub 的固定尺寸会让坐标算错、掩盖布局问题
const CANVAS = {};
function harvestCanvas(html) {
  const re = /<canvas id="(\w+)" width="(\d+)" height="(\d+)"/g;
  let m;
  while ((m = re.exec(html))) CANVAS[m[1]] = { width: +m[2], height: +m[3] };
}
global.document = {
  getElementById: (id) => {
    if (!cache[id]) cache[id] = el(id);
    if (CANVAS[id]) Object.assign(cache[id], CANVAS[id]);   // 每次都覆盖：三个动画共用 id「cv」，缓存会串味
    return cache[id];
  },
  createElement: () => el('new'),
  querySelectorAll: () => []
};
global.setInterval = () => 0;
global.clearInterval = () => {};

/* 只跑初始化抓不到「最后一幕崩了」——三个动画的绘制入口名字各不相同，
   这里按「绘制函数 + 步数数组」成对探测，把每一幕都真的画一遍。
   树动画就曾在这里翻过车：第一刀切出 5 人的叶子，第二层没有候选，
   终幕拿到 null 直接抛错，而初始化阶段一切正常。 */
const TAIL = `
;(function () {
  var pairs = [["show", "steps"], ["drawScene", "SC"], ["draw", "rounds"]];
  for (var i = 0; i < pairs.length; i++) {
    var fn = null, arr = null;
    try { fn = eval(pairs[i][0]); } catch (e) {}
    try { arr = eval(pairs[i][1]); } catch (e) {}
    if (typeof fn === "function" && arr && arr.length) {
      for (var k = 0; k < arr.length; k++) fn(k);
      return;
    }
  }
})();`;

const ROOT = path.dirname(__dirname);   // __dirname = ai-kb/code → ROOT = ai-kb
let ok = true;
for (const f of ['anim_glm', 'anim_tree', 'anim_gbdt']) {
  const html = fs.readFileSync(path.join(ROOT, f + '.html'), 'utf8');
  const m = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!m) { console.log(f + ': NO SCRIPT'); ok = false; continue; }
  harvestCanvas(html);
  TAG = f;
  const before = OUT.length;
  try {
    new Function(m[1] + TAIL)();
    const bad = OUT.length - before;
    console.log(f + ': RUNTIME OK' + (bad ? `  ✗ 越界 ${bad} 处` : '  画布内 ✓'));
    OUT.slice(before, before + 4).forEach(s => console.log('    ' + s));
    if (bad) ok = false;
  } catch (e) {
    console.log(f + ': ERROR -> ' + e.message);
    ok = false;
  }
}
process.exit(ok ? 0 : 1);
