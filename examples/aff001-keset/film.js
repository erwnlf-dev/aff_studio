// Affiliate — Keset diatomite motif kucing (Shopee 55566811995). Disutradarai per produk (aff_studio ADR-P06).
// Gaya midcentury-toon (kit Slate `midcentury`, lemo-opuscar MIT). 1080x1920, 24 fps. Murni fungsi t.
// Timing: vo.json job 2026-10-20-9fed21, onset dikoreksi ke jendela sunyi terukur (kata_koreksi.json).
import { PAL, setClock, shape, plane, ink, rays, ellipse, rect, rrect, spline, star, text, fit, measure, xform,
  paperFinish, dashed, clamp, lerp, seg, ss, eo, eio, back, hash, TAU } from './engine/toon.js';
import { drawHand } from './engine/chars.js';
import { FOTO } from './aset/foto.js';

const W = 1080, H = 1920, FPS = 24;
const KATA = [[0.0, 0.24, 'Keset'], [0.28, 0.56, 'kucing'], [0.62, 0.96, 'ini,'], [0.987, 1.28, 'nyerap'], [1.36, 1.72, 'air?'],
  [2.36, 2.52, 'Habis'], [2.568, 3.08, 'mandi,'], [3.12, 3.48, 'lantai'], [3.54, 3.8, 'basah'], [3.84, 3.96, 'dan'],
  [4.02, 4.52, 'licin?'], [5.14, 5.72, 'Kenalin…'], [6.12, 6.36, 'keset'], [6.413, 6.92, 'diatomite'], [6.973, 7.24, 'motif'],
  [7.28, 7.8, 'kucing.'], [8.38, 8.6, 'Daya'], [8.63, 8.88, 'serapnya'], [8.944, 9.52, 'tinggi,'], [9.56, 9.92, 'lantai'],
  [9.96, 10.16, 'tetap'], [10.2, 10.72, 'kering.'], [11.28, 11.647, 'Alasnya'], [11.695, 12.287, 'anti-slip,'],
  [12.314, 12.527, 'nggak'], [12.607, 12.927, 'gampang'], [12.987, 13.52, 'geser.'], [14.12, 14.414, 'Sebulan'],
  [14.474, 14.894, 'terjual'], [14.954, 15.334, 'sepuluh'], [15.364, 15.654, 'ribu'], [15.687, 15.96, 'lebih.'],
  [16.56, 16.954, 'Motifnya'], [17.011, 17.514, 'banyak,'], [17.554, 17.674, 'cek'], [17.727, 17.834, 'di'], [17.882, 18.074, 'link'],
  [18.154, 18.394, 'ya.']];

// setiap hentakan/pendaratan: [id, frame, indeks kata]
const CUE_LIST = [['serap', 24, 3], ['kaki_basah', 85, 8], ['licin', 96, 10], ['keset_jatuh', 123, 11], ['nama', 147, 12],
  ['motif', 167, 14], ['tetes_1', 207, 17], ['tetes_2', 215, 18], ['kering', 245, 21], ['balik', 271, 22], ['dorong', 296, 24],
  ['pental', 312, 26], ['cap', 359, 29], ['segel', 376, 31], ['motif_pop', 397, 32], ['cek', 421, 34], ['link', 429, 36]];
export const CUES = [{ id: 'hook_tetes', t: 13 / FPS }, { id: 'hook_tetes_2', t: 35 / FPS }]
  .concat(CUE_LIST.map(([id, f, k]) => ({ id, t: f / FPS, kata: k, teks: KATA[k][2] })));
const C = {}; CUES.forEach(c => { C[c.id] = c.t; });

export const META = {
  dur: 18.72,
  kontras: [['#2B2420', '#FBF6EA'], ['#2B2420', '#F4EAD5'], ['#2B2420', '#E8B43A'], ['#B8452B', '#FBF6EA'], ['#FBF6EA', '#257A74'],
    ['#2B2420', '#F3D37F']],
};
const LOOP_AT = 18.45, LOOP_END = 18.68;
const AIR = PAL.blueL, AIR_D = PAL.blueD;

// ------------------------------------------------------------ cutout produk: gambar, siluet tinta, bayangan, sisi bawah
const IMG = {}, SIL = {}, BAY = {}, BAWAH = {};
function topeng(im, isi) {
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
  const g = c.getContext('2d'); g.drawImage(im, 0, 0); g.globalCompositeOperation = 'source-in'; isi(g, c.width, c.height);
  return c;
}
if (typeof Image !== 'undefined') {
  await Promise.all(Object.entries(FOTO).map(([k, v]) => new Promise(ok => {
    const im = new Image(); im.onload = () => { IMG[k] = im; ok(); }; im.onerror = () => ok(); im.src = v.src;
  })));
  for (const [k, im] of Object.entries(IMG)) {
    SIL[k] = topeng(im, (g, w, h) => { g.fillStyle = PAL.ink; g.fillRect(0, 0, w, h); });
    BAY[k] = topeng(im, (g, w, h) => { g.fillStyle = PAL.brown; g.fillRect(0, 0, w, h); });
    BAWAH[k] = topeng(im, (g, w, h) => {           // sisi bawah anti-slip (ilustrasi): navy berpola titik
      g.fillStyle = '#7F8FB4'; g.fillRect(0, 0, w, h);
      g.globalCompositeOperation = 'source-atop'; g.fillStyle = '#C9D3EA';   // titik hanya di dalam siluet, latar tetap
      const s = Math.max(w, h) / 34;
      for (let y = s / 2, r = 0; y < h; y += s, r++) for (let x = (r % 2) * s / 2; x < w; x += s) { g.beginPath(); g.arc(x, y, s * 0.22, 0, TAU); g.fill(); }
    });
  }
}
function produk(ctx, nama, cx, cy, w, o = {}) {
  const im = IMG[nama]; if (!im) return;
  const h = w * im.height / im.width, a = o.alpha ?? 1;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy); ctx.rotate(o.rot || 0); ctx.scale(o.sx ?? 1, o.sy ?? 1);
  if (o.bayang !== false) { ctx.save(); ctx.globalAlpha *= 0.3; ctx.drawImage(BAY[nama], -w / 2 + 12, -h / 2 + (o.tinggi ?? 18), w, h); ctx.restore(); }
  for (let i = 0; i < 10; i++) { const t = i * TAU / 10; ctx.drawImage(SIL[nama], -w / 2 + Math.cos(t) * 4.5, -h / 2 + Math.sin(t) * 4.5, w, h); }
  ctx.drawImage(o.bawah ? BAWAH[nama] : im, -w / 2, -h / 2, w, h);
  ctx.restore();
}
const tinggiProduk = (nama, w) => IMG[nama] ? w * IMG[nama].height / IMG[nama].width : w * 0.75;

// ------------------------------------------------------------ helper
const pop = (t, t0, d = 0.28) => back(seg(t, t0, t0 + d), 1.8);
const E_in = u => u * u;
const kf = (t, keys, e = eio) => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
    const [t0, a] = keys[i - 1], [t1, b] = keys[i], u = (keys[i][2] || e)(seg(t, t0, t1));
    return Array.isArray(a) ? a.map((v, j) => lerp(v, b[j], u)) : lerp(a, b, u);
  }
  return keys[keys.length - 1][1];
};
function squash(t, t0, sx = 0.12, sy = 0.1) {          // benda datar mendarat: 1,12 × 0,9 selama 2 frame lalu pegas
  if (t < t0) return [1, 1];
  const u = (t - t0) * FPS;
  if (u < 2) return [1 + sx, 1 - sy];
  const d = Math.exp(-(u - 2) * 0.35) * Math.cos((u - 2) * 0.55);
  return [1 + sx * d, 1 - sy * d];
}
function cam(ctx, z, cx, cy) { ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy); }
function ubin(ctx, col, s = 180, o = 0) {               // lantai ubin dilihat dari atas, nat putih
  ctx.fillStyle = col; ctx.fillRect(-400, -400, W + 800, H + 800);
  for (let x = -s + o; x < W + s; x += s) ink(ctx, [[x, -300], [x, H + 300]], 5, { color: PAL.white, seed: 40 + x, taper: false, breaks: 0.12 });
  for (let y = -s + o; y < H + s; y += s) ink(ctx, [[-300, y], [W + 300, y]], 5, { color: PAL.white, seed: 90 + y, taper: false, breaks: 0.12 });
}
function genangan(ctx, cx, cy, r, k = 1, seed = 1) {   // air di lantai: elips bergelombang + kilau
  if (k <= 0.02) return;
  const pts = ellipse(cx, cy, r * k, r * 0.62 * k, 28).map(([x, y], i) => [x + 5 * k * Math.sin(i * 1.7 + seed), y + 4 * k * Math.cos(i * 1.3 + seed)]);
  shape(ctx, pts, { fill: AIR, line: 3.4, seed, grain: 0.15, breaks: 0.1 });
  ink(ctx, ellipse(cx - r * 0.25 * k, cy - r * 0.15 * k, r * 0.4 * k, r * 0.18 * k, 16, Math.PI * 1.1, Math.PI * 1.6), 5 * k, { color: PAL.white, seed: seed + 3 });
}
function tetes(ctx, x, y, r, sy = 1) {                  // tetes air (ujung di atas)
  const pts = xform(spline([[0, -1.9], [0.62, -0.55], [1, 0.3], [0.7, 0.9], [0, 1.1], [-0.7, 0.9], [-1, 0.3], [-0.62, -0.55]], true, 6), x, y, 0, r, r * sy);
  shape(ctx, pts, { fill: AIR, line: 3.6, seed: 61, grain: 0.1, breaks: 0 });
  ink(ctx, ellipse(x - r * 0.35, y + r * 0.05, r * 0.2, r * 0.36, 10), 4, { color: PAL.white, seed: 62 });
}
function percik(ctx, cx, cy, t, t0, r = 70) {           // cincin percik 6 frame + 4 butir di busur
  const u = seg(t, t0, t0 + 6 / FPS); if (u <= 0 || u >= 1) return;
  ink(ctx, ellipse(cx, cy, r * (0.4 + 0.8 * eo(u)), r * 0.45 * (0.4 + 0.8 * eo(u)), 30), 5 * (1 - u), { color: AIR_D, closed: true, seed: 63 });
  for (let i = 0; i < 4; i++) {
    const a = -Math.PI * (0.2 + 0.2 * i), d = r * (0.5 + 0.9 * eo(u));
    tetes(ctx, cx + Math.cos(a) * d * 1.4, cy + Math.sin(a) * d - 60 * Math.sin(Math.PI * u), 9 * (1 - u * 0.6), 1);
  }
}
function gayung(ctx, x, y, a, k = 1) {                  // gayung plastik koral: mangkuk + gagang, berporos di bibir mangkuk
  ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.scale(k, k);
  shape(ctx, rrect(40, -34, 230, 46, 18), { fill: PAL.coral, line: 4, seed: 70, grain: 0.25 });
  shape(ctx, spline([[-120, -60], [0, -70], [20, 40], [-10, 120], [-120, 130], [-200, 110], [-215, 30], [-205, -55]], true, 6), { fill: PAL.coral, line: 4.4, seed: 71, grain: 0.3, shade: [{ pts: rect(-220, 40, 120, 100), color: PAL.coralD, alpha: 0.45 }] });
  shape(ctx, ellipse(-100, -64, 112, 22, 30), { fill: PAL.coralD, line: 4, seed: 72, grain: 0.2 });
  ctx.restore();
}
function lengan(ctx, from, pergelangan, k = 1) {
  ink(ctx, [from, pergelangan], 30 * k, { seed: 140, taper: false, wob: 0.03 });
  ink(ctx, [from, pergelangan], 22 * k, { seed: 141, taper: false, wob: 0.03, color: PAL.coral });
}
function tanganDi(ctx, ujung, a, jenis, k, dari, sisi = 1) {
  const jangkau = (jenis === 'point' ? 57 : jenis === 'grip' ? 30 : 44) * k;
  const w = [ujung[0] - Math.cos(a) * jangkau, ujung[1] - Math.sin(a) * jangkau];
  if (dari) lengan(ctx, dari, w, k / 2.2);
  drawHand(ctx, w[0], w[1], a, jenis, sisi, k);
  return w;
}
function pelat(ctx, str, x, y, font, o = {}) {          // kartu putih bertinta untuk teks kunci
  const w = measure(ctx, str, font) + (o.pad ?? 48), px = parseInt(font.match(/(\d+)px/)[1], 10), h = px * 1.34;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? 0); ctx.scale(o.k ?? 1, o.k ?? 1);
  shape(ctx, rrect(-w / 2, -h / 2, w, h, 14), { fill: o.fill ?? PAL.white, line: 4, seed: o.seed ?? 760, grain: 0.12, off: [6, 5] });
  text(ctx, str, 0, px * 0.36, { font, fill: o.color ?? PAL.ink, align: 'center' });
  ctx.restore();
}
function teksKunci(ctx, t, t0, str, y = 330) {
  const k = pop(t, t0, 0.28); if (k <= 0) return;
  pelat(ctx, str, W / 2, y, '92px Slab', { k, rot: -0.02, seed: 770 + str.length });
}
function labelIlustrasi(ctx, x, y) { text(ctx, 'ilustrasi', x, y, { font: '600 30px Jost', fill: PAL.ink, plate: PAL.white, off: [3, 3] }); }

// ------------------------------------------------------------ disclosure (setiap frame) + caption
function disclosure(ctx) {
  const font = '600 34px Jost', w = measure(ctx, 'Link afiliasi', font) + 64;
  ctx.save(); ctx.translate(60, 175);
  shape(ctx, [[0, 0], [w - 22, 0], [w, 28], [w - 22, 56], [0, 56]], { fill: PAL.white, line: 3.4, seed: 980, grain: 0.1, breaks: 0, off: [4, 4] });
  shape(ctx, ellipse(w - 30, 28, 7, 7, 14), { fill: PAL.kraftL, line: 2.6, seed: 981, off: [0, 0] });
  text(ctx, 'Link afiliasi', 20, 40, { font, fill: PAL.ink });
  ctx.restore();
}
// [kata awal, kata akhir, kata disorot]; angka sebagai digit di caption
const CAP = [[0, 4, 3], [5, 10, 10], [11, 15, 13], [16, 21, 21], [22, 26, 23], [27, 31, 29], [32, 37, 36]];
const DIGIT = { 29: '10' };
const CHUNKS = CAP.map(([a, b, s]) => ({ toks: KATA.slice(a, b + 1).map((k, j) => [DIGIT[a + j] ?? k[2], a + j, a + j === s]), a: KATA[a][0], b: KATA[b][1] }));
CHUNKS.forEach((c, i) => { const nx = CHUNKS[i + 1]; c.end = nx ? Math.min(nx.a, c.b + 0.5) : META.dur; });
function caption(ctx, t) {
  const c = CHUNKS.find(q => t >= Math.max(0, q.a - 0.04) && t < q.end); if (!c) return;
  const a = c.a <= 0 ? 1 : Math.min(ss(seg(t, c.a - 0.04, c.a + 0.08)), c.end >= META.dur ? 1 : 1 - ss(seg(t, c.end - 0.1, c.end)));
  if (a <= 0) return;
  const str = c.toks.map(q => q[0]).join(' ');
  const f = fit(ctx, str, '600 {px}px Jost', 68, 900, 2, 64);
  const sp = measure(ctx, ' ', f.font), lh = f.px * 1.2;
  const w = Math.max(...f.lines.map(l => measure(ctx, l, f.font))) + 96, h = 34 + f.lines.length * lh, x = W / 2 - w / 2, y = 1470 - h;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(0, (1 - a) * 12);
  shape(ctx, rrect(x, y, w, h, 16), { fill: PAL.paper, line: 3.4, seed: 901, grain: 0.12, breaks: 0.06, off: [5, 5] });
  star(ctx, x + 26, y + h / 2, 11, { n: 8, inner: 0.42, fill: PAL.mustard, off: [0, 0] });
  star(ctx, x + w - 26, y + h / 2, 11, { n: 8, inner: 0.42, fill: PAL.mustard, off: [0, 0] });
  let ti = 0;
  f.lines.forEach((l, li) => {
    const words = l.split(' '), ws = words.map(wd => measure(ctx, wd, f.font));
    let xx = W / 2 - (ws.reduce((p, q) => p + q, 0) + sp * (words.length - 1)) / 2;
    const by = y + 17 + f.px * 0.92 + li * lh;
    words.forEach((wd, j) => {
      const tok = c.toks[ti++];
      if (tok && tok[2]) {
        const k = clamp(back(seg(t, KATA[tok[1]][0] - 0.02, KATA[tok[1]][0] + 0.22), 1.6), 0, 1.15);
        if (k > 0) { ctx.save(); ctx.translate(xx + ws[j] / 2, by - f.px * 0.33); ctx.scale(k, k);
          shape(ctx, rrect(-ws[j] / 2 - 9, -f.px * 0.62, ws[j] + 18, f.px * 1.12, 9), { fill: PAL.mustard, line: 0, off: [3, 3], grain: 0.1, seed: 905 + j }); ctx.restore(); }
      }
      text(ctx, wd, xx, by, { font: f.font, fill: PAL.ink });
      xx += ws[j] + sp;
    });
  });
  ctx.restore();
}

// ------------------------------------------------------------ 1. HOOK (0 – 2,333): gayung meneteskan air, keset menyerapnya
const KS1 = { x: 540, y: 1080, w: 820, rot: -0.1 };
const BIBIR1 = [600, 660];                          // bibir gayung (titik lepas tetes)
function gayungSudut1(t) { return kf(t, [[0, -0.42], [0.12, -0.56, eo], [0.25, -0.08, eio], [0.9, -0.12], [1.02, -0.26, eo], [1.15, 0.0, eio], [2.4, -0.05]]); }
function sceneHook(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.04 * ss(seg(t, 0, 2.333)), 540, 1000);
  ubin(ctx, PAL.tealL);
  produk(ctx, 'keset', KS1.x, KS1.y, KS1.w, { rot: KS1.rot });
  // tetes 1: lepas 0,2 → mendarat C.hook_tetes; tetes 2: lepas 1,15 → C.hook_tetes_2
  [[0.2, C.hook_tetes, [580, 1010]], [1.15, C.hook_tetes_2, [470, 1110]]].forEach(([t0, t1, p], i) => {
    if (t >= t0 && t < t1) {
      const u = E_in(seg(t, t0, t1));
      tetes(ctx, lerp(BIBIR1[0], p[0], u), lerp(BIBIR1[1] + 40, p[1], u), 26, 1 + 0.25 * u);
    }
    if (t >= t1) {                                    // genangan menyusut = terserap
      const k = 1 - eio(seg(t, t1 + 0.05, t1 + 0.9));
      genangan(ctx, p[0], p[1], 84, k, 5 + i);
      percik(ctx, p[0], p[1] - 10, t, t1, 70);
    }
  });
  if (t < 0.2) {                                      // frame 0: tetes menggantung + jalur putus-putus ke keset
    tetes(ctx, BIBIR1[0], BIBIR1[1] + 40 + 6 * ss(seg(t, 0, 0.2)), 26, 1);
    dashed(ctx, spline([[BIBIR1[0], BIBIR1[1] + 90], [610, 840], [580, 960]], false, 8), 7, 20, 14, 0, PAL.ink);
  }
  if (t < 0.3) {                                      // kejanggalan disorot di frame 0: tetes dilingkari tinta merah
    const k = 1 - ss(seg(t, 0.2, 0.3));
    ink(ctx, ellipse(BIBIR1[0] + 4, BIBIR1[1] + 44, 62, 70, 40, -1.4, -1.4 + TAU * 0.96), 7, { color: PAL.coralD, seed: 15, alpha: k });
  }
  const a = gayungSudut1(t);
  gayung(ctx, BIBIR1[0] + 200, BIBIR1[1] - 50, a, 1.0);
  const pegang = [BIBIR1[0] + 200 + Math.cos(a) * 200, BIBIR1[1] - 50 + Math.sin(a) * 200];
  tanganDi(ctx, pegang, Math.PI * 0.95 + a, 'grip', 2.3, [W + 120, 140], -1);
  labelIlustrasi(ctx, 120, 1480 - 210);
  ctx.restore();
  // teks hook (thumbnail): "Keset ini" / "nyerap air?" di pelat mustard
  text(ctx, 'Keset ini', W / 2, 362, { font: "800 150px 'Barlow Condensed'", fill: PAL.ink, plate: PAL.white, off: [6, 6], align: 'center' });
  const s2 = "800 150px 'Barlow Condensed'", w2 = measure(ctx, 'nyerap air?', s2);
  const hk = 1 + 0.06 * Math.sin(Math.PI * seg(t, C.serap, C.serap + 0.25));
  ctx.save(); ctx.translate(W / 2, 500); ctx.scale(hk, hk);
  shape(ctx, rrect(-w2 / 2 - 22, -112, w2 + 44, 150, 16), { fill: PAL.mustard, line: 4, seed: 10, grain: 0.15, off: [6, 6] });
  text(ctx, 'nyerap air?', 0, 18, { font: s2, fill: PAL.ink, align: 'center' });
  ctx.restore();
}

// ------------------------------------------------------------ 2. MASALAH (2,333 – 5,0): kaki basah tergelincir di lantai
const LANTAI2 = 1000;
function kaki(ctx, ax, ay, rot, sx = 1, sy = 1) {      // betis dari atas layar ke pergelangan (ax, ay); telapak ke kanan
  ctx.save(); ctx.translate(ax, ay); ctx.rotate(rot);
  const betis = spline([[-92, -900], [92, -900], [96, -520], [70, -230], [50, -40], [-46, -30], [-74, -240], [-98, -540]], true, 7);
  shape(ctx, betis, { fill: PAL.skin, line: 4.4, seed: 200, grain: 0.25, shade: [{ pts: rect(30, -900, 80, 880), color: PAL.skinD, alpha: 0.45 }] });
  ctx.scale(sx, sy);
  shape(ctx, spline([[-50, -40], [40, -52], [150, -38], [205, -10], [200, 22], [-46, 26], [-62, -10]], true, 6), { fill: PAL.skin, line: 4.4, seed: 201, grain: 0.25 });
  [[178, -24], [196, -6], [204, 12]].forEach(([x, y], i) => shape(ctx, ellipse(x + 6, y, 13 - i * 2, 10 - i, 12), { fill: PAL.skin, line: 3, seed: 202 + i, grain: 0.2 }));
  ctx.restore();
}
function sceneMasalah(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, 2.333, 5.0)), 540, 1100);
  ctx.fillStyle = PAL.pink; ctx.fillRect(-300, -300, W + 600, LANTAI2 + 300);
  for (let x = -40; x < W + 200; x += 150) ink(ctx, [[x, -200], [x, LANTAI2]], 4, { color: PAL.white, seed: 210 + x, taper: false, breaks: 0.1 });
  for (let y = 60; y < LANTAI2; y += 150) ink(ctx, [[-200, y], [W + 200, y]], 4, { color: PAL.white, seed: 260 + y, taper: false, breaks: 0.1 });
  plane(ctx, rect(-300, LANTAI2, W + 600, H), PAL.paperD);
  ink(ctx, [[-300, LANTAI2], [W + 300, LANTAI2]], 5, { seed: 280, taper: false });
  // tirai mandi mustard bergaris di kiri + rel handuk di kanan
  shape(ctx, spline([[-40, 80], [200, 80], [220, 520], [190, 960], [-40, 960]], true, 6), { fill: PAL.mustard, line: 4.4, seed: 290, grain: 0.3 });
  for (let i = 0; i < 3; i++) ink(ctx, [[30 + i * 55, 120], [20 + i * 55, 930]], 6, { color: PAL.mustardD, seed: 291 + i, wob: 0.3 });
  ink(ctx, [[-60, 70], [300, 70]], 10, { seed: 296, taper: false });
  shape(ctx, rrect(720, 470, 280, 22, 10), { fill: PAL.chrome, line: 3.6, seed: 297 });
  shape(ctx, spline([[750, 490], [960, 490], [950, 760], [760, 770]], true, 5), { fill: PAL.white, line: 4, seed: 298, grain: 0.2 });
  for (let i = 0; i < 3; i++) ink(ctx, [[770, 710 + i * 18], [940, 710 + i * 18]], 4, { color: PAL.tealL, seed: 299 + i, taper: false });
  // genangan di lantai (perspektif samping: pipih)
  [[420, 1095, 160], [800, 1170, 120], [180, 1200, 100]].forEach(([x, y, r], i) => genangan(ctx, x, y, r, 1, 220 + i));
  // kaki: masuk dari kiri atas lewat busur, menapak di "basah", tergelincir di "licin?"
  const tMasuk = 2.333, tapak = C.kaki_basah, gel = C.licin;
  const ax = kf(t, [[tMasuk, -40], [tapak - 0.2, 330, eo], [tapak, 350], [gel, 350], [gel + 6 / FPS, 580, eo], [5.0, 586]]);
  const ay = kf(t, [[tMasuk, 720], [tapak - 0.45, 880, eo], [tapak - 4 / FPS, 850], [tapak, 1080, E_in], [5.0, 1080]]);
  const rot = kf(t, [[tMasuk, -0.25], [tapak, 0], [gel, 0], [gel + 6 / FPS, 0.24, eo], [5.0, 0.26]]);
  const [sx, sy] = squash(t, tapak, 0.06, 0.12);
  const getar = t > gel + 6 / FPS ? 3 * Math.sin(TAU * 3 * t) : 0;
  if (t >= tMasuk) kaki(ctx, ax + getar, ay, rot, sx, sy);
  percik(ctx, 440, 1090, t, tapak, 130);
  ctx.restore();
  teksKunci(ctx, t, KATA[7][0], 'Lantai licin?');
}

// ------------------------------------------------------------ 3. PRODUK (5,0 – 8,333): keset jatuh, genangan terserap
const KS3 = { x: 540, y: 1000, w: 820 };
const GEN3 = [[280, 860, 92], [820, 900, 84], [300, 1200, 100], [800, 1240, 90], [560, 700, 70]];
function sceneProduk(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.05 * ss(seg(t, C.keset_jatuh, 8.333)), 540, 1000);
  ubin(ctx, PAL.mustardL);
  GEN3.forEach(([x, y, r], i) => {
    const t0 = C.keset_jatuh + 0.12 + i * 4 / FPS;
    genangan(ctx, x, y, r, 1 - eio(seg(t, t0, t0 + 0.7)), 300 + i);
  });
  const y = kf(t, [[5.0, 330], [C.keset_jatuh, KS3.y, E_in]]);
  const [sx, sy] = squash(t, C.keset_jatuh);
  produk(ctx, 'keset', KS3.x, y, KS3.w * (t < C.keset_jatuh ? 1.12 : 1), { sx, sy, tinggi: t < C.keset_jatuh ? 60 : 18 });
  // "motif kucing": cincin tinta digambar mengelilingi kepala kucing + label
  if (t >= C.motif) {
    const u = eo(seg(t, C.motif, C.motif + 0.35));
    ink(ctx, ellipse(KS3.x - 230, KS3.y + 175, 150, 120, 60, -1.2, -1.2 + TAU * u), 7, { color: PAL.coralD, seed: 320 });
    const lk = pop(t, C.motif + 0.2, 0.28);
    if (lk > 0) pelat(ctx, 'motif kucing', 330, 1440 - 200, '600 52px Jost', { k: lk, rot: -0.04, seed: 330 });
  }
  ctx.restore();
  teksKunci(ctx, t, C.nama, 'Keset diatomite');
}

// ------------------------------------------------------------ 4. FITUR ① (8,333 – 11,167): air diserap, lantai tetap kering
const KS4 = { x: 470, y: 1010, w: 820, rot: 0.14 };
const BIBIR4 = [680, 620];
function sceneFitur1(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.04 * ss(seg(t, 8.333, 11.167)), 520, 1000);
  ubin(ctx, PAL.blueL, 170, 40);
  produk(ctx, 'keset', KS4.x, KS4.y, KS4.w, { rot: KS4.rot });
  const a = kf(t, [[8.333, -0.3], [8.36, -0.44, eo], [8.42, 0.02, eio], [9.2, 0.0], [9.6, -0.3, eio]]);
  [[8.4, C.tetes_1, [520, 960]], [8.7, C.tetes_2, [380, 1100]]].forEach(([t0, t1, p], i) => {
    if (t >= t0 && t < t1) { const u = E_in(seg(t, t0, t1)); tetes(ctx, lerp(BIBIR4[0], p[0], u), lerp(BIBIR4[1] + 40, p[1], u), 30, 1 + 0.25 * u); }
    if (t >= t1) { genangan(ctx, p[0], p[1], 96, 1 - eio(seg(t, t1 + 0.05, t1 + 0.85)), 400 + i); percik(ctx, p[0], p[1] - 10, t, t1, 80); }
  });
  gayung(ctx, BIBIR4[0] + 200, BIBIR4[1] - 50, a, 1.0);
  tanganDi(ctx, [BIBIR4[0] + 200 + Math.cos(a) * 200, BIBIR4[1] - 50 + Math.sin(a) * 200], Math.PI * 0.95 + a, 'grip', 2.3, [W + 120, 140], -1);
  // "kering": segel centang dicap di lantai kanan keset
  const sy = kf(t, [[9.75, -300], [C.kering - 4 / FPS, 1080, eo], [C.kering, 1180, E_in], [C.kering + 0.15, 1180], [10.9, -200, eo]]);
  if (t >= C.kering) {
    const [qx, qy] = squash(t, C.kering, 0.2, 0.2);
    ctx.save(); ctx.translate(900, 1210); ctx.scale(qx, qy);
    shape(ctx, ellipse(0, 0, 96, 96, 40), { fill: PAL.tealD, line: 5, seed: 410, grain: 0.3 });
    ink(ctx, [[-42, 2], [-10, 36], [46, -34]], 18, { seed: 411, taper: false, color: PAL.white });
    ctx.restore();
  }
  if (t > 9.75 && t < 10.9) {
    shape(ctx, rrect(900 - 70, sy - 40, 140, 70, 14), { fill: PAL.kraftD, line: 4, seed: 412, grain: 0.3 });
    shape(ctx, ellipse(900, sy + 40, 90, 22, 30), { fill: PAL.tealD, line: 4, seed: 413, grain: 0.2 });
    tanganDi(ctx, [900 + 20, sy - 60], Math.PI * 0.6, 'grip', 2.2, [900 + 420, sy - 700], -1);
  }
  labelIlustrasi(ctx, 110, 1480 - 210);
  ctx.restore();
  teksKunci(ctx, t, 8.42, 'Cepat kering');
}

// ------------------------------------------------------------ 5. FITUR ② (11,167 – 14,0): sisi bawah anti-slip, didorong tidak geser
const KS5 = { x: 540, y: 1000, w: 820 };
function sceneFitur2(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, 11.167, 14.0)), 540, 1000);
  ctx.fillStyle = PAL.avocadoL; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (let i = 0; i < 7; i++) ink(ctx, [[-200, 640 + i * 150], [W + 200, 600 + i * 150]], 4, { color: PAL.avocado, seed: 500 + i, taper: false, breaks: 0.2 });
  // membalik di "Alasnya": skalaY cos(π u), sisi bawah terlihat 0,6 s, lalu balik lagi
  const b1 = seg(t, C.balik, C.balik + 8 / FPS), b2 = seg(t, 11.95, 11.95 + 8 / FPS);
  const fase = b2 > 0 ? 1 + eio(b2) : eio(b1);
  const sY = Math.cos(Math.PI * fase), bawah = sY < 0;
  // dorong: tangan mundur 30 px (4 frame) lalu dorong; keset bergeser 6 px dan kembali; tangan terpental di "geser."
  const geser = t < C.dorong ? 0 : 6 * Math.exp(-(t - C.dorong) * 6) * Math.cos((t - C.dorong) * 30);
  const [qx, qy] = t >= C.dorong ? squash(t, C.dorong, 0.03, 0.03) : [1, 1];
  produk(ctx, 'keset_abu', KS5.x - geser, KS5.y, KS5.w, { sx: qx, sy: Math.abs(sY) * qy, bawah });
  if (bawah && Math.abs(sY) > 0.2) labelIlustrasi(ctx, 120, 1480 - 210);
  if (t > 12.0) {
    const tx = kf(t, [[12.0, 1400], [C.dorong - 4 / FPS, 1015, eo], [C.dorong - 0.01, 1045, eio], [C.dorong, 975, E_in], [C.pental - 2 / FPS, 975],
      [C.pental + 0.2, 1060, eo], [13.6, 1500, eio]]);
    tanganDi(ctx, [tx, 1000], Math.PI, 'flat', 3.2, [tx + 560, 1240], -1);
  }
  ctx.restore();
  teksKunci(ctx, t, C.balik, 'Anti-slip');
}

// ------------------------------------------------------------ 6. BUKTI (14,0 – 16,5): cap "10RB+ terjual/bulan" + segel rating
const KS6 = { x: 540, y: 1150, w: 640 };
const KARTU6 = { x: 540, y: 560, w: 700, h: 300 };
function stempelY(t) {
  return kf(t, [[14.2, -400], [14.62, 360, eo], [C.cap - 5 / FPS, 300, eo], [C.cap, 455, E_in], [C.cap + 0.18, 455], [15.4, -500, eo]]);
}
function sceneBukti(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, 14.0, 16.5)), 540, 900);
  ctx.fillStyle = PAL.paper; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (let i = 0; i < 9; i++) ink(ctx, [[-200, 300 + i * 170], [W + 200, 290 + i * 170]], 3, { color: PAL.paperD, seed: 600 + i, taper: false });
  produk(ctx, 'keset', KS6.x, KS6.y, KS6.w, { rot: 0.05 });
  shape(ctx, rrect(KARTU6.x - KARTU6.w / 2, KARTU6.y - KARTU6.h / 2, KARTU6.w, KARTU6.h, 18), { fill: PAL.white, line: 4.4, seed: 610, grain: 0.12, off: [6, 6] });
  if (t >= C.cap) {
    const [qx, qy] = squash(t, C.cap, 0.08, 0.08);
    ctx.save(); ctx.translate(KARTU6.x, KARTU6.y); ctx.rotate(-0.05); ctx.scale(qx, qy);
    ink(ctx, rrect(-300, -118, 600, 236, 16), 6, { closed: true, color: PAL.coralD, seed: 620, breaks: 0.15 });
    text(ctx, '10RB+', 0, 22, { font: "800 150px 'Barlow Condensed'", fill: PAL.coralD, align: 'center' });
    text(ctx, 'terjual / bulan', 0, 92, { font: '600 52px Jost', fill: PAL.coralD, align: 'center' });
    ctx.restore();
  }
  // segel rating di "lebih."
  const sk = pop(t, C.segel, 0.3);
  if (sk > 0) {
    ctx.save(); ctx.translate(840, 860); ctx.scale(sk, sk); ctx.rotate(0.08);
    star(ctx, 0, 0, 170, { n: 18, inner: 0.86, fill: PAL.white, off: [0, 0] });
    shape(ctx, ellipse(0, 0, 136, 136, 48), { fill: PAL.tealD, line: 5, seed: 630, grain: 0.3 });
    star(ctx, -58, -32, 26, { n: 5, inner: 0.45, fill: PAL.mustard, off: [0, 0] });
    text(ctx, '4,89', 22, -10, { font: '64px Slab', fill: PAL.white, align: 'center' });
    text(ctx, '9,5rb+', 0, 56, { font: '600 40px Jost', fill: PAL.white, align: 'center' });
    text(ctx, 'ulasan', 0, 98, { font: '600 34px Jost', fill: PAL.white, align: 'center' });
    ctx.restore();
  }
  // tangan + cap karet (antisipasi naik, hentak, tekan, angkat)
  const yb = stempelY(t);
  if (t > 14.2 && t < 15.4) {
    const [sx, sy] = t >= C.cap ? squash(t, C.cap, 0.15, 0.2) : (t > C.cap - 2 / FPS ? [0.9, 1.15] : [1, 1]);
    ctx.save(); ctx.translate(KARTU6.x, yb); ctx.scale(sx, sy);
    shape(ctx, rrect(-260, -24, 520, 24, 6), { fill: PAL.coral, line: 3.6, seed: 640, grain: 0.2 });
    shape(ctx, rrect(-250, -112, 500, 92, 14), { fill: PAL.kraftD, line: 4.6, seed: 641, grain: 0.35, shade: [{ pts: rect(150, -120, 120, 110), color: PAL.brown, alpha: 0.5 }] });
    shape(ctx, rrect(-34, -236, 68, 130, 12), { fill: PAL.brownL, line: 4, seed: 642, grain: 0.3 });
    shape(ctx, ellipse(0, -270, 62, 52, 36), { fill: PAL.kraft, line: 4.4, seed: 643, grain: 0.3 });
    ctx.restore();
    tanganDi(ctx, [KARTU6.x + 34, yb - 290], Math.PI * 0.62, 'grip', 2.4, [KARTU6.x + 420, yb - 900], -1);
  }
  ctx.restore();
}

// ------------------------------------------------------------ 7. CTA (16,5 – 18,72): motif lain + tunjuk ke link
const MOTIF7 = [['motif_pink', 200, 1190, 300, -0.12], ['motif_panda', 880, 1200, 290, 0.1], ['motif_anjing', 880, 560, 260, 0.08]];
function sceneCta(ctx, t) {
  ctx.fillStyle = PAL.paper; ctx.fillRect(-300, -300, W + 600, H + 600);
  ctx.save(); cam(ctx, 1 + 0.02 * ss(seg(t, 16.5, 18.72)), 540, 960);
  rays(ctx, 540, 900, 30, 1500, PAL.mustardL, { alpha: 0.55 });
  MOTIF7.forEach(([n, x, y, w, r], i) => { const k = pop(t, C.motif_pop + i * 4 / FPS, 0.3); if (k > 0) produk(ctx, n, x, y, w * k, { rot: r }); });
  const nk = 1 + 0.05 * Math.sin(Math.PI * seg(t, C.motif_pop, C.motif_pop + 0.3));
  produk(ctx, 'keset', 480, 880, 830 * nk, { rot: -0.06 });
  const ck = pop(t, C.cek, 0.3), lp = 1 + 0.07 * Math.sin(Math.PI * seg(t, C.link, C.link + 0.3));
  if (ck > 0) pelat(ctx, 'Cek motif di link', W / 2, 360, '86px Slab', { k: ck * lp, rot: -0.02, seed: 700, fill: PAL.mustard });
  // tangan menunjuk ke bawah (ke tempat link) lewat busur, tiba di "link"
  const m = eio(seg(t, C.cek, C.link));
  const enter = eo(seg(t, 16.6, 17.1));
  const tip = [lerp(980, 860, m) + 60 * Math.sin(Math.PI * m) + 400 * (1 - enter), lerp(900, 1180, m) + 6 * Math.sin(TAU * 0.8 * t)];
  tanganDi(ctx, tip, Math.PI * 0.5 + 0.25 * (1 - m), 'point', 2.2, [tip[0] + 360, tip[1] - 520], -1);
  ctx.restore();
}

// ------------------------------------------------------------ transisi + potong
function irisMasuk(ctx, cx, cy, p, gambarBerikut) {
  const r = 2300 * p;
  ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, TAU); ctx.clip(); gambarBerikut(); ctx.restore();
  if (r > 0 && r < 2300) ink(ctx, ellipse(cx, cy, r, r, 80), 6, { closed: true, seed: 990 });
}
function wipe(ctx, p, dari, gambarBerikut) {
  ctx.save(); ctx.beginPath();
  if (dari === 'bawah') ctx.rect(0, H * (1 - p), W, H * p); else if (dari === 'atas') ctx.rect(0, 0, W, H * p); else ctx.rect(0, 0, W * p, H);
  ctx.clip(); gambarBerikut(); ctx.restore();
  const tepi = dari === 'bawah' ? [[0, H * (1 - p)], [W, H * (1 - p)]] : dari === 'atas' ? [[0, H * p], [W, H * p]] : [[W * p, 0], [W * p, H]];
  if (p > 0 && p < 1) ink(ctx, tepi, 6, { seed: 991, taper: false });
}
function renderSemua(ctx, t) {
  setClock(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (t < 2.333) sceneHook(ctx, t);
  else if (t < 5.0) sceneMasalah(ctx, t);
  else if (t < 8.333) { sceneProduk(ctx, t); if (t >= 8.0) wipe(ctx, eio(seg(t, 8.0, 8.333)), 'bawah', () => sceneFitur1(ctx, t)); }
  else if (t < 11.167) { sceneFitur1(ctx, t); if (t >= 10.833) wipe(ctx, eio(seg(t, 10.833, 11.167)), 'kiri', () => sceneFitur2(ctx, t)); }
  else if (t < 14.0) { sceneFitur2(ctx, t); if (t >= 13.65) wipe(ctx, eio(seg(t, 13.65, 14.0)), 'atas', () => sceneBukti(ctx, t)); }
  else if (t < 16.5) { sceneBukti(ctx, t); if (t >= 16.1) irisMasuk(ctx, KS6.x, KS6.y, eio(seg(t, 16.1, 16.5)), () => sceneCta(ctx, t)); }
  else sceneCta(ctx, t);
  caption(ctx, t);
  disclosure(ctx);
  paperFinish(ctx, W, H, 1);
}
export function renderFilm(ctx, t) {
  if (t >= LOOP_END) { renderSemua(ctx, 0); return; }
  renderSemua(ctx, t);
  if (t >= LOOP_AT) {                                   // end card membuka iris ke frame pembuka, jadi loop menyambung
    const p = eio(seg(t, LOOP_AT, LOOP_END));
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.beginPath(); ctx.arc(540, 960, 2300 * p, 0, TAU); ctx.clip();
    renderSemua(ctx, 0); ctx.restore();
    setClock(t);
    if (p > 0 && p < 1) ink(ctx, ellipse(540, 960, 2300 * p, 2300 * p, 80), 6, { closed: true, seed: 992 });
  }
}
