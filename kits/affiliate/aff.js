// Kit affiliate aff_studio — bagian yang berulang di setiap video (compliance + identitas), gaya midcentury-toon.
// Dikirim ke Slate sebagai engine/aff.js di samping kit `midcentury` (tools/slate.py, tools/pratinjau.py);
// film mengimpor `./engine/aff.js`. Isi adegan tetap digambar per video (ADR-P06): kit ini hanya
//   - cutout produk: garis tinta stiker, bayangan siluet cokelat, sisi bawah ilustrasi (muatFoto, produk),
//   - disclosure "Link afiliasi" setiap frame, slab caption dari timing kata, pelat teks kunci, label "ilustrasi",
//   - tangan + lengan, cap karet, segel bulat, transisi (wipe, iris), loop ke frame 0,
//   - easing dan pose (pop, kf, squash, cam).
// Semua murni fungsi dari t (kontrak render Slate). Diambil dari examples/aff001-keset.
import { PAL, shape, ink, ellipse, rect, rrect, star, text, fit, measure, clamp, lerp, seg, ss, eio, back, TAU } from './toon.js';
import { drawHand } from './chars.js';

export const W = 1080, H = 1920, FPS = 24;

// ------------------------------------------------------------ easing dan pose
export const pop = (t, t0, d = 0.28) => back(seg(t, t0, t0 + d), 1.8);
export const E_in = u => u * u;
// keyframe: [[t, nilai, easing?], ...]; nilai boleh angka atau array
export const kf = (t, keys, e = eio) => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
    const [t0, a] = keys[i - 1], [t1, b] = keys[i], u = (keys[i][2] || e)(seg(t, t0, t1));
    return Array.isArray(a) ? a.map((v, j) => lerp(v, b[j], u)) : lerp(a, b, u);
  }
  return keys[keys.length - 1][1];
};
// mendarat: skala (1+sx) × (1−sy) selama 2 frame lalu pegas teredam (benda datar 0,12/0,1; Baru Tau 0,25/0,3)
export function squash(t, t0, sx = 0.12, sy = 0.1) {
  if (t < t0) return [1, 1];
  const u = (t - t0) * FPS;
  if (u < 2) return [1 + sx, 1 - sy];
  const d = Math.exp(-(u - 2) * 0.35) * Math.cos((u - 2) * 0.55);
  return [1 + sx * d, 1 - sy * d];
}
export function cam(ctx, z, cx, cy) { ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy); }

// ------------------------------------------------------------ cutout produk (aset/foto.js dari tools/cutout.py)
const IMG = {}, SIL = {}, BAY = {}, BAWAH = {}, KONTAK = {}, JATUH = {}, LUMUR = {};
const PAD = 70;                                   // ruang blur di sekeliling bayangan lembut
function topeng(im, dasar, titik) {
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
  const g = c.getContext('2d'); g.drawImage(im, 0, 0); g.globalCompositeOperation = 'source-in';
  g.fillStyle = dasar; g.fillRect(0, 0, c.width, c.height);
  if (titik) {                                   // pola titik hanya di dalam siluet (source-atop, bukan source-in)
    g.globalCompositeOperation = 'source-atop'; g.fillStyle = titik;
    const s = Math.max(c.width, c.height) / 34;
    for (let y = s / 2, r = 0; y < c.height; y += s, r++) for (let x = (r % 2) * s / 2; x < c.width; x += s) { g.beginPath(); g.arc(x, y, s * 0.22, 0, TAU); g.fill(); }
  }
  return c;
}
// Muat semua cutout sebelum frame 0 (dipanggil dengan await di top-level film.js). o.bawah = [dasar, titik] sisi bawah.
export async function muatFoto(FOTO, o = {}) {
  if (typeof Image === 'undefined' || !FOTO) return;
  const [dasar, titik] = o.bawah || ['#7F8FB4', '#C9D3EA'];
  await Promise.all(Object.entries(FOTO).map(([k, v]) => new Promise(ok => {
    const im = new Image(); im.onload = () => { IMG[k] = im; ok(); }; im.onerror = () => ok(); im.src = v.src;
  })));
  for (const [k, im] of Object.entries(IMG)) {
    SIL[k] = topeng(im, PAL.ink); BAY[k] = topeng(im, PAL.brown); BAWAH[k] = topeng(im, dasar, titik);
    KONTAK[k] = lembut(BAY[k], 7); JATUH[k] = lembut(BAY[k], 26);
  }
}
// siluet diblur sekali saat muat (bukan tiap frame): bayangan lembut tanpa biaya render per frame
function lembut(sil, px) {
  const c = document.createElement('canvas'); c.width = sil.width + 2 * PAD; c.height = sil.height + 2 * PAD;
  const g = c.getContext('2d'); g.filter = `blur(${px}px)`; g.drawImage(sil, PAD, PAD);
  return c;
}
// salinan produk yang "diterangi" adegan: sorot hangat di kiri atas, bayangan di kanan bawah, warna ambien adegan
// (soft-light). Tint dibatasi 0–0,15 (visual.produk_tint_maks): warna dan bentuk produk tetap terbaca asli.
function diterangi(nama, cahaya, k, relight) {
  const kunci = nama + '|' + cahaya + '|' + k + '|' + relight;
  if (LUMUR[kunci]) return LUMUR[kunci];
  const im = IMG[nama], c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
  const g = c.getContext('2d'); g.drawImage(im, 0, 0);
  if (relight > 0) {
    const gr = g.createLinearGradient(0, 0, c.width, c.height);
    gr.addColorStop(0, `rgba(255,246,226,${0.55 * relight})`); gr.addColorStop(0.45, 'rgba(255,246,226,0)');
    gr.addColorStop(0.6, 'rgba(60,40,30,0)'); gr.addColorStop(1, `rgba(60,40,30,${0.9 * relight})`);
    g.globalCompositeOperation = 'soft-light'; g.fillStyle = gr; g.fillRect(0, 0, c.width, c.height);
  }
  if (cahaya && k > 0) { g.globalCompositeOperation = 'soft-light'; g.globalAlpha = Math.min(k, 0.15); g.fillStyle = cahaya; g.fillRect(0, 0, c.width, c.height); }
  g.globalCompositeOperation = 'destination-in'; g.globalAlpha = 1; g.drawImage(im, 0, 0);   // kembalikan alpha asli
  return (LUMUR[kunci] = c);
}
export const tinggiProduk = (nama, w) => IMG[nama] ? w * IMG[nama].height / IMG[nama].width : w * 0.75;
// produk(ctx, nama, cx, cy, lebar, o)
//   o.rot, o.sx, o.sy, o.alpha; o.bawah: sisi bawah ilustrasi; o.bayang: false = tanpa bayangan;
//   o.tinggi: jarak benda ke lantai (px, bawaan 18; benda di udara → bayangan menjauh dan memudar);
//   o.blend (bawaan true): bayangan lembut dua lapis + pencahayaan ulang; false = gaya v1 (bayangan siluet keras);
//   o.cahaya: warna ambien adegan (biasanya warna latar) yang meresap tipis ke produk, o.tint 0–0,15 (bawaan 0,08);
//   o.asli: true = tanpa tint dan tanpa pencahayaan ulang (end card / close-up: warna produk apa adanya).
export function produk(ctx, nama, cx, cy, w, o = {}) {
  const im = IMG[nama]; if (!im) return;
  const h = w * im.height / im.width, a = o.alpha ?? 1, blend = o.blend !== false, tinggi = o.tinggi ?? 18;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy); ctx.rotate(o.rot || 0); ctx.scale(o.sx ?? 1, o.sy ?? 1);
  if (o.bayang !== false && !blend) { ctx.save(); ctx.globalAlpha *= 0.3; ctx.drawImage(BAY[nama], -w / 2 + 12, -h / 2 + tinggi, w, h); ctx.restore(); }
  if (o.bayang !== false && blend) {
    const s = w / im.width, pw = (im.width + 2 * PAD) * s, ph = (im.height + 2 * PAD) * s, jauh = clamp((tinggi - 18) / 120, 0, 1);
    ctx.save(); ctx.globalAlpha *= 0.34 * (1 - 0.6 * jauh);       // bayangan jatuh: lebar, lembut, searah cahaya kiri atas
    ctx.drawImage(JATUH[nama], -pw / 2 + 26 + 30 * jauh, -ph / 2 + 30 + tinggi * 0.9, pw, ph); ctx.restore();
    ctx.save(); ctx.globalAlpha *= 0.5 * (1 - jauh);                // bayangan kontak: rapat di bawah benda
    ctx.drawImage(KONTAK[nama], -pw / 2 + 5, -ph / 2 + 8, pw, ph); ctx.restore();
  }
  for (let i = 0; i < 10; i++) { const t = i * TAU / 10; ctx.drawImage(SIL[nama], -w / 2 + Math.cos(t) * 4.5, -h / 2 + Math.sin(t) * 4.5, w, h); }
  const gambar = o.bawah ? BAWAH[nama] : (blend && !o.asli ? diterangi(nama, o.cahaya || null, o.cahaya ? (o.tint ?? 0.08) : 0, 0.22) : im);
  ctx.drawImage(gambar, -w / 2, -h / 2, w, h);
  ctx.restore();
}

// ------------------------------------------------------------ tangan
export function lengan(ctx, from, pergelangan, k = 1) {
  ink(ctx, [from, pergelangan], 30 * k, { seed: 140, taper: false, wob: 0.03 });
  ink(ctx, [from, pergelangan], 22 * k, { seed: 141, taper: false, wob: 0.03, color: PAL.coral });
}
// tangan dengan ujung jari/telapak di `ujung`, menghadap sudut a; lengan dari titik `dari` (opsional)
export function tanganDi(ctx, ujung, a, jenis, k, dari, sisi = 1) {
  const jangkau = (jenis === 'point' ? 57 : jenis === 'grip' ? 30 : 44) * k;
  const w = [ujung[0] - Math.cos(a) * jangkau, ujung[1] - Math.sin(a) * jangkau];
  if (dari) lengan(ctx, dari, w, k / 2.2);
  drawHand(ctx, w[0], w[1], a, jenis, sisi, k);
  return w;
}

// ------------------------------------------------------------ teks: pelat, teks kunci, label ilustrasi, disclosure
export function pelat(ctx, str, x, y, font, o = {}) {
  const w = measure(ctx, str, font) + (o.pad ?? 48), px = parseInt(font.match(/(\d+)px/)[1], 10), h = px * 1.34;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? 0); ctx.scale(o.k ?? 1, o.k ?? 1);
  shape(ctx, rrect(-w / 2, -h / 2, w, h, 14), { fill: o.fill ?? PAL.white, line: 4, seed: o.seed ?? 760, grain: 0.12, off: [6, 5] });
  text(ctx, str, 0, px * 0.36, { font, fill: o.color ?? PAL.ink, align: 'center' });
  ctx.restore();
}
// teks kunci per scene (≤ 3 kata, 92 px Slab), pop di t0
export function teksKunci(ctx, t, t0, str, y = 330) {
  const k = pop(t, t0, 0.28); if (k <= 0) return;
  pelat(ctx, str, W / 2, y, '92px Slab', { k, rot: -0.02, seed: 770 + str.length });
}
export function labelIlustrasi(ctx, x, y) { text(ctx, 'ilustrasi', x, y, { font: '600 30px Jost', fill: PAL.ink, plate: PAL.white, off: [3, 3] }); }
// tag kraft di kiri atas, setiap frame (kunci compliance disclosure.ada / disclosure.font_px ≥ 32)
export function disclosure(ctx, teks = 'Link afiliasi') {
  const font = '600 34px Jost', w = measure(ctx, teks, font) + 64;
  ctx.save(); ctx.translate(60, 175);
  shape(ctx, [[0, 0], [w - 22, 0], [w, 28], [w - 22, 56], [0, 56]], { fill: PAL.white, line: 3.4, seed: 980, grain: 0.1, breaks: 0, off: [4, 4] });
  shape(ctx, ellipse(w - 30, 28, 7, 7, 14), { fill: PAL.kraftL, line: 2.6, seed: 981, off: [0, 0] });
  text(ctx, teks, 20, 40, { font, fill: PAL.ink });
  ctx.restore();
}

// ------------------------------------------------------------ caption (slab kertas, ≤ 7 kata, 1 kata disorot)
// KATA: [[mulai, selesai, teks], ...] (kata_koreksi.json); CAP: [[kata awal, kata akhir, kata disorot], ...];
// o.digit: {indeks kata: 'teks layar'} (angka sebagai digit); o.dur: META.dur (caption terakhir sampai akhir).
export function buatCaption(KATA, CAP, o = {}) {
  const digit = o.digit || {}, dur = o.dur ?? 1e9, dasar = o.y ?? 1470;
  const CHUNKS = CAP.map(([a, b, s]) => ({ toks: KATA.slice(a, b + 1).map((k, j) => [digit[a + j] ?? k[2], a + j, a + j === s]), a: KATA[a][0], b: KATA[b][1] }));
  CHUNKS.forEach((c, i) => { const nx = CHUNKS[i + 1]; c.end = nx ? Math.min(nx.a, c.b + 0.5) : dur; });
  return function caption(ctx, t) {
    const c = CHUNKS.find(q => t >= Math.max(0, q.a - 0.04) && t < q.end); if (!c) return;
    const a = c.a <= 0 ? 1 : Math.min(ss(seg(t, c.a - 0.04, c.a + 0.08)), c.end >= dur ? 1 : 1 - ss(seg(t, c.end - 0.1, c.end)));
    if (a <= 0) return;
    const str = c.toks.map(q => q[0]).join(' ');
    const f = fit(ctx, str, '600 {px}px Jost', 68, 900, 2, 64);
    const sp = measure(ctx, ' ', f.font), lh = f.px * 1.2;
    const w = Math.max(...f.lines.map(l => measure(ctx, l, f.font))) + 96, h = 34 + f.lines.length * lh, x = W / 2 - w / 2, y = dasar - h;
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
  };
}

// ------------------------------------------------------------ bukti: cap karet + segel bulat
// badan cap karet; yb = dasar karet. Tangan dipasang terpisah: tanganDi(ctx, [x + 34, yb - 290], π·0,62, 'grip', 2.4, ...)
export function capKaret(ctx, x, yb, sx = 1, sy = 1) {
  ctx.save(); ctx.translate(x, yb); ctx.scale(sx, sy);
  shape(ctx, rrect(-260, -24, 520, 24, 6), { fill: PAL.coral, line: 3.6, seed: 640, grain: 0.2 });
  shape(ctx, rrect(-250, -112, 500, 92, 14), { fill: PAL.kraftD, line: 4.6, seed: 641, grain: 0.35, shade: [{ pts: rect(150, -120, 120, 110), color: PAL.brown, alpha: 0.5 }] });
  shape(ctx, rrect(-34, -236, 68, 130, 12), { fill: PAL.brownL, line: 4, seed: 642, grain: 0.3 });
  shape(ctx, ellipse(0, -270, 62, 52, 36), { fill: PAL.kraft, line: 4.4, seed: 643, grain: 0.3 });
  ctx.restore();
}
// cetakan cap: bingkai tinta + baris teks, semua #B8452B (kontras 4,97:1 di atas #FBF6EA)
export function cetakCap(ctx, x, y, w, h, baris, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? -0.05); ctx.scale(o.sx ?? 1, o.sy ?? 1);
  ink(ctx, rrect(-w / 2, -h / 2, w, h, 16), 6, { closed: true, color: PAL.coralD, seed: 620, breaks: 0.15 });
  baris.forEach(([str, font, dy]) => text(ctx, str, 0, dy, { font, fill: PAL.coralD, align: 'center' }));
  ctx.restore();
}
// segel bulat (rating): bintang mustard + angka di lingkaran teal tua
export function segelRating(ctx, x, y, k, rating, ulasan) {
  if (k <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.rotate(0.08);
  star(ctx, 0, 0, 170, { n: 18, inner: 0.86, fill: PAL.white, off: [0, 0] });
  shape(ctx, ellipse(0, 0, 136, 136, 48), { fill: PAL.tealD, line: 5, seed: 630, grain: 0.3 });
  star(ctx, -58, -32, 26, { n: 5, inner: 0.45, fill: PAL.mustard, off: [0, 0] });
  text(ctx, rating, 22, -10, { font: '64px Slab', fill: PAL.white, align: 'center' });
  text(ctx, ulasan, 0, 56, { font: '600 40px Jost', fill: PAL.white, align: 'center' });
  text(ctx, 'ulasan', 0, 98, { font: '600 34px Jost', fill: PAL.white, align: 'center' });
  ctx.restore();
}

// ------------------------------------------------------------ transisi dan loop
export function irisMasuk(ctx, cx, cy, p, gambarBerikut) {
  const r = 2300 * p;
  ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, TAU); ctx.clip(); gambarBerikut(); ctx.restore();
  if (r > 0 && r < 2300) ink(ctx, ellipse(cx, cy, r, r, 80), 6, { closed: true, seed: 990 });
}
export function wipe(ctx, p, dari, gambarBerikut) {
  ctx.save(); ctx.beginPath();
  if (dari === 'bawah') ctx.rect(0, H * (1 - p), W, H * p); else if (dari === 'atas') ctx.rect(0, 0, W, H * p); else ctx.rect(0, 0, W * p, H);
  ctx.clip(); gambarBerikut(); ctx.restore();
  const tepi = dari === 'bawah' ? [[0, H * (1 - p)], [W, H * (1 - p)]] : dari === 'atas' ? [[0, H * p], [W, H * p]] : [[W * p, 0], [W * p, H]];
  if (p > 0 && p < 1) ink(ctx, tepi, 6, { seed: 991, taper: false });
}
// renderFilm yang menutup film dengan iris ke frame 0 (loopAt → loopEnd), supaya putaran ulang menyambung
export function denganLoop(renderSemua, loopAt, loopEnd, setClock) {
  return function renderFilm(ctx, t) {
    if (t >= loopEnd) { renderSemua(ctx, 0); return; }
    renderSemua(ctx, t);
    if (t >= loopAt) {
      const p = eio(seg(t, loopAt, loopEnd));
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.beginPath(); ctx.arc(540, 960, 2300 * p, 0, TAU); ctx.clip();
      renderSemua(ctx, 0); ctx.restore();
      setClock(t);
      if (p > 0 && p < 1) ink(ctx, ellipse(540, 960, 2300 * p, 2300 * p, 80), 6, { closed: true, seed: 992 });
    }
  };
}
