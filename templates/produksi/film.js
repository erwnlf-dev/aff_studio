// Affiliate — {{NAMA}} (Shopee {{ID}}). Disutradarai per produk (aff_studio ADR-P06, series/BIBLE.md).
// Gaya {{GAYA}} (kit Slate `midcentury` + kit affiliate engine/aff.js). 1080x1920, 24 fps. Murni fungsi t.
// Timing: vo.json job {{JOB}}, onset dikoreksi (kata_koreksi.json, tools/sunyi.py).
import { PAL, setClock, shape, plane, ink, rays, ellipse, rect, rrect, spline, star, text, measure, xform,
  paperFinish, dashed, lerp, seg, ss, eo, eio, TAU } from './engine/toon.js';
import { pop, E_in, kf, squash, cam, muatFoto, produk, tanganDi, pelat, teksKunci, labelIlustrasi, disclosure,
  buatCaption, capKaret, cetakCap, segelRating, irisMasuk, wipe, denganLoop } from './engine/aff.js';
import { FOTO } from './aset/foto.js';

// konstanta lokal: CUES dan META tidak boleh bergantung pada impor (audit_film mengganti impor dengan stub)
const W = 1080, H = 1920, FPS = 24;
// dari `python3 tools/produksi.py <folder> kata` (kata_koreksi.json): [mulai, selesai, teks]
const KATA = [];

// setiap hentakan/pendaratan: [id, frame, indeks kata]; frame = round(onset × 24) dari KATA
const CUE_LIST = [];
export const CUES = [].concat(CUE_LIST.map(([id, f, k]) => ({ id, t: f / FPS, kata: k, teks: KATA[k][2] })));
const C = {}; CUES.forEach(c => { C[c.id] = c.t; });

export const META = {
  dur: 0,                                   // durasi VO + 0,3
  kontras: [['#2B2420', '#FBF6EA'], ['#2B2420', '#F4EAD5'], ['#2B2420', '#E8B43A'], ['#B8452B', '#FBF6EA']],
};
const LOOP_AT = 0, LOOP_END = 0;            // iris ke frame 0: ±0,27 s sebelum META.dur

await muatFoto(FOTO);

// caption: [kata awal, kata akhir, kata disorot]; DIGIT = {indeks kata: 'angka sebagai digit'}
const CAP = [];
const DIGIT = {};
const caption = buatCaption(KATA, CAP, { digit: DIGIT, dur: META.dur });

// ------------------------------------------------------------ adegan (satu fungsi per bagian storyboard)
// Setiap adegan: latar = tempat dari cerita (warna sendiri), produk sebagai hero (produk(ctx, nama, …, {cahaya: <warna latar>})),
// satu gerak hero berangka, tangan yang berakting, teks kunci ≤ 3 kata. End card: produk(…, {asli: true}).
function sceneHook(ctx, t) {
  ctx.fillStyle = PAL.paper; ctx.fillRect(0, 0, W, H);
}

function renderSemua(ctx, t) {
  setClock(t);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  sceneHook(ctx, t);
  caption(ctx, t);
  disclosure(ctx);
  paperFinish(ctx, W, H, 1);
}
export const renderFilm = denganLoop(renderSemua, LOOP_AT, LOOP_END, setClock);
