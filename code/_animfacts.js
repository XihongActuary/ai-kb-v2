/* 复算三个动画的最终数字，写进 out/anim_facts.json。
 *
 * 为什么要有这个脚本：
 *   动画是纯前端算法，跑在浏览器里，Python 流水线够不着它。
 *   但讲解里要引用的「收敛到多少、误差降到多少」必须是真跑出来的，
 *   不能靠人眼从动画里估。这里把动画里的算法逐行搬到 node 上重算一遍，
 *   结果落成 JSON，页面再从 JSON 取值 —— 和全站「数字只有一个来源」是同一条规矩。
 *
 * 用法：node code/_animfacts.js     （改完任何一个动画都要重跑）
 * 前提：三份算法必须与 anim_*.html 里的 <script> 保持一致，否则数字会对不上。
 */
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, '..', 'out', 'anim_facts.json');
const R = {};

/* ================= ① Poisson GLM · IRLS ================= */
(function () {
  var rng = (function () { var s = 20261003; return function () { s = (s * 1103515245 + 12345) >>> 0; return s / 4294967296; }; })();
  var N = 46, X = [], Y = [], B0T = -0.55, B1T = -0.028;
  for (var i = 0; i < N; i++) {
    var age = 19 + Math.floor(rng() * 56);
    var lam = Math.exp(B0T + B1T * (age - 40));
    var y = 0, L = Math.exp(-lam), p = 1, k = 0;
    do { k++; p *= rng(); } while (p > L);
    y = k - 1; X.push(age); Y.push(y);
  }
  function irlsStep(b0, b1) {
    var Sxx = 0, Sxz = 0, Sx = 0, Sz = 0, n = X.length;
    for (var i = 0; i < n; i++) {
      var eta = b0 + b1 * (X[i] - 40);
      eta = Math.max(Math.min(eta, 4), -4);
      var mu = Math.exp(eta), w = mu, z = eta + (Y[i] - mu) / mu;
      Sxx += w * (X[i] - 40) * (X[i] - 40); Sxz += w * (X[i] - 40) * z;
      Sx += w * (X[i] - 40); Sz += w * z;
    }
    var Sw = n * Sxx - Sx * Sx;
    if (Math.abs(Sw) < 1e-10) return [b0, b1];
    return [(Sxx * Sz - Sx * Sxz) / Sw, (n * Sxz - Sx * Sz) / Sw];
  }
  function dev(b0, b1) {
    var d = 0;
    for (var i = 0; i < N; i++) {
      var mu = Math.exp(b0 + b1 * (X[i] - 40)), y = Y[i];
      if (y > 0) d += 2 * (y * Math.log(y / mu) - (y - mu)); else d += 2 * mu;
    }
    return d;
  }
  var st = [{ b0: 0, b1: 0 }];
  for (var s2 = 0; s2 < 7; s2++) {
    var p = st[st.length - 1], q = irlsStep(p.b0, p.b1);
    st.push({ b0: q[0], b1: q[1] });
  }
  st.forEach(function (x) { x.dev = dev(x.b0, x.b1); });
  var last = st[st.length - 1];
  R.glm = {
    n: N, rounds: st.length - 1,
    steps: st.map(function (x) { return { b0: +x.b0.toFixed(4), b1: +x.b1.toFixed(4), dev: +x.dev.toFixed(2) }; }),
    b0: +last.b0.toFixed(4), b1: +last.b1.toFixed(4),
    dev0: +st[0].dev.toFixed(2), dev_end: +last.dev.toFixed(2),
    rr: +Math.exp(last.b1).toFixed(4),               // 每大一岁，出险强度乘几倍
    drop_pct: +(100 * (1 - Math.exp(last.b1))).toFixed(2),
    b1_true: B1T, b0_true: B0T,
    drop_pct_true: +(100 * (1 - Math.exp(B1T))).toFixed(2)
  };
})();

/* ================= ② 决策树 · 基尼分裂 ================= */
(function () {
  var MINLEAF = 5;
  var rng = (function () { var s = 77031; return function () { s = (s * 1103515245 + 12345) >>> 0; return s / 4294967296; }; })();
  var N = 56, D = [];
  for (var i = 0; i < N; i++) {
    var age = 19 + rng() * 55, mile = 8000 + rng() * 38000;
    var pp = 1 / (1 + Math.exp(-(0.115 * (28 - age) + 0.00007 * (mile - 15000) - 1.1)));
    D.push({ age: age, mile: mile, r: rng() < pp });
  }
  function gini(ix) {
    if (!ix.length) return 0;
    var n1 = 0;
    for (var i = 0; i < ix.length; i++) if (D[ix[i]].r) n1++;
    var p = n1 / ix.length; return 2 * p * (1 - p);
  }
  function pR(ix) {
    var n1 = 0;
    for (var i = 0; i < ix.length; i++) if (D[ix[i]].r) n1++;
    return n1 / ix.length;
  }
  function splitGain(idx, attr, thr) {
    var L = [], R = [];
    for (var i = 0; i < idx.length; i++) (D[idx[i]][attr] <= thr ? L : R).push(idx[i]);
    if (L.length < MINLEAF || R.length < MINLEAF) return null;
    var w = (L.length * gini(L) + R.length * gini(R)) / idx.length;
    return { gain: gini(idx) - w, weighted: w, L: L, R: R, nL: L.length, nR: R.length };
  }
  function scan(idxs) {
    var best = null;
    ["age", "mile"].forEach(function (attr) {
      var vals = idxs.map(function (i) { return D[i][attr]; }).sort(function (a, b) { return a - b; });
      for (var j = 4; j < vals.length - 4; j += 3) {
        var thr = (vals[j] + vals[j + 1]) / 2, g = splitGain(idxs, attr, thr);
        if (!g) continue;
        var cand = { attr: attr, thr: thr, g: g, idxs: idxs };
        if (!best || g.gain > best.g.gain) best = cand;
      }
    });
    return best;
  }
  /* pack：把一刀的完整「收支表」都留下来。
   * 页面上要手算 Gain：切之前 − 切之后，两个数都必须是真跑出来的，不能靠人凑。 */
  function pack(x, tag, knife) {
    if (!x) return null;
    var ix = x.idxs, L = x.g.L, R = x.g.R;
    var w = x.g.weighted;
    return {
      knife: knife, tag: tag,
      attr: x.attr, thr: +x.thr.toFixed(1),
      n_parent: ix.length, p_parent: +pR(ix).toFixed(3),
      gini_before: +gini(ix).toFixed(4),
      nL: x.g.nL, pL: +pR(L).toFixed(3), gini_L: +gini(L).toFixed(4),
      nR: x.g.nR, pR: +pR(R).toFixed(3), gini_R: +gini(R).toFixed(4),
      gini_after: +w.toFixed(4),
      gain: +x.g.gain.toFixed(4)
    };
  }
  var root = D.map(function (_, i) { return i; });
  var b1 = scan(root);
  var b2 = b1 ? scan(b1.g.L) : null;
  var b3 = b1 ? scan(b1.g.R) : null;
  /* 最终叶子：某一层切不动时，它父节点那一整组就是一片叶子 */
  var leaves = [];
  function leafOf(sp, side) {
    var ix = side === "L" ? sp.g.L : sp.g.R;
    return { n: ix.length, p: +pR(ix).toFixed(3) };
  }
  if (b1) {
    if (b2) { leaves.push(leafOf(b2, "L")); leaves.push(leafOf(b2, "R")); }
    else leaves.push(leafOf(b1, "L"));
    if (b3) { leaves.push(leafOf(b3, "L")); leaves.push(leafOf(b3, "R")); }
    else leaves.push(leafOf(b1, "R"));
  }
  var purest = leaves.reduce(function (a, x) { return (!a || x.p < a.p) ? x : a; }, null);
  var dirtiest = leaves.reduce(function (a, x) { return (!a || x.p > a.p) ? x : a; }, null);
  R.tree = {
    n: N, min_leaf: MINLEAF,
    n_risk: D.filter(function (d) { return d.r; }).length,
    root_p: +pR(root).toFixed(3), root_gini: +gini(root).toFixed(4),
    s1: pack(b1, "全部", 1), s2: pack(b2, "左组", 2), s3: pack(b3, "右组", 3),
    leaves: leaves,
    purest: purest, dirtiest: dirtiest,
    n_splits: [b1, b2, b3].filter(function (x) { return !!x; }).length,
    left_small: b1 ? b1.g.L.length : 0
  };
})();

/* ================= ③ GBDT · 逐轮补残差 ================= */
(function () {
  var rng = (function () { var s = 920241; return function () { s = (s * 1103515245 + 12345) >>> 0; return s / 4294967296; }; })();
  var N = 80, X = [], Y = [];
  function truth(x) { return 1.0 + 0.55 * Math.pow((x - 50) / 22, 2); }
  for (var i = 0; i < N; i++) { var x = 18 + rng() * 64; X.push(x); Y.push(truth(x) + (rng() - 0.5) * 0.34); }
  var LR = 0.45, MAXD = 2, M = 8;
  function meanOf(ix, r) { var m = 0; ix.forEach(function (i) { m += r[i]; }); return m / ix.length; }
  function sseOf(ix, r) { var m = meanOf(ix, r), s = 0; ix.forEach(function (i) { s += Math.pow(r[i] - m, 2); }); return s; }
  function fitStump(res) {
    var idx = X.map(function (_, i) { return i; });
    function bestSplit(idxs) {
      var bs = null;
      for (var j = 0; j < idxs.length; j++) for (var k2 = j + 1; k2 < idxs.length; k2++) {
        var thr = (X[idxs[j]] + X[idxs[k2]]) / 2, L = [], R = [];
        idxs.forEach(function (i) { (X[i] <= thr ? L : R).push(i); });
        if (L.length < 5 || R.length < 5) continue;
        var sse = sseOf(L, res) + sseOf(R, res);
        if (!bs || sse < bs.sse) bs = { thr: thr, sse: sse, L: L, R: R };
      }
      return bs;
    }
    function mk(ix) { return { idxs: ix, sse0: sseOf(ix, res), leaf: meanOf(ix, res), thr: undefined }; }
    var rt = mk(idx);
    function grow(node, depth) {
      if (depth >= MAXD) return;
      var bs = bestSplit(node.idxs); if (!bs) return;
      if (bs.sse >= node.sse0 * 0.98) return;
      node.thr = bs.thr; node.l = mk(bs.L); node.r = mk(bs.R);
      grow(node.l, depth + 1); grow(node.r, depth + 1);
    }
    grow(rt, 0); return rt;
  }
  function sp(n, x) { while (n.thr !== undefined) { n = x <= n.thr ? n.l : n.r; } return n.leaf; }
  function lc(n) { return n.thr === undefined ? 1 : lc(n.l) + lc(n.r); }
  var trees = [], rounds = [{ F: X.map(function () { return 0; }) }];
  for (var r = 0; r < M; r++) {
    var Fp = rounds[rounds.length - 1].F;
    var res = Y.map(function (y, i) { return y - Fp[i]; });
    var t = fitStump(res); trees.push(t);
    rounds.push({ F: X.map(function (_, i) { return Fp[i] + LR * sp(t, X[i]); }) });
  }
  function mse(F) { var s = 0; for (var i = 0; i < N; i++) s += Math.pow(Y[i] - F[i], 2); return s / N; }
  var noise = 0;
  for (var i = 0; i < N; i++) noise += Math.pow(Y[i] - truth(X[i]), 2);
  noise /= N;
  R.gbdt = {
    n: N, lr: LR, max_depth: MAXD, rounds: M,
    mse: rounds.map(function (x) { return +mse(x.F).toFixed(4); }),
    noise_emp: +noise.toFixed(4),
    noise_theory: +(0.34 * 0.34 / 12).toFixed(4),     // 均匀噪声 ±0.17 的理论方差
    leaf_counts: trees.map(lc)
  };
})();

fs.writeFileSync(OUT, JSON.stringify(R, null, 1), 'utf8');
console.log('写出 ' + OUT);
console.log('  GLM  β₁=' + R.glm.b1 + '（真值 ' + R.glm.b1_true + '）  deviance ' + R.glm.dev0 + ' → ' + R.glm.dev_end);
console.log('  树   第一刀 ' + R.tree.s1.attr + ' ≤ ' + R.tree.s1.thr +
  '（左 ' + R.tree.s1.nL + ' 人 ' + Math.round(R.tree.s1.pL * 100) + '% 高风险）  共切 ' + R.tree.n_splits + ' 刀');
['s1', 's2', 's3'].forEach(function (k) {
  var s = R.tree[k];
  if (s) console.log('    ' + k + ' 第' + s.knife + '刀·' + s.tag + ' ' + s.attr + ' ≤ ' + s.thr +
    '  Gini ' + s.gini_before + ' → ' + s.gini_after + '  Gain ' + s.gain);
});
console.log('  GBDT MSE ' + R.gbdt.mse[0] + ' → ' + R.gbdt.mse[R.gbdt.mse.length - 1] +
  '（噪声地板 实测 ' + R.gbdt.noise_emp + ' / 理论 ' + R.gbdt.noise_theory + '）');
