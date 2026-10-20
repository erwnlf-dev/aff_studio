// Template "kartu": video produk dari foto penjual (doc 12 ADR-P05, prototipe).
//
// Semua isi dan angka datang dari isi.json (tools/siapkan_film.py: snapshot parameter, beat, timing kata, caption,
// palet) dan foto.json (foto sebagai data URI). Template ini tidak memuat angka spesifikasi sendiri selain tata letak
// kanvas 1080×1920. Murni fungsi dari t: tanpa Math.random, Date, atau timer (kontrak render Slate).

const isi = await (await fetch('./isi.json')).json();
const FOTO = await Promise.all(((await (await fetch('./foto.json')).json()).foto).map(f => new Promise((ok, gagal) => {
  const im = new Image();
  im.onload = () => ok(im);
  im.onerror = () => gagal(new Error('foto gagal dimuat'));
  im.src = f.src;
})));

const P = isi.params;
const W = 1080, H = 1920, FPS = 30, FRAME = 1 / FPS;
const PAL = isi.palet;
const ATAS = P['zona_aman.atas_px'];
const BAWAH = H - Math.max(...Object.keys(P).filter(k => /^zona_aman\..*\.bawah_px$/.test(k)).map(k => P[k]));
const KARTU = 780, KARTU_KECIL = 560, KARTU_Y = ATAS + 310, RADIUS = 40;
// blok teks kunci (≤ 2 baris) di antara label disclosure dan kartu; caption tepat di bawah kartu
const KUNCI_Y = ATAS + 165, CAPTION_Y = KARTU_Y + KARTU + 22;

// loop: false — video produk tidak dirancang menyambung ke frame 0 (QA Slate melewati cek loop)
export const META = { dur: isi.dur, kontras: isi.kontras, loop: false };
export const CUES = isi.dorong.map((i, n) => ({ id: 'sorot' + n, t: isi.kata[i].t0, kata: isi.kata[i].teks }));

// ---------------------------------------------------------------- easing

const klem = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sine = u => 0.5 - 0.5 * Math.cos(Math.PI * klem(u));
const keluarKubik = u => 1 - Math.pow(1 - klem(u), 3);
// pegas redaman 0,55: lewat sasaran sekali ±10–13 % lalu diam (BIBLE Baru Tau "slow in / slow out")
const pegas = u => { u = klem(u); return 1 - Math.exp(-5.2 * u) * Math.cos(7.5 * u); };

function dorongan(t, t0) {
  // punch-in kata disorot: naik 4 frame, kembali dalam ~0,45 s
  const x = t - t0;
  if (x < 0 || x > 0.6) return 0;
  return x < 4 * FRAME ? keluarKubik(x / (4 * FRAME)) : 1 - sine((x - 4 * FRAME) / 0.45);
}

// ---------------------------------------------------------------- gambar dasar

function teksBaris(ctx, teks, lebarMaks) {
  const kata = teks.split(/\s+/).filter(Boolean), baris = [];
  let cur = '';
  for (const k of kata) {
    const coba = cur ? cur + ' ' + k : k;
    if (ctx.measureText(coba).width > lebarMaks && cur) { baris.push(cur); cur = k; } else cur = coba;
  }
  if (cur) baris.push(cur);
  return baris;
}

function fotoCover(ctx, im, x, y, w, h, skala, fx, fy) {
  // foto mengisi kotak (cover), diperbesar `skala` ke arah titik fokus (fx, fy) dalam 0..1, jendela tetap di dalam foto
  const s0 = Math.max(w / im.width, h / im.height) * skala;
  const vw = w / s0, vh = h / s0;
  const cx = klem(fx * im.width, vw / 2, im.width - vw / 2);
  const cy = klem(fy * im.height, vh / 2, im.height - vh / 2);
  ctx.drawImage(im, cx - vw / 2, cy - vh / 2, vw, vh, x, y, w, h);
}

function latar(ctx, t) {
  ctx.fillStyle = PAL.latar;
  ctx.fillRect(0, 0, W, H);
  // panel lembut di belakang kartu; ambient < 5 % gerak hero, siklus utuh sepanjang film
  const geser = 6 * Math.sin(2 * Math.PI * t / isi.dur);
  ctx.fillStyle = PAL.latar_lembut;
  ctx.beginPath();
  ctx.roundRect(60, KARTU_Y - 24 + geser, W - 120, KARTU + 64, 64);
  ctx.fill();
}

function disclosure(ctx) {
  const fs = P['disclosure.font_px'];
  ctx.font = `600 ${fs}px Inter`;
  const w = ctx.measureText(isi.disclosure).width + fs;
  ctx.fillStyle = '#000000';
  ctx.beginPath();
  ctx.roundRect(48, ATAS + 8, w, fs * 1.5, fs * 0.75);
  ctx.fill();
  ctx.fillStyle = '#FFFFFF';
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  ctx.fillText(isi.disclosure, 48 + fs / 2, ATAS + 8 + fs * 0.75);
}

// ---------------------------------------------------------------- kartu produk

function kartu(ctx, b, t) {
  const im = FOTO[b.foto];
  const durB = b.t1 - b.t0, u = (t - b.t0) / durB;
  const zoomMaks = Math.min(P['motion.kenburns.zoom_maks'], 1 + P['motion.kenburns.zoom_per_detik'] * durB);
  let skala = 1 + (zoomMaks - 1) * sine(u);
  // beat panjang: potong keras ke crop detail di tengah beat (ganti visual tiap ≤ motion.ganti_visual_maks_detik)
  const detail = b.foto_penuh && durB > P['motion.ganti_visual_maks_detik'] && t >= b.t0 + durB / 2;
  if (detail) skala *= Math.min(1.25, Math.min(im.width, im.height) / KARTU);

  let punch = 0;
  const iB = isi.beats.indexOf(b);
  for (const i of isi.dorong) if (isi.kata[i].beat === iB) punch = Math.max(punch, dorongan(t, isi.kata[i].t0));
  const ukuran = (b.foto_penuh ? KARTU : KARTU_KECIL) * (1 + (P['motion.punch_in_kata_kunci'] - 1) * punch);
  const x = (W - ukuran) / 2, y = KARTU_Y + (KARTU - ukuran) / 2;

  ctx.save();
  ctx.shadowColor = 'rgba(0,0,0,0.35)';
  ctx.shadowBlur = 40;
  ctx.shadowOffsetY = 18;
  ctx.fillStyle = '#FFFFFF';
  ctx.beginPath();
  ctx.roundRect(x, y, ukuran, ukuran, RADIUS);
  ctx.fill();
  ctx.restore();

  ctx.save();
  ctx.beginPath();
  ctx.roundRect(x, y, ukuran, ukuran, RADIUS);
  ctx.clip();
  fotoCover(ctx, im, x, y, ukuran, ukuran, skala, b.fokus[0], b.fokus[1]);
  ctx.restore();
}

function teksKunci(ctx, b, t, iBeat) {
  if (!b.teks_kunci) return;
  const hook = iBeat === 0;
  const fs = Math.round(P['teks.kunci_font_px'] * (hook ? 1.6 : 1.3));
  // beat pertama sudah utuh di frame 0 (thumbnail); beat lain masuk dengan pegas dalam 7 frame
  const u = hook ? 1 : (t - b.t0) / (7 * FRAME);
  const s = hook ? 1 : 0.92 + 0.08 * pegas(u);
  ctx.save();
  ctx.globalAlpha = hook ? 1 : klem(u * 2);
  ctx.translate(W / 2, KUNCI_Y);
  ctx.scale(s, s);
  ctx.font = `${fs}px Lilita`;
  ctx.fillStyle = PAL.teks;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const baris = teksBaris(ctx, b.teks_kunci, W - 2 * 90).slice(0, 2);
  const tinggi = fs * 1.08;
  baris.forEach((s1, i) => ctx.fillText(s1, 0, (i - (baris.length - 1) / 2) * tinggi));
  ctx.restore();
}

function chipBukti(ctx, b, t) {
  const fs = Math.max(P['teks.kunci_font_px'] - 2, 56);
  b.bukti.forEach((teks, i) => {
    const u = (t - b.t0 - 0.25 - i * 4 * FRAME) / (8 * FRAME);
    if (u <= 0) return;
    ctx.save();
    ctx.font = `600 ${fs}px Inter`;
    const w = ctx.measureText(teks).width + fs * 1.1, h = fs * 1.6;
    // tanpa teks kunci: chip menempati blok teks kunci di atas kartu, jadi foto tidak tertutup
    const y = b.teks_kunci ? KARTU_Y + KARTU - 70 - (b.bukti.length - i) * (h + 18)
                           : KUNCI_Y - (b.bukti.length * (h + 14)) / 2 + i * (h + 14);
    ctx.translate(W / 2, y + h / 2);
    const s = 0.85 + 0.15 * pegas(u);
    ctx.scale(s, s);
    ctx.globalAlpha = klem(u * 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.roundRect(-w / 2, -h / 2, w, h, h / 2);
    ctx.fill();
    ctx.fillStyle = '#121216';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(teks, 0, 2);
    ctx.restore();
  });
}

function hargaTag(ctx, b, t) {
  if (!b.harga) return;
  const u = (t - b.t0 - 0.2) / (8 * FRAME);
  if (u <= 0) return;
  const fs = P['teks.kunci_font_px'] * 1.4;
  ctx.save();
  ctx.translate(W / 2, KARTU_Y + KARTU - 120);
  const s = 0.85 + 0.15 * pegas(u);
  ctx.scale(s, s);
  ctx.font = `${fs}px Lilita`;
  const w = ctx.measureText(b.harga.teks).width + fs;
  ctx.fillStyle = '#FFFFFF';
  ctx.beginPath();
  ctx.roundRect(-w / 2, -fs * 0.8, w, fs * 1.6, 24);
  ctx.fill();
  ctx.fillStyle = '#121216';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(b.harga.teks, 0, 0);
  ctx.font = `600 ${P['disclosure.font_px']}px Inter`;
  ctx.fillStyle = PAL.teks;
  ctx.fillText('harga per ' + b.harga.tanggal, 0, fs * 1.25);
  ctx.restore();
}

// ---------------------------------------------------------------- caption

function caption(ctx, t) {
  const gaya = P['caption.gaya'];
  if (gaya === 'tanpa') return;
  const g = isi.caption.find(c => t >= c.t0 && t < c.t1);
  if (!g) return;
  const fs = P['caption.font_px'];
  ctx.font = `600 ${fs}px Inter`;
  const spasi = ctx.measureText(' ').width, lebarMaks = W - 2 * 120;
  const baris = [[]];
  let lebar = 0;
  for (const i of g.kata) {
    const w = ctx.measureText(isi.kata[i].teks).width;
    if (lebar + w > lebarMaks && baris[baris.length - 1].length) { baris.push([]); lebar = 0; }
    baris[baris.length - 1].push({ i, w });
    lebar += w + spasi;
  }
  const tinggiBaris = fs * 1.2, pad = 26;
  const lebarBaris = baris.map(r => r.reduce((a, k) => a + k.w, 0) + spasi * (r.length - 1));
  const kotakW = Math.max(...lebarBaris) + 2 * pad, kotakH = baris.length * tinggiBaris + 2 * pad * 0.7;
  const y0 = Math.min(CAPTION_Y, BAWAH - 12 - kotakH);
  ctx.fillStyle = PAL.kotak_caption;
  ctx.beginPath();
  ctx.roundRect((W - kotakW) / 2, y0, kotakW, kotakH, 22);
  ctx.fill();
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  baris.forEach((r, n) => {
    let x = (W - lebarBaris[n]) / 2;
    const y = y0 + pad * 0.7 + tinggiBaris * (n + 0.5);
    for (const { i, w } of r) {
      const k = isi.kata[i];
      const tampak = gaya !== 'kata_per_kata' || t >= k.t0;
      if (tampak) {
        ctx.fillStyle = g.sorot.includes(i) ? P['caption.warna_sorot'] : '#FFFFFF';
        ctx.fillText(k.teks, x, y);
      }
      x += w + spasi;
    }
  });
}

// ---------------------------------------------------------------- film

export function renderFilm(ctx, t) {
  let iBeat = 0;
  for (let i = 0; i < isi.beats.length; i++) if (t >= isi.beats[i].t0) iBeat = i;
  const b = isi.beats[iBeat];
  latar(ctx, t);
  kartu(ctx, b, t);
  teksKunci(ctx, b, t, iBeat);
  if (b.bukti.length) chipBukti(ctx, b, t);
  hargaTag(ctx, b, t);
  caption(ctx, t);
  disclosure(ctx);
}
