// Affiliate — Mini Kipas Turbo Genggam LED 23000 RPM (Shopee 41671303438). Disutradarai per produk (aff_studio ADR-P06, series/BIBLE.md).
// Gaya midcentury-toon (kit Slate `midcentury` + kit affiliate engine/aff.js). 1080x1920, 24 fps. Murni fungsi t.
// Timing: vo.json job 2026-10-20-bd860a, onset dikoreksi (kata_koreksi.json, tools/sunyi.py).
// Cerita: penumpang KRL yang gerah (June dari kit) — jendela gerbong → gerbong padat → tote bag → pintu (tes tisu) →
// kursi (layar LED) → papan info stasiun (cap bukti) → end card 10 warna.
import { PAL, setClock, shape, plane, ink, rays, ellipse, rect, rrect, spline, star, text, measure, xform,
  paperFinish, dashed, lerp, seg, ss, eo, eio, hash, TAU } from './engine/toon.js';
import { drawOwner, armJoints, toScreen, NAVY, NAVYD } from './engine/chars.js';
import { pop, E_in, kf, squash, cam, muatFoto, produk, tanganDi, pelat, teksKunci, labelIlustrasi, disclosure,
  buatCaption, capKaret, cetakCap, segelRating, irisMasuk, wipe, denganLoop } from './engine/aff.js';
import { FOTO } from './aset/foto.js';

// konstanta lokal: CUES dan META tidak boleh bergantung pada impor (audit_film mengganti impor dengan stub)
const W = 1080, H = 1920, FPS = 24;
const KATA = [[0.0, 0.32, 'Kipas'], [0.347, 0.64, 'sekecil'], [0.72, 1.2, 'ini,'], [1.24, 1.6, 'anginnya'], [1.64, 2.0, 'sekencang'],
  [2.08, 2.52, 'ini?'], [3.08, 3.65, 'Desak-desakan'], [3.677, 3.73, 'di'], [3.77, 4.37, 'kereta,'], [4.43, 4.69, 'gerah'],
  [4.75, 5.24, 'banget?'], [5.83, 6.29, 'Nah…'], [6.64, 6.71, 'ini'], [6.79, 7.19, 'dia,'], [7.23, 7.51, 'kipas'],
  [7.577, 7.91, 'turbo'], [7.95, 8.55, 'genggam.'], [9.12, 9.47, 'Motornya'], [9.53, 9.71, 'dua'], [9.75, 9.95, 'puluh'],
  [9.99, 10.11, 'tiga'], [10.19, 10.79, 'ribu'], [10.88, 11.39, 'RPM.'], [11.96, 12.077, 'Enam'], [12.157, 12.717, 'level,'],
  [12.757, 13.197, 'angkanya'], [13.257, 13.517, 'muncul'], [13.57, 13.677, 'di'], [13.717, 14.077, 'layar.'],
  [14.157, 14.817, 'Udah'], [14.877, 15.297, 'terjual'], [15.357, 15.617, 'sepuluh'], [15.677, 16.057, 'ribu'],
  [16.09, 16.4, 'lebih.'], [16.98, 17.107, 'Ada'], [17.147, 17.507, 'sepuluh'], [17.539, 17.907, 'warna,'], [17.947, 18.147, 'cek'],
  [18.174, 18.227, 'di'], [18.275, 18.467, 'link'], [18.547, 18.867, 'ya.']];

// setiap hentakan/pendaratan: [id, frame, indeks kata]; frame = round(onset × 24) dari KATA
const CUE_LIST = [['kencang', 39, 4], ['desak', 74, 6], ['gerah', 106, 9], ['nah', 140, 11], ['kipas', 174, 14],
  ['motor', 219, 17], ['rpm', 261, 22], ['enam', 287, 23], ['layar', 329, 28], ['cap', 369, 31], ['segel', 386, 33],
  ['warna', 412, 35], ['cek', 431, 37], ['link', 439, 39]];
// tanpa kata: tekan tombol di hook (frame 5) dan tekan tombol di celah sunyi 6,30–6,64 setelah "Nah…" (QA render 2: di kata "ini" +111 ms)
export const CUES = [{ id: 'nyala', t: 5 / FPS }, { id: 'ini', t: 153 / FPS }]
  .concat(CUE_LIST.map(([id, f, k]) => ({ id, t: f / FPS, kata: k, teks: KATA[k][2] })));
const C = {}; CUES.forEach(c => { C[c.id] = c.t; });

export const META = {
  dur: 19.18,                               // 18,88 + 0,3
  kontras: [['#2B2420', '#FBF6EA'], ['#2B2420', '#F4EAD5'], ['#2B2420', '#E8B43A'], ['#B8452B', '#FBF6EA'], ['#FBF6EA', '#257A74'],
    ['#2B2420', '#F3D37F']],
};
const LOOP_AT = 18.91, LOOP_END = 19.14;    // iris ke frame 0
// batas adegan (potongan di jendela sunyi VO)
const T2 = 2.75, T3 = 137 / FPS, T4 = 8.875, T5 = 281 / FPS, T6 = 14.5, T7 = 16.75;

await muatFoto(FOTO);

// ------------------------------------------------------------ caption: [kata awal, kata akhir, kata disorot]
// "dua puluh tiga ribu" (kata 18–21) tampil sebagai satu token "23.000"; angka lain sebagai digit
const GABUNG = { 18: [21, '23.000'] };
const KATA_CAP = [], IDX = [];
for (let i = 0; i < KATA.length; i++) {
  IDX[i] = KATA_CAP.length;
  if (GABUNG[i]) { const [j, s] = GABUNG[i]; KATA_CAP.push([KATA[i][0], KATA[j][1], s]); for (let q = i + 1; q <= j; q++) IDX[q] = IDX[i]; i = j; }
  else KATA_CAP.push(KATA[i]);
}
const CAP = [[0, 5, 4], [6, 10, 9], [11, 16, 15], [17, 22, 22], [23, 28, 28], [29, 33, 32], [34, 40, 39]].map(c => c.map(i => IDX[i]));
const DIGIT = { [IDX[23]]: '6', [IDX[31]]: '10', [IDX[35]]: '10' };
const caption = buatCaption(KATA_CAP, CAP, { digit: DIGIT, dur: META.dur });

// ------------------------------------------------------------ titik di cutout kipas (px di cutout/kipas.png 292×475)
const KP = { w: 292, h: 475 }, RING = [103, 111], RING_R = 76, LAYAR = [95, 250], TOMBOL = [93, 300], GAGANG = [106, 360];
function titik(k, p) {
  const s = k.w / KP.w, dx = (p[0] - KP.w / 2) * s, dy = (p[1] - KP.h / 2) * s, c = Math.cos(k.rot || 0), si = Math.sin(k.rot || 0);
  return [k.x + c * dx - si * dy, k.y + si * dx + c * dy];
}
const kedip = t => ((t % 2.9) < 0.1 ? 1 : 0);

// ------------------------------------------------------------ helper khusus video ini
// jendela gerbong: langit, matahari datar (opsional), gedung dua lapis yang bergeser (kereta jalan)
function jendela(ctx, x, y, w, h, t, o = {}) {
  shape(ctx, rrect(x - 22, y - 22, w + 44, h + 44, 34), { fill: o.kusen ?? PAL.white, line: 4.4, seed: 1400 + (x | 0), grain: 0.2 });
  const R = rrect(x, y, w, h, 22);
  ctx.save(); ctx.beginPath(); R.forEach(([a, b], i) => (i ? ctx.lineTo(a, b) : ctx.moveTo(a, b))); ctx.closePath(); ctx.clip();
  ctx.fillStyle = PAL.blueL; ctx.fillRect(x, y, w, h);
  if (o.matahari) shape(ctx, ellipse(x + w * 0.74, y + h * 0.27, 56, 56, 30), { fill: PAL.mustard, line: 4, seed: 1410, grain: 0.2 });
  const geser = t * (o.v ?? 40), P = w + 420;
  [[PAL.blue, 0.45, 0.5, 20, 0], [PAL.blueD, 1, 0.34, 40, 3]].forEach(([warna, v, hmax, sd, garis]) => {
    for (let i = 0; i < 9; i++) {
      const bw = 70 + 80 * hash(i, sd), bh = h * (0.14 + hmax * hash(i, sd + 1));
      const bx = x - 210 + ((((i * 157 + sd * 7) - geser * v) % P) + P) % P;
      shape(ctx, rect(bx, y + h - bh, bw, bh + 12), { fill: warna, line: garis, seed: sd + i, grain: 0.2, off: [0, 0] });
      if (garis) for (let r = 0; r < 3; r++) shape(ctx, rect(bx + 14, y + h - bh + 20 + r * 34, bw - 28, 12), { fill: PAL.blueL, line: 0, grain: 0, off: [0, 0] });
    }
  });
  ctx.restore();
  ink(ctx, R, 5, { closed: true, seed: 1420 + (x | 0) });
}
// potongan jalur (a..b dari 0..1)
function potong(P, a, b) { const n = P.length - 1; return P.slice(Math.max(0, Math.floor(a * n)), Math.min(n, Math.ceil(b * n)) + 1); }
// garis angin: arus bergulung dari mulut kipas (demo, berlabel ilustrasi); k 0..1 = kekuatan angin
function angin(ctx, dari, ke, t, k, o = {}) {
  if (k <= 0.02) return;
  const n = o.n ?? 4, lebar = o.lebar ?? 200, cepat = o.cepat ?? 1.5;
  const dx = ke[0] - dari[0], dy = ke[1] - dari[1], L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L;
  for (let i = 0; i < n; i++) {
    const f = n === 1 ? 0 : i / (n - 1) - 0.5, ombak = 46 * Math.sin(i * 2.1 + 1);
    const s0 = [dari[0] + nx * f * lebar * 0.3, dari[1] + ny * f * lebar * 0.3], s1 = [ke[0] + nx * f * lebar, ke[1] + ny * f * lebar];
    const P = spline([s0, [lerp(s0[0], s1[0], 0.35) + nx * ombak, lerp(s0[1], s1[1], 0.35) + ny * ombak],
      [lerp(s0[0], s1[0], 0.7) - nx * ombak, lerp(s0[1], s1[1], 0.7) - ny * ombak], s1], false, 12);
    const u = (((t * cepat * (0.7 + 0.6 * k) + i * 0.29) % 1) + 1) % 1, a = Math.max(0, u - 0.32 - 0.3 * k), b = Math.min(1, u + 0.06);
    if (b - a < 0.04) continue;
    const S = potong(P, a, b), lw = 0.6 + 0.4 * k;
    ink(ctx, S, 22 * lw, { color: PAL.ink, seed: 500 + i, wob: 0.15 });
    ink(ctx, S, 12 * lw, { color: PAL.white, seed: 510 + i, wob: 0.15 });
    const [hx, hy] = S[S.length - 1], [px, py] = S[Math.max(0, S.length - 3)], a0 = Math.atan2(hy - py, hx - px);
    if (b < 0.97) {
      const gl = ellipse(hx + Math.cos(a0 + 1.57) * 20, hy + Math.sin(a0 + 1.57) * 20, 20, 20, 16, a0 - 1.57, a0 + 2.8);
      ink(ctx, gl, 20 * lw, { color: PAL.ink, seed: 520 + i }); ink(ctx, gl, 10 * lw, { color: PAL.white, seed: 530 + i });
    }
  }
}
// helai rambut: dari akar (rx, ry) ke sudut a, panjang len
function helai(ctx, rx, ry, a, len, lebar, seed, bend = 0.18, warna = PAL.hair) {
  const tx = rx + Math.cos(a) * len, ty = ry + Math.sin(a) * len, nx = -Math.sin(a), ny = Math.cos(a);
  const mx = (rx + tx) / 2 + nx * len * bend, my = (ry + ty) / 2 + ny * len * bend;
  shape(ctx, spline([[rx - nx * lebar / 2, ry - ny * lebar / 2], [mx - nx * lebar * 0.3, my - ny * lebar * 0.3], [tx, ty],
    [mx + nx * lebar * 0.3, my + ny * lebar * 0.3], [rx + nx * lebar / 2, ry + ny * lebar / 2]], true, 5), { fill: warna, line: 0, seed, grain: 0.3, off: [0, 0] });
}
// tetes (keringat): ujung di atas
function tetes(ctx, x, y, r, rot = 0) {
  shape(ctx, xform(spline([[0, -1.9], [0.62, -0.55], [1, 0.3], [0.7, 0.9], [0, 1.1], [-0.7, 0.9], [-1, 0.3], [-0.62, -0.55]], true, 6), x, y, rot, r),
    { fill: PAL.blueL, line: 3.4, seed: 61, grain: 0.1, breaks: 0 });
  ink(ctx, ellipse(x - r * 0.35, y + r * 0.05, r * 0.2, r * 0.36, 10), 3, { color: PAL.white, seed: 62 });
}
// pita kertas/kain yang ditiup: akar (x, y), sudut menggantung → mendatar sesuai angin k, ombak berjalan
function pita(ctx, x, y, k, t, o = {}) {
  const L = o.L ?? 330, lb = o.lebar ?? 80, phi = lerp(Math.PI / 2 - 0.05, Math.PI + (o.angkat ?? -0.04), k), A = (o.A ?? 30) * k;
  const c = Math.cos(phi), s = Math.sin(phi), nx = -s, ny = c, kiri = [], kanan = [];
  for (let i = 0; i <= 16; i++) {
    const u = i / 16, w = lb * (1 - 0.15 * u) / 2;
    const off = A * u * Math.sin(TAU * (1.6 * u - (o.hz ?? 5) * t)) + 7 * u * Math.sin(TAU * 0.7 * t), cx = x + c * L * u + nx * off, cy = y + s * L * u + ny * off;
    kiri.push([cx - nx * w, cy - ny * w]); kanan.push([cx + nx * w, cy + ny * w]);
  }
  shape(ctx, [...kiri, ...kanan.reverse()], { fill: o.warna ?? PAL.white, line: 3.6, seed: o.seed ?? 1600, grain: 0.15, breaks: 0.05 });
  if (o.lipat !== false) ink(ctx, potong(kiri.map((p, i) => [(p[0] + kanan[16 - i][0]) / 2, (p[1] + kanan[16 - i][1]) / 2]), 0.1, 0.8), 2.4, { color: PAL.paperDD, seed: (o.seed ?? 1600) + 1 });
}
// ibu jari (kapsul kulit) dari pangkal ke ujung
function jempol(ctx, pangkal, ujung, k = 1) {
  ink(ctx, [pangkal, ujung], 34 * k, { color: PAL.ink, seed: 1300, taper: false, wob: 0.05 });
  ink(ctx, [pangkal, ujung], 25 * k, { color: PAL.skin, seed: 1301, taper: false, wob: 0.05 });
  const a = Math.atan2(ujung[1] - pangkal[1], ujung[0] - pangkal[0]);
  shape(ctx, ellipse(ujung[0] - Math.cos(a) * 7 * k, ujung[1] - Math.sin(a) * 7 * k, 7 * k, 5.5 * k, 12, 0, TAU, a), { fill: PAL.pink, line: 2.2, seed: 1302, grain: 0 });
}
// gerak tekan jempol: antisipasi naik 14 px (4 frame), tekan 8 px (1 frame), lepas 5 frame
function tekan(t, P) {
  for (const p of P) if (t >= p - 5 / FPS && t < p + 7 / FPS) return kf(t, [[p - 5 / FPS, 0], [p - 1 / FPS, -14, eo], [p, 8, E_in], [p + 2 / FPS, 8], [p + 7 / FPS, 0, eo]]);
  return 0;
}
// kipas di tangan: produk + tangan menggenggam gagang (jari menutupi gagang) + jempol di tombol
function kipasDiTangan(ctx, k, t, o) {
  produk(ctx, 'kipas', k.x, k.y, k.w, { rot: k.rot || 0, sx: o.sx, sy: o.sy, cahaya: o.cahaya, asli: o.asli, tinggi: o.tinggi });
  const s = k.w / KP.w, g = titik(k, GAGANG), b = titik(k, TOMBOL), arah = o.kanan === false ? 0 : Math.PI;
  const uj = [g[0] + (arah ? -18 : 18) * s, g[1] + 20 * s];
  tanganDi(ctx, uj, arah + (k.rot || 0), 'grip', 2.1 * s, o.dari, arah ? -1 : 1);
  const d = tekan(t, o.tekan || []), lepas = arah ? [0.62, -0.78] : [-0.62, -0.78];
  const pangkal = [g[0] + (arah ? 52 : -52) * s, g[1] - 4 * s];
  jempol(ctx, pangkal, [b[0] - lepas[0] * d * -1 + (arah ? 6 : -6) * s, b[1] + lepas[1] * -d], s * 0.9);
}

// ------------------------------------------------------------ June close-up (kepala + bahu); angin dari kanan
// w 0..1 kekuatan angin, lega 0..1 (mata terpejam, senyum), lepas 0..1 (butir keringat terlempar)
function juneDekat(ctx, x, y, s, t, w, lega, lepas) {
  const fl = i => 0.24 * w * Math.sin(TAU * 4 * t + i * 1.7);
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  shape(ctx, spline([[-330, 760], [-300, 360], [-210, 262], [-70, 228], [70, 228], [210, 262], [300, 360], [330, 760]], true, 6),
    { fill: PAL.coral, line: 4.4, seed: 1200, grain: 0.35, shade: [{ pts: rect(130, 200, 260, 600), color: PAL.coralD, alpha: 0.45 }] });
  ink(ctx, [[175, 250], [275, 760]], 40, { seed: 1201, taper: false, wob: 0.05 });
  ink(ctx, [[175, 250], [275, 760]], 30, { seed: 1202, taper: false, wob: 0.05, color: PAL.mustard });
  shape(ctx, rrect(-44, 90, 88, 150, 22), { fill: PAL.skin, line: 4, seed: 1203, grain: 0.2, shade: [{ pts: rect(-50, 90, 110, 50), color: PAL.skinD, alpha: 0.55 }] });
  shape(ctx, rrect(-76, 196, 152, 60, 24), { fill: PAL.coral, line: 4, seed: 1204, grain: 0.3 });
  for (let i = 0; i < 2; i++) ink(ctx, [[-62, 214 + i * 18], [62, 214 + i * 18]], 3, { color: PAL.coralD, seed: 1205 + i, taper: false });
  // rambut belakang (bob), terdorong ke kiri
  shape(ctx, spline([[10, -196], [-130, -172], [-190 - 40 * w, -70], [-205 - 90 * w, 40 + 10 * w], [-170 - 80 * w, 128 - 20 * w], [-70, 96], [70, 96],
    [150, 120 - 40 * w], [182 - 20 * w, 30], [168 - 20 * w, -100], [120, -170]], true, 7), { fill: PAL.hair, line: 0, seed: 1206, grain: 0.3, off: [0, 0] });
  [[-150, -60], [-168, 0], [-170, 60], [-150, 112]].forEach(([rx, ry], i) =>
    helai(ctx, rx - 20 * w, ry, lerp(1.75, 3.2 - 0.12 * i, w) + fl(i), lerp(70, 160, w) - 10 * i, 46, 1210 + i));
  // kepala + wajah
  shape(ctx, ellipse(0, 0, 118, 140, 40), { fill: PAL.skin, line: 4.4, seed: 1220, grain: 0.15, breaks: 0.2 });
  const mata = lega > 0.5;
  [[-46, 12], [46, 12]].forEach(([ex, ey], i) => {
    if (mata) ink(ctx, spline([[ex - 18, ey + 4], [ex, ey - 9], [ex + 18, ey + 4]], false, 5), 6, { seed: 1270 + i, taper: false });
    else {
      shape(ctx, ellipse(ex, ey + 4, 9, 13, 14), { fill: PAL.ink, line: 0, grain: 0, off: [0, 0] });
      shape(ctx, rect(ex - 16, ey - 16, 32, 14), { fill: PAL.skin, line: 0, grain: 0, off: [0, 0] });
      ink(ctx, [[ex - 15, ey - 2], [ex + 15, ey - 2]], 4.4, { seed: 1272 + i, taper: false });
    }
    ink(ctx, mata ? spline([[ex - 18, ey - 34], [ex, ey - 42], [ex + 18, ey - 34]], false, 4)
      : (i ? [[ex - 18, ey - 40], [ex + 18, ey - 30]] : [[ex - 18, ey - 30], [ex + 18, ey - 40]]), 5, { seed: 1274 + i });
  });
  ink(ctx, spline([[4, 22], [-7, 52], [8, 56]], false, 4), 4, { seed: 1280 });
  if (mata) shape(ctx, spline([[-32, 82], [32, 82], [16, 106], [-16, 106]], true, 5), { fill: PAL.coralD, line: 3.4, seed: 1281, grain: 0, breaks: 0 });
  else shape(ctx, ellipse(0, 94, 13, 10, 16), { fill: PAL.coralD, line: 3.2, seed: 1282, grain: 0, breaks: 0 });
  [[-72, 60], [72, 60]].forEach(([cx, cy], i) => shape(ctx, ellipse(cx, cy, 20, 12, 14), { fill: mata ? PAL.pink : PAL.coralL, line: 0, grain: 0, seed: 1283 + i, alpha: 0.9 }));
  // tudung rambut depan + poni (tertiup ke kiri atas) + bando
  shape(ctx, spline([[-128, 20], [-130, -70], [-98, -142], [-30, -170], [40, -168], [100, -140], [130, -70], [128, 20], [112, -30], [76, -92], [0, -106],
    [-76, -92], [-112, -30]], true, 6), { fill: PAL.hair, line: 0, seed: 1230, grain: 0.3 });
  for (let i = 0; i < 5; i++) helai(ctx, -72 + 36 * i, -100 + 6 * Math.abs(i - 2), lerp(1.62, 3.3, w) + fl(i + 4) * 0.8, lerp(70, 112, w), 44, 1240 + i, 0.15);
  ink(ctx, ellipse(0, -30, 138, 150, 30, Math.PI + 0.35, TAU - 0.35), 16, { color: PAL.mustard, seed: 1250, taper: false });
  [[128, -30], [132, 40]].forEach(([rx, ry], i) => helai(ctx, rx, ry, lerp(1.45, 2.3, w) + fl(i + 9) * 0.5, lerp(80, 60, w), 40, 1260 + i));
  // butir keringat (terlempar ke kiri waktu turbo)
  [[-80, -60], [92, -42], [104, 34]].forEach(([dx, dy], i) => {
    const u = eo(Math.min(1, lepas * (1 + 0.15 * i)));
    if (u >= 1) return;
    tetes(ctx, dx - (260 + 70 * i) * u, dy - 30 * i * u + 60 * u * u, 15 * (1 - 0.5 * u), -0.9 * u);
  });
  ctx.restore();
}

// ------------------------------------------------------------ 1. HOOK (0 – 2,75): angin kipas meniup poni June di jendela KRL
const KH = { x: 770, y: 1000, w: 330, rot: 0.04 };
const anginHook = t => kf(t, [[0, 0.5], [C.nyala, 0.5], [C.nyala + 6 / FPS, 0.7, eo], [C.kencang - 2 / FPS, 0.72], [C.kencang + 3 / FPS, 1.0, eo]]);
function sceneHook(ctx, t) {
  const w = anginHook(t);
  ctx.save(); cam(ctx, 1 + 0.04 * ss(seg(t, 0, T2)), 540, 1000);
  ctx.fillStyle = PAL.paperD; ctx.fillRect(-300, -300, W + 600, H + 600);
  ink(ctx, [[-300, 560], [W + 300, 560]], 4, { seed: 1100, taper: false, color: PAL.paperDD });
  jendela(ctx, 70, 620, 940, 900, t, { v: 70 });
  // angin di belakang June: terlihat antara kipas dan wajah, lalu keluar lagi di kiri kepala (wajah tetap bersih)
  const r = titik(KH, RING);
  angin(ctx, [r[0] - 40, r[1] + 10], [-20, 820], t, w, { n: 5, lebar: 420 });
  juneDekat(ctx, 320, 960, 1.2, t, w, ss(seg(t, C.kencang, C.kencang + 0.2)), seg(t, C.kencang, C.kencang + 10 / FPS));
  kipasDiTangan(ctx, KH, t, { cahaya: PAL.blueL, dari: [960, 1780], tekan: [C.nyala] });
  if (t < 0.95) {                                    // frame 0: kipas kecil dilingkari tinta merah
    const k = 1 - ss(seg(t, 0.75, 0.95));
    ink(ctx, ellipse(KH.x + 4, KH.y + 10, 215, 320, 50, -1.3, -1.3 + TAU * 0.95), 8, { color: PAL.coralD, seed: 15, alpha: k });
  }
  labelIlustrasi(ctx, 80, 1470 - 230);
  ctx.restore();
  const F1 = "800 150px 'Barlow Condensed'";
  text(ctx, 'Kipas kecil,', 520, 330, { font: F1, fill: PAL.ink, plate: PAL.white, off: [6, 6], align: 'center', maxW: 800 });
  const w2 = Math.min(measure(ctx, 'angin kencang?', F1), 780), hk = 1 + 0.06 * Math.sin(Math.PI * seg(t, C.kencang, C.kencang + 0.25));
  ctx.save(); ctx.translate(520, 486); ctx.scale(hk, hk);
  shape(ctx, rrect(-w2 / 2 - 22, -112, w2 + 44, 150, 16), { fill: PAL.mustard, line: 4, seed: 10, grain: 0.15, off: [6, 6] });
  text(ctx, 'angin kencang?', 0, 18, { font: F1, fill: PAL.ink, align: 'center', maxW: 780 });
  ctx.restore();
}

// ------------------------------------------------------------ 2. MASALAH (2,75 – 5,708): gerbong padat, June gerah
const JM = { x: 560, y: 1650, s: 1.9 };
function poseMasalah(t) {
  const fase = 2.6 * t + 1.0 * Math.max(0, t - C.gerah);       // kipasan tangan makin cepat setelah "gerah"
  return { x: JM.x, y: JM.y, s: JM.s, dir: 1, view: 'q', face: 'focus', blink: kedip(t), shadow: false, look: [-3, 2],
    armB: { a1: -1.78, a2: -1.62 }, handB: 'grip', armF: { a1: -0.5, a2: -2.05 + 0.38 * Math.sin(TAU * fase) }, handF: 'open' };
}
// tali pegangan KRL: pita dari palang ke cincin segitiga
function tali(ctx, px, py, ujung, seed) {
  ink(ctx, [[px, py], ujung], 16, { seed, taper: false, wob: 0.05 });
  ink(ctx, [[px, py], ujung], 9, { seed: seed + 1, taper: false, wob: 0.05, color: PAL.white });
  const a = Math.atan2(ujung[1] - py, ujung[0] - px) - Math.PI / 2;
  const cincin = xform(spline([[0, -6], [40, 56], [0, 70], [-40, 56]], true, 6), ujung[0], ujung[1], a);
  ink(ctx, cincin, 17, { closed: true, seed: seed + 2 });
  ink(ctx, cincin, 9, { closed: true, seed: seed + 3, color: PAL.white });
}
function penumpangKiri(ctx, dx, t) {                 // punggung pria berjaket navy, tangan di pegangan x 150
  ctx.save(); ctx.translate(dx, 0);
  ink(ctx, [[190, 820], [168, 560], [150, 470]], 60, { seed: 1520, taper: false });
  ink(ctx, [[190, 820], [168, 560], [150, 470]], 48, { seed: 1521, taper: false, color: NAVY });
  shape(ctx, spline([[-220, 1990], [-210, 860], [-90, 730], [80, 720], [230, 770], [300, 900], [310, 1990]], true, 6),
    { fill: NAVY, line: 4.4, seed: 1522, grain: 0.3, shade: [{ pts: rect(170, 700, 200, 1300), color: NAVYD, alpha: 0.7 }] });
  shape(ctx, rrect(20, 640, 90, 100, 20), { fill: PAL.skinD, line: 4, seed: 1523, grain: 0.2 });
  shape(ctx, ellipse(60, 590, 92, 106, 30), { fill: PAL.hair, line: 4, seed: 1524, grain: 0.3 });
  shape(ctx, ellipse(150, 600, 16, 24, 12), { fill: PAL.skinD, line: 3, seed: 1525, grain: 0 });
  tanganDi(ctx, [150, 452], -Math.PI / 2, 'grip', 2.3, null, -1);
  ctx.restore();
}
function penumpangKanan(ctx, dx, t) {                // punggung penumpang berkemeja toska + tali ransel mustard
  ctx.save(); ctx.translate(dx, 0);
  shape(ctx, spline([[800, 1990], [810, 900], [900, 770], [1040, 750], [1180, 800], [1240, 1990]], true, 6),
    { fill: PAL.tealD, line: 4.4, seed: 1530, grain: 0.3, shade: [{ pts: rect(800, 700, 90, 1300), color: PAL.tealDD, alpha: 0.6 }] });
  ink(ctx, [[930, 790], [890, 1500]], 30, { seed: 1531, taper: false });
  ink(ctx, [[930, 790], [890, 1500]], 22, { seed: 1532, taper: false, color: PAL.mustard });
  shape(ctx, rrect(980, 660, 90, 110, 20), { fill: PAL.skin, line: 4, seed: 1533, grain: 0.2 });
  shape(ctx, ellipse(1020, 610, 88, 100, 30), { fill: PAL.hair, line: 4, seed: 1534, grain: 0.3 });
  ctx.restore();
}
function sceneMasalah(ctx, t) {
  const sentak = t > C.desak ? 0.014 * Math.exp(-(t - C.desak) * 4) * Math.sin((t - C.desak) * 18) : 0;
  const g = 0.01 * Math.sin(TAU * 0.45 * (t - T2)) + sentak;
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, T2, T3)), 540, 1100);
  ctx.translate(540, 1700); ctx.rotate(g); ctx.translate(-540, -1700);
  ctx.fillStyle = PAL.pink; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (const x of [20, 540, 1060]) ink(ctx, [[x, 240], [x, 1180]], 4, { color: PAL.pinkD, seed: 1500 + x, taper: false });
  jendela(ctx, 90, 520, 380, 400, t, { matahari: true, v: 90 });
  jendela(ctx, 610, 520, 380, 400, t, { v: 90 });
  shape(ctx, rrect(-80, 1170, W + 160, 140, 28), { fill: PAL.teal, line: 4.4, seed: 1510, grain: 0.3 });
  shape(ctx, rrect(-80, 1300, W + 160, 80, 20), { fill: PAL.tealD, line: 4.4, seed: 1511, grain: 0.3 });
  plane(ctx, rect(-300, 1560, W + 600, 800), PAL.paperDD);
  ink(ctx, [[-300, 1560], [W + 300, 1560]], 5, { seed: 1512, taper: false });
  shape(ctx, rrect(-100, 190, W + 200, 24, 10), { fill: PAL.chrome, line: 4, seed: 1513, grain: 0.15 });
  // penumpang mendesak di "Desak-desakan": mundur 20 px (4 frame) lalu maju 70 px
  const dor = kf(t, [[T2, 0], [C.desak - 4 / FPS, -20, eo], [C.desak, 70, E_in], [C.desak + 0.5, 52, eo]]);
  const ayun = i => 0.07 * Math.sin(TAU * 0.45 * t + i) + sentak * 4;
  [[400, 0], [820, 1]].forEach(([x, i]) => tali(ctx, x, 202, [x + Math.sin(ayun(i)) * 250, 202 + Math.cos(ayun(i)) * 250], 1540 + 4 * i));
  tali(ctx, 150 + dor, 202, [150 + dor, 452], 1550);
  penumpangKanan(ctx, 10 - dor, t);
  // June (terjepit 0,96 × 1,03 waktu didesak) + tote di pinggang
  const pose = poseMasalah(t), [qx, qy] = t >= C.desak ? squash(t, C.desak, -0.04, -0.03) : [1, 1];
  const J = toScreen(pose, armJoints(pose, 'B').ha), tg = [JM.x + (J[0] - JM.x) * qx, JM.y + (J[1] - JM.y) * qy];
  tali(ctx, tg[0], 202, [tg[0], tg[1] - 26], 1560);
  ctx.save(); ctx.translate(JM.x, JM.y); ctx.scale(qx, qy); ctx.translate(-JM.x, -JM.y);
  const tas = toScreen(pose, [-70, -250]);
  ink(ctx, [toScreen(pose, [-20, -380]), [tas[0] + 30, tas[1] - 40]], 16, { seed: 1561, taper: false });
  shape(ctx, xform(rrect(-70, -60, 140, 160, 14), tas[0], tas[1], 0.12), { fill: PAL.mustard, line: 4.4, seed: 1562, grain: 0.35 });
  drawOwner(ctx, pose, t);
  // keringat: dua butir di dahi, satu meluncur dan jatuh di "gerah"
  [[30, -522], [-24, -536]].forEach(([lx, ly], i) => { const p = toScreen(pose, [lx, ly]); tetes(ctx, p[0], p[1] + 2 * Math.sin(TAU * 2 * t + i), 13); });
  const jatuh = seg(t, C.gerah - 0.25, C.gerah), turun = t > C.gerah ? E_in(seg(t, C.gerah, C.gerah + 10 / FPS)) : 0;
  if (turun < 1) { const p = toScreen(pose, [52, -476 + 30 * eo(jatuh)]); tetes(ctx, p[0] + 6 * turun, p[1] + 150 * turun, 14); }
  ctx.restore();
  penumpangKiri(ctx, -10 + dor, t);
  ctx.restore();
  teksKunci(ctx, t, C.desak + 0.2, 'Gerah banget?');
}

// ------------------------------------------------------------ 3. PRODUK (5,708 – 8,875): kipas keluar dari tote bag
const KP3 = { x: 540, y: 760, w: 430 };
const TAS3 = 1170;
function sceneProduk(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.04 * ss(seg(t, C.nah, T4)), 540, 900);
  ctx.fillStyle = PAL.tealL; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (const y of [660, 1460]) ink(ctx, [[-300, y], [W + 300, y]], 4, { color: PAL.teal, seed: 1600 + y, taper: false });
  jendela(ctx, 70, 230, 940, 340, t, { v: 90 });
  shape(ctx, rrect(930, -100, 46, 2200, 20), { fill: PAL.chrome, line: 4, seed: 1602, grain: 0.15 });
  const tasY = TAS3 + kf(t, [[5.62, 0], [C.nah, 16, eo], [C.nah + 0.35, 0, eio]]);
  // tote kanvas: mulut gelap + dua tali (kiri ke bahu, kanan di belakang tiang)
  shape(ctx, ellipse(540, tasY + 4, 262, 34, 40), { fill: PAL.ink, line: 4, seed: 1610, grain: 0.1 });
  for (const [sabuk, sd] of [[[[320, tasY + 10], [170, 840], [-60, 600]], 1611], [[[760, tasY + 10], [960, 820], [1160, 640]], 1616]]) {
    ink(ctx, sabuk, 36, { seed: sd, taper: false }); ink(ctx, sabuk, 26, { seed: sd + 1, taper: false, color: PAL.mustardD });
  }
  const ka = t < C.ini ? 0 : kf(t, [[C.ini, 0], [C.ini + 6 / FPS, 0.85, eo]]);
  pita(ctx, 168, 800, Math.max(0.1, ka), t, { L: 150, lebar: 34, warna: PAL.coral, A: 18, hz: 6, seed: 1613, lipat: false });
  pita(ctx, 160, 812, Math.max(0.1, ka * 0.9), t + 0.13, { L: 120, lebar: 30, warna: PAL.coralD, A: 16, hz: 6, seed: 1614, lipat: false });
  shape(ctx, ellipse(160, 806, 18, 14, 12), { fill: PAL.coral, line: 3, seed: 1615, grain: 0 });
  const y = kf(t, [[5.62, 1330], [C.nah, KP3.y - 30, eo], [C.nah + 0.2, KP3.y, eio]]), [sx, sy] = squash(t, C.nah, 0.08, 0.08);
  const k3 = { ...KP3, y };
  const r = titik(k3, RING);
  angin(ctx, [r[0] - 40, r[1]], [60, 640], t, ka, { n: 4, lebar: 260 });
  kipasDiTangan(ctx, k3, t, { sx, sy, cahaya: PAL.tealL, dari: [1140, 1560], tekan: [C.ini] });
  shape(ctx, [[276, tasY], [804, tasY], [842, tasY + 520], [238, tasY + 520]],
    { fill: PAL.mustard, line: 4.4, seed: 1620, grain: 0.35, breaks: 0.08, shade: [{ pts: rect(690, tasY - 20, 200, 560), color: PAL.mustardD, alpha: 0.4 }] });
  shape(ctx, [[276, tasY], [804, tasY], [808, tasY + 50], [272, tasY + 50]], { fill: PAL.mustardD, line: 4, seed: 1621, grain: 0.3, breaks: 0 });
  dashed(ctx, [[290, tasY + 64], [792, tasY + 64]], 4, 16, 12, 0, PAL.mustardD);
  for (const x of [380, 700]) ink(ctx, [[x, tasY + 90], [x + (x < 540 ? -14 : 14), tasY + 420]], 3, { color: PAL.mustardD, seed: 1622 + x });
  if (t >= C.ini) labelIlustrasi(ctx, 70, 1470 - 230);
  ctx.restore();
  teksKunci(ctx, t, C.kipas, 'Kipas turbo');
}

// ------------------------------------------------------------ 4. FITUR ① (8,875 – 11,708): tes tisu + rotor di kaca pembesar
const KP4 = { x: 400, y: 1030, w: 440, rot: -0.06 };
const LUP4 = { x: 735, y: 690, r: 185 };           // tepi kanan bingkai 938 (zona aman ≤ 940)
function putaran(t, t0, t1, wmax) {                 // sudut rotor = ∫ω dt, ω naik eio dari 0 (t0) ke wmax (t1)
  if (t <= t0) return 0;
  const n = 24, te = Math.min(t, t1); let a = 0;
  for (let i = 0; i < n; i++) a += eio(seg(t0 + (te - t0) * (i + 0.5) / n, t0, t1)) * (te - t0) / n;
  return wmax * (a + Math.max(0, t - t1));
}
function rotor(ctx, x, y, r, sudut) {
  shape(ctx, ellipse(x, y, r, r, 48), { fill: PAL.chromeD, line: 5, seed: 1700, grain: 0.2, off: [0, 0] });
  shape(ctx, ellipse(x, y, r * 0.86, r * 0.86, 48), { fill: PAL.chrome, line: 3.6, seed: 1701, grain: 0.15, off: [0, 0] });
  const bilah = spline([[0.22, -0.1], [0.55, -0.24], [0.82, -0.16], [0.8, 0.08], [0.5, 0.04], [0.24, 0.1]], true, 4);
  for (let i = 0; i < 7; i++) shape(ctx, xform(bilah, x, y, sudut + i * TAU / 7, r), { fill: PAL.tealD, line: 3.4, seed: 1702 + i, grain: 0.2, off: [0, 0] });
  shape(ctx, ellipse(x, y, r * 0.26, r * 0.26, 24), { fill: PAL.coral, line: 4, seed: 1710, grain: 0.2, off: [0, 0] });
  shape(ctx, ellipse(x, y, r * 0.08, r * 0.08, 12), { fill: PAL.white, line: 2.4, seed: 1711, grain: 0, off: [0, 0] });
}
function kacaPembesar(ctx, x, y, r, k, isi) {
  if (k <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.translate(-x, -y);
  shape(ctx, xform(rrect(-24, 0, 48, 180, 18), x + r * 0.74, y + r * 0.74, -Math.PI / 4), { fill: PAL.kraftD, line: 4.4, seed: 1720, grain: 0.3 });
  shape(ctx, ellipse(x, y, r + 18, r + 18, 60), { fill: PAL.ink, line: 0, seed: 1721, grain: 0, off: [0, 0] });
  shape(ctx, ellipse(x, y, r, r, 60), { fill: PAL.white, line: 0, seed: 1722, grain: 0.1, off: [0, 0] });
  ctx.save(); ctx.beginPath(); ctx.arc(x, y, r - 2, 0, TAU); ctx.clip(); isi(); ctx.restore();
  ink(ctx, ellipse(x, y, r * 0.8, r * 0.8, 24, Math.PI * 1.08, Math.PI * 1.38), 7, { color: PAL.white, seed: 1723 });
  ctx.restore();
}
function pintuKRL(ctx, t) {                           // pintu geser dua daun di dinding avokad
  ctx.fillStyle = PAL.avocadoL; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (const [x0, i] of [[120, 0], [546, 1]]) {
    shape(ctx, rrect(x0, 130, 414, 1720, 16), { fill: PAL.avocado, line: 4.4, seed: 1730 + i, grain: 0.3, shade: [{ pts: rect(x0 + 360, 120, 70, 1740), color: PAL.avocadoD, alpha: 0.45 }] });
    jendela(ctx, x0 + 62, 270, 290, 560, t, { v: 90, kusen: PAL.chrome });
  }
  ink(ctx, [[540, 130], [540, 1850]], 14, { seed: 1735, taper: false });
}
function sceneFitur1(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.04 * ss(seg(t, T4, T5)), 540, 1000);
  pintuKRL(ctx, t);
  const ang = t < C.motor ? 0.12 : 0.12 + 0.88 * eio(seg(t, C.motor, C.rpm));
  produk(ctx, 'kipas', KP4.x, KP4.y, KP4.w, { rot: KP4.rot, cahaya: PAL.avocadoL });
  const r = titik(KP4, RING), P0 = [r[0] + 40, r[1] - KP4.w / KP.w * RING_R - 60];
  pita(ctx, P0[0], P0[1], ang, t, { L: 330, lebar: 84, A: 30, hz: 4 + 2 * ang, angkat: -0.06, seed: 1740 });
  angin(ctx, [r[0] - 30, r[1] + 30], [-40, r[1] + 120], t, ang, { n: 3, lebar: 220, cepat: 1.8 });
  tanganDi(ctx, [P0[0] + 4, P0[1] + 10], Math.PI / 2, 'grip', 2.4, [P0[0] + 260, -120], -1);
  // kaca pembesar: rotor (ilustrasi) makin cepat sampai "RPM"
  const kk = pop(t, C.motor, 0.3);
  if (kk > 0) {
    dashed(ctx, [[LUP4.x - LUP4.r * 0.9, LUP4.y + LUP4.r * 0.5], [r[0] + 70, r[1] - 20]], 6, 16, 12, 0, PAL.ink);
    kacaPembesar(ctx, LUP4.x, LUP4.y, LUP4.r, kk, () => rotor(ctx, LUP4.x, LUP4.y, LUP4.r * 0.92, putaran(t, C.motor, C.rpm, 7.5)));
    labelIlustrasi(ctx, LUP4.x - 70, LUP4.y + LUP4.r + 70);
  }
  labelIlustrasi(ctx, 70, 1470 - 230);
  const la = pop(t, 9.9, 0.3);
  if (la > 0) pelat(ctx, 'angin 20 m/s', 250, 520, '600 46px Jost', { k: la, rot: 0.03, fill: PAL.mustardL, seed: 1750 });
  ctx.restore();
  const k = pop(t, C.motor + 0.1, 0.28) * (1 + 0.08 * Math.sin(Math.PI * seg(t, C.rpm, C.rpm + 0.25)));
  if (k > 0) pelat(ctx, '23.000 RPM', W / 2, 330, '92px Slab', { k, rot: -0.02, seed: 1760 });
}

// ------------------------------------------------------------ 5. FITUR ② (11,708 – 14,5): 6 level di layar LED
const KP5 = { x: 340, y: 990, w: 520, rot: 0 };
const LUP5 = { x: 730, y: 790, r: 190 };           // tepi kanan bingkai 938 (zona aman ≤ 940)
const TEKAN5 = [290, 300, 310, 320, 329].map(f => f / FPS);
const SEG7 = { 1: 'bc', 2: 'abged', 3: 'abgcd', 4: 'fgbc', 5: 'afgcd', 6: 'afgedc' };
function angka7(ctx, d, x, y, h, warna) {
  const w = h * 0.55, tb = h * 0.14;
  const S = { a: [[-1, -1], [1, -1]], b: [[1, -1], [1, 0]], c: [[1, 0], [1, 1]], d: [[-1, 1], [1, 1]], e: [[-1, 0], [-1, 1]], f: [[-1, -1], [-1, 0]], g: [[-1, 0], [1, 0]] };
  for (const s of 'abcdefg') {
    const [[x0, y0], [x1, y1]] = S[s], on = SEG7[d].includes(s), q = 0.17;
    ink(ctx, [[x + lerp(x0, x1, q) * w / 2, y + lerp(y0, y1, q) * h / 2], [x + lerp(x0, x1, 1 - q) * w / 2, y + lerp(y0, y1, 1 - q) * h / 2]], tb,
      { color: on ? warna : PAL.inkSoft, seed: 1800 + s.charCodeAt(0), taper: false, wob: 0.05 });
  }
}
function layarLED(ctx, x, y, level) {
  shape(ctx, rrect(x - 120, y - 150, 240, 290, 26), { fill: PAL.ink, line: 4, seed: 1810, grain: 0.1, off: [0, 0] });
  angka7(ctx, level, x, y - 30, 170, PAL.white);
  shape(ctx, rrect(x - 60, y + 80, 104, 40, 8), { fill: null, line: 4, lineColor: PAL.white, seed: 1811, off: [0, 0], breaks: 0 });
  shape(ctx, rect(x + 44, y + 92, 10, 16), { fill: PAL.white, line: 0, grain: 0, off: [0, 0] });
  for (let i = 0; i < 4; i++) shape(ctx, rect(x - 52 + i * 24, y + 87, 17, 26), { fill: PAL.white, line: 0, grain: 0, off: [0, 0] });
}
function kainKursi(ctx) {                            // kain kursi KRL: biru dengan pola wajik
  ctx.fillStyle = PAL.blue; ctx.fillRect(-300, -300, W + 600, H + 600);
  for (let r = 0; r < 24; r++) for (let c = 0; c < 14; c++) {
    const x = -60 + c * 90 + (r % 2) * 45, y = -40 + r * 90;
    shape(ctx, [[x, y - 16], [x + 12, y], [x, y + 16], [x - 12, y]], { fill: PAL.blueD, line: 0, grain: 0, off: [0, 0] });
  }
  for (const y of [520, 1520]) dashed(ctx, [[-100, y], [W + 100, y]], 4, 18, 12, 0, PAL.blueL);
}
function sceneFitur2(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, T5, T6)), 540, 1000);
  kainKursi(ctx);
  const level = 1 + TEKAN5.filter(p => t >= p + 2 / FPS).length;
  const r = titik(KP5, RING);
  angin(ctx, [r[0] - 40, r[1]], [-60, r[1] - 120], t, t < C.enam ? 0.15 : level / 6, { n: Math.min(5, level), lebar: 280, cepat: 1.2 + 0.15 * level });
  kipasDiTangan(ctx, KP5, t, { asli: true, kanan: false, dari: [-160, 1760], tekan: TEKAN5 });
  const kk = pop(t, C.enam, 0.3);
  if (kk > 0) {
    const d = titik(KP5, LAYAR);
    dashed(ctx, [[LUP5.x - LUP5.r * 0.95, LUP5.y + LUP5.r * 0.3], [d[0] + 50, d[1]]], 6, 16, 12, 0, PAL.ink);
    kacaPembesar(ctx, LUP5.x, LUP5.y, LUP5.r, kk, () => {
      ctx.fillStyle = PAL.paper; ctx.fillRect(LUP5.x - 200, LUP5.y - 200, 400, 400);
      const b = 1 + 0.06 * Math.sin(Math.PI * seg(t, TEKAN5[level - 2] + 2 / FPS, TEKAN5[level - 2] + 6 / FPS));
      ctx.save(); ctx.translate(LUP5.x, LUP5.y); ctx.scale(b, b); ctx.translate(-LUP5.x, -LUP5.y);
      layarLED(ctx, LUP5.x, LUP5.y + 10, level);
      ctx.restore();
    });
    labelIlustrasi(ctx, LUP5.x - 70, LUP5.y + LUP5.r + 70);
  }
  ctx.restore();
  teksKunci(ctx, t, C.enam, '6 level');
}

// ------------------------------------------------------------ 6. BUKTI (14,5 – 16,75): papan info stasiun, cap + segel
const KP6 = { x: 300, y: 1060, w: 380, rot: 0.08 };
const KARTU6 = { x: 560, y: 590, w: 700, h: 300 };
function papanGabus(ctx) {
  ctx.fillStyle = PAL.brown; ctx.fillRect(-300, -300, W + 600, H + 600);
  shape(ctx, rrect(40, 250, 1000, 1300, 12), { fill: PAL.kraftL, line: 4.4, seed: 1900, grain: 0.5, off: [0, 0] });
  for (let i = 0; i < 260; i++) {
    const x = 60 + hash(i, 7) * 960, y = 270 + hash(i, 9) * 1260;
    shape(ctx, ellipse(x, y, 3 + 4 * hash(i, 3), 2 + 3 * hash(i, 4), 8), { fill: hash(i, 5) < 0.5 ? PAL.kraft : PAL.kraftD, line: 0, grain: 0, off: [0, 0] });
  }
}
function stempelY(t) {
  return kf(t, [[14.55, -400], [14.95, 380, eo], [C.cap - 5 / FPS, 320, eo], [C.cap, 485, E_in], [C.cap + 0.18, 485], [16.1, -500, eo]]);
}
function sceneBukti(ctx, t) {
  ctx.save(); cam(ctx, 1 + 0.03 * ss(seg(t, T6, T7)), 540, 900);
  papanGabus(ctx);
  produk(ctx, 'kipas', KP6.x, KP6.y, KP6.w, { rot: KP6.rot, cahaya: PAL.kraftL });
  shape(ctx, rrect(KARTU6.x - KARTU6.w / 2, KARTU6.y - KARTU6.h / 2, KARTU6.w, KARTU6.h, 12), { fill: PAL.white, line: 4.4, seed: 1910, grain: 0.12, off: [6, 6] });
  [[-1, 0], [1, 1]].forEach(([s, i]) => {
    const x = KARTU6.x + s * (KARTU6.w / 2 - 40), y = KARTU6.y - KARTU6.h / 2 + 30;
    shape(ctx, ellipse(x, y, 18, 18, 16), { fill: PAL.coral, line: 3.4, seed: 1911 + i, grain: 0.1 });
  });
  if (t >= C.cap) {
    const [qx, qy] = squash(t, C.cap, 0.08, 0.08);
    cetakCap(ctx, KARTU6.x, KARTU6.y + 10, 600, 236, [['10RB+', "800 150px 'Barlow Condensed'", 22], ['terjual', '600 52px Jost', 92]], { sx: qx, sy: qy });
  }
  segelRating(ctx, 830, 930, pop(t, C.segel, 0.3), '4,7', '26rb+');
  const yb = stempelY(t);
  if (t > 14.55 && t < 16.1) {
    const [sx, sy] = t >= C.cap ? squash(t, C.cap, 0.15, 0.2) : (t > C.cap - 2 / FPS ? [0.9, 1.15] : [1, 1]);
    capKaret(ctx, KARTU6.x, yb, sx, sy);
    tanganDi(ctx, [KARTU6.x + 34, yb - 290], Math.PI * 0.62, 'grip', 2.4, [KARTU6.x + 420, yb - 900], -1);
  }
  ctx.restore();
}

// ------------------------------------------------------------ 7. CTA (16,75 – 19,18): 10 warna + tunjuk ke link
const WARNA = ['#F2A7B8', '#F4F1EA', '#2B2B2E', '#8E6CC9', '#F2A7B8', '#F4F1EA', '#2B2B2E', '#8E6CC9', '#9A9EA3', '#F29A4A'];
const KIPAS7 = [850, 960];
function sceneCta(ctx, t) {
  ctx.fillStyle = PAL.paper; ctx.fillRect(-300, -300, W + 600, H + 600);
  ctx.save(); cam(ctx, 1 + 0.02 * ss(seg(t, T7, META.dur)), 540, 960);
  rays(ctx, 430, 880, 30, 1500, PAL.mustardL, { alpha: 0.55 });
  // kipas warna: 10 keping membuka dari poros (stagger 2 frame)
  WARNA.forEach((c, i) => {
    const k = pop(t, C.warna + i * 2 / FPS, 0.25), a = lerp(-0.62, -0.62 + i * 0.1, Math.min(1, k));
    if (k <= 0) return;
    shape(ctx, xform(rrect(-30, -310, 60, 300, 14), KIPAS7[0], KIPAS7[1], a), { fill: c, line: 3.6, seed: 2000 + i, grain: 0.15 });
  });
  if (t >= C.warna) shape(ctx, ellipse(KIPAS7[0], KIPAS7[1] - 20, 16, 16, 14), { fill: PAL.chrome, line: 3.4, seed: 2011, grain: 0 });
  const lw = pop(t, C.warna + 0.35, 0.28);
  if (lw > 0) pelat(ctx, '10 warna', 790, 580, '600 56px Jost', { k: lw, rot: 0.04, seed: 2012 });
  const nk = 1 + 0.05 * Math.sin(Math.PI * seg(t, C.warna, C.warna + 0.3));
  produk(ctx, 'kipas', 430, 870, 440 * nk, { rot: -0.05, asli: true });
  const ka = pop(t, C.warna + 4 / FPS, 0.3);
  if (ka > 0) produk(ctx, 'kipas_abu', 180, 1110, 210 * ka, { rot: -0.1, asli: true });
  // pelat CTA sudah ada sejak awal end card (dibaca paling lama), berdenyut sekali di "cek" dan di "link"
  const ck = pop(t, T7 + 0.08, 0.3), lp = 1 + 0.07 * Math.sin(Math.PI * seg(t, C.cek, C.cek + 0.25)) + 0.07 * Math.sin(Math.PI * seg(t, C.link, C.link + 0.3));
  if (ck > 0) pelat(ctx, 'Cek warna di link', 520, 360, '80px Slab', { k: ck * lp, rot: -0.02, seed: 2020, fill: PAL.mustard });
  // tangan masuk dari kanan bawah (di bawah keping warna), menunjuk ke bawah ke tempat link, tiba di "link" lewat busur
  const m = eio(seg(t, C.cek, C.link)), masuk = eo(seg(t, 17.0, 17.5));
  const tip = [lerp(930, 720, m) + 420 * (1 - masuk), lerp(1150, 1250, m) - 50 * Math.sin(Math.PI * m) + 6 * Math.sin(TAU * 0.8 * t)];
  tanganDi(ctx, tip, Math.PI * 0.5 + 0.35 * (1 - m), 'point', 2.2, [tip[0] + 420, tip[1] - 40], -1);
  ctx.restore();
}

// ------------------------------------------------------------ urutan scene + transisi
function renderSemua(ctx, t) {
  setClock(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (t < T2) sceneHook(ctx, t);
  else if (t < T3) sceneMasalah(ctx, t);
  else if (t < T4) { sceneProduk(ctx, t); if (t >= 8.55) wipe(ctx, eio(seg(t, 8.55, T4)), 'kiri', () => sceneFitur1(ctx, t)); }
  else if (t < T5) { sceneFitur1(ctx, t); if (t >= 11.4) wipe(ctx, eio(seg(t, 11.4, T5)), 'bawah', () => sceneFitur2(ctx, t)); }
  else if (t < T6) { sceneFitur2(ctx, t); if (t >= 14.2) wipe(ctx, eio(seg(t, 14.2, T6)), 'atas', () => sceneBukti(ctx, t)); }
  else if (t < T7) { sceneBukti(ctx, t); if (t >= 16.4) irisMasuk(ctx, KP6.x, KP6.y, eio(seg(t, 16.4, T7)), () => sceneCta(ctx, t)); }
  else sceneCta(ctx, t);
  caption(ctx, t);
  disclosure(ctx);
  paperFinish(ctx, W, H, 1);
}
export const renderFilm = denganLoop(renderSemua, LOOP_AT, LOOP_END, setClock);
