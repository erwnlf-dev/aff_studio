# Ledger critic loop — mini kipas turbo (41671303438)

## Audit numerik sebelum putaran 1 (`produksi.py audit`)

```
lolos kontrak render: tanpa Math.random/Date/timer/font sendiri; timing kata dari kata_koreksi.json (41 kata)
lolos 1 cue tanpa kata (nyala, frame 5) + 15 cue dengan kata: selisih −0,4 … +0,5 frame (batas ±1)
audit_film: 17 lolos, 0 gagal (score.json belum ada)
```

## Putaran 1 — `pratinjau_r1.jpg` (24 momen, termasuk frame setelah setiap transisi: 2,75 · 5,708 · 8,875 · 11,708 · 14,5 · 16,75) + `pratinjau_r1_zoom.jpg`

**Cek TERLARANG:**
- Tanpa glow, partikel dekoratif, gradien polos, atau teks karangan. Teks layar hanya hook, teks kunci, cap/segel dari data, "angin 20 m/s" (fitur:0), "10 warna" (varian), dan "ilustrasi".
- Matahari di jendela gerbong berupa cakram datar tanpa sinar. Sinar mustard hanya di end card (aksen satu kali).
- Garis angin adalah demonstrasi fitur (BIBLE affiliate: "garis angin + rambut tertiup") dan berlabel "ilustrasi". Tidak ada garis kecepatan pada gerak kipas.
- Teks penjual tidak ada: cutout bersih. Angka "100" di layar kipas adalah tampilan produk (persen baterai).

**Masalah, urut dari yang terbesar:**

1. **Frame 137–212 (5,71–8,83 s): tote bag berupa gumpalan segi delapan 640×600 px.** Spline di atas 4 titik membulatkan sudutnya, jadi tidak terbaca sebagai tas dan menutup 32 % frame. → Tote trapesium bersisi lurus 528–604 × 520 px, keliman atas 50 px bertusuk jelujur, dua lipatan kain, dua tali (kiri ke bahu, kanan ke belakang tiang), dan mulut gelap 524 × 68.
2. **Frame 0–65 (hook): demo angin tidak terbaca di ukuran thumbnail.** Garis angin tinta 14 px + putih 7 px, 4 arus, dan potongan yang terlihat hanya 22–47 % jalur. Di frame 0 angin 0,35, jadi poni baru terangkat ±40 px. → Garis 22/12 px, 5 arus selebar 380 px, potongan 38–68 % jalur, gulungan di ujung 20 px; angin frame 0 = 0,5, setelah tekan 0,7, turbo 1,0.
3. **Frame 0–65, 137–212, 281–335: jempol berupa kapsul tinta 47 px, terlalu tebal untuk tombol 30 px.** → 34/25 px × skala, kuku 7 px.

**Catatan untuk putaran berikutnya:**
- CTA 16,75–17,95: 40 % atas frame kosong sampai pelat CTA pop di "cek"; keping warna dan tangan menumpuk di kanan; label "10 warna" kecil.
- Frame 14,5 (setelah wipe ke bukti): kartu masih kosong. Kipas sudah ada, jadi BASELINE 5 tetap lolos.
- Masalah: tangan June yang mengipas terbaca seperti melambai di ukuran kecil.

## Putaran 2 — `pratinjau_r2.jpg` (22 momen)

**Perbaikan putaran 1 terkonfirmasi:**
- Frame 141–212: tote terbaca sebagai tas kanvas (keliman, tali, mulut gelap), dan kipas keluar dari mulutnya.
- Frame 0–42: garis angin terlihat di ukuran thumbnail (5 arus + gulungan).
- Jempol ramping dan tidak menutup layar "100".

**Masalah, urut dari yang terbesar:**

1. **Frame 0–65 (hook): garis angin menutupi wajah June.** Di 1,0–1,75 s, 3 dari 5 arus lewat di atas mata dan mulut, jadi ekspresi lega di "sekencang" (frame 40) tidak terbaca. → Arus digambar di belakang June, dan ujungnya digeser ke (−20, 820). Angin terlihat di celah kipas–wajah (x 460–700) dan keluar lagi di kiri kepala; poni dan rambut yang tertiup jadi buktinya.
2. **Frame 402–431 (CTA 16,75–17,95): 40 % atas frame kosong sampai pelat pop di "cek".** Keping warna (poros 850, 1.150) dan tangan penunjuk menumpuk di x 650–950, y 950–1.250; label "10 warna" 50 px. → Pelat CTA pop di 16,83 dan berdenyut di "cek" dan "link"; poros keping naik ke (850, 960) dengan ujung di y 650–700; label 56 px di (820, 580); tangan masuk dari kanan bawah di bawah keping (ujung y 1.150→1.250, busur 50 px).

**Catatan:** frame 136 (5,71 s) caption memudar di hening, dan itu benar (caption terakhir masalah selesai 5,74 s). Tangan June yang mengipas sekarang terbaca sebagai mengipas/mengusap dahi.

## Putaran 3 — `pratinjau_r3.jpg` (22 momen, termasuk iris loop 18,95 dan frame ≥ 19,14 = frame 0)

**Perbaikan putaran 2 terkonfirmasi:**
- Frame 30–58: wajah June bersih, dan mata terpejam + senyum di "sekencang" terbaca.
- Angin terlihat di celah kipas–wajah dan keluar di kiri kepala.
- CTA: pelat sudah ada sejak 16,83 s, keping warna di y 650–960, dan tangan menunjuk di bawahnya.

**Masalah, urut dari yang terbesar:**

1. **Zona aman kanan (≤ 940):**
   - Kaca pembesar fitur ① (pusat 790, r 185 + bingkai 18) sampai x 993 di frame 219–281.
   - Kaca pembesar fitur ② (pusat 800, r 195 + 18) sampai x 1.013 di frame 287–348.
   - Label "10 warna" (56 px, lebar ±273) sampai x 957 di frame 420–460.

   Di Shopee/TikTok kolom ikon kanan menutup x > 940 di y 800–1.500. → LUP4 ke (735, 690), tepi bingkai 938; kipas fitur ② ke x 340 dan LUP5 ke (730, 790) r 190, tepi 938; label ke x 790, tepi 927. Gagang kaca pembesar (kayu, bukan teks) tetap keluar sampai ±1.000, dicatat.

**Catatan:** frame 348 (14,5 s, setelah wipe ke bukti) kartu masih kosong selama 0,45 s sebelum cap datang. Kipas dan papan sudah ada, jadi dibiarkan sebagai antisipasi.

## Putaran 4 (akhir) — `pratinjau_r4.jpg` (24 momen di setiap cue +1 frame dan frame setelah transisi) + `pratinjau_r4_potong.jpg` (frame 137–140) + `pratinjau_slate.jpg` (renderer Slate, paritas)

**Perbaikan putaran 3 terkonfirmasi:**
- Frame 262: kaca pembesar rotor di x 532–938.
- Frame 330: kaca pembesar layar di x 522–938.
- Frame 440: label "10 warna" di dalam zona aman.

**Frame setelah transisi:**
- 66: June di gerbong.
- 137: kipas sudah terlihat naik dari mulut tote, y 860, setengah bawahnya masih tertutup tas.
- 213: kipas + tisu + tangan.
- 281: kipas close-up + tangan.
- 348: kipas + papan.
- 402: kipas end card.

**Sisa kecil (tidak diperbaiki):** frame 40 (1,667 s) adalah frame peralihan gerah→lega, ada satu butir keringat melintas di tengah wajah selama 4 frame. Itu bagian dari aksi terlempar.

**Paritas:** pratinjau Slate (font kit, `aset/foto.js`, `engine/aff.js`) sama dengan pratinjau lokal di 10 momen.

### Perbandingan BASELINE affiliate (berdampingan dengan Baru Tau #003 `final_sheet.jpg` dan aff001 `final_sheet.jpg`)

| # | Butir | Video ini | aff001 / #003 |
|---|---|---|---|
| 1 | Frame 0 thumbnail utuh | ✔ kipas cutout 330×537 dilingkari tinta merah 8 px; hook "Kipas kecil, / angin kencang?" 150 px (4 kata, pelat mustard); poni June sudah tertiup (angin 0,5) + keringat | aff001: keset + gayung + tetes dilingkari |
| 2 | Hook 1 detik tanpa suara | ✔ aksi pertama: jempol antisipasi f1–4, tekan f5 (0,21 s); turbo f39; hook selesai 2,75 s (14,3 %) | aff001 0,06 s / 12 % |
| 3 | Tangan/karakter berakting | ✔ June close-up (gerah → lega, keringat terlempar), June di gerbong (pegangan, mengipas 2,6→3,6 Hz, terjepit 0,96×1,03), penumpang mendesak (mundur 20 px 4 frame → maju 70 px), tangan menarik kipas dari tas, jempol (antisipasi 4 frame ×7), tangan menjepit tisu, tangan cap (antisipasi 5 frame), tangan menunjuk (busur 50 px) | aff001: tangan + kaki; #003: tangan |
| 4 | Warna + komposisi per bagian | ✔ 7 latar/tempat: jendela gerbong (krem + langit biru, close-up), gerbong lebar (pink), dinding toska + tote (tengah), pintu avokad (kipas kiri + kaca pembesar kanan), kain kursi biru (close-up + kaca pembesar), papan gabus (kartu atas + kipas kiri bawah), krem + sinar (end card) | aff001: 7 |
| 5 | Transisi dari konten, subjek setelah transisi | ✔ potong keras ×2, wipe ×3, iris ×2; frame 66, 137, 213, 281, 348, 402 berisi subjek | ✔ |
| 6 | Subjek ≥ 640 px | ✔ kipas 699 (produk), 716 (①), 846 (②), 716 (CTA); June 800+ (hook), 1.075 (masalah); bukti: kipas 618 + kartu cap 700×300 (bukan scene wajib produk) | aff001 bukti 508 |
| 7 | Tanpa diam > 0,5 s | QA server (gedung bergeser 70–90 px/s, angin, kamera 1→1,04 di setiap adegan) | |
| 8 | Caption | ✔ Jost 600 68 px, 3–7 kata/layar, 1 kata disorot, dasar y 1.470; "23.000", "6", "10" sebagai digit (kata 18–21 digabung jadi satu token) | ✔ |
| 9 | Momen puncak | ✔ hening 5,27–5,77 (0,50 s, di jendela sunyi terukur 5,24–5,80); kipas berhenti di "Nah…" frame 140, hentakan frame 141, tampil 3,0 s | aff001 0,52 s |
| 10 | End card | ✔ kipas asli 716 px + varian abu 312 px + 10 keping warna; CTA "Cek warna di link" 80 px (pelat sejak 16,83 s, 2,3 s); disclosure; tanpa harga; loop iris ke frame 0 | ✔ |
| 11 | Musik | ✔ 7 aransemen (F6/Gm7 · Am–E7 + rel · F–Bb–Gm–C + ride · Cmaj7 woodblock/celesta · Dm–Gm delapan-an · G swing · akor penutup), motif 3 nada pembuka/penutup di celah VO, 16 hit + 40-an foley, semua hit +1,0 frame; level per bagian 0,22–1,9; LRA → QA server | aff001 LRA 1,5 |
| 12 | Klaim bersumber | ✔ `naskah` lolos (nama, fitur:0–2, masalah, terjual, rating, ulasan, varian, ajakan); label "angin 20 m/s" = fitur:0 | ✔ |
| 13 | Kedip/kontras | QA server (META.kontras 6 pasangan); angka LED berganti 5× dalam 1,6 s (≤ 3/s), luas < 3 % frame | |
| 14 | Audit numerik | ✔ 33 lolos, 0 gagal | ✔ |
| 15 | Tanpa teks penjual | ✔ semua foto lewat cutout; "Kipas Turbo Portable"/"UP to 10H"/"100 Level"/"16900 r/min" tidak tampil; "100" di layar = tampilan produk | ✔ |
| 16 | Tanpa foto utuh/model | ✔ foto 7–8 (model) tidak dipakai | ✔ |
| 17 | Demo fitur digambar | ✔ angin + poni (hook), tes tisu + rotor di kaca pembesar (①), layar 7 segmen 1→6 + jempol (②), semuanya berlabel "ilustrasi" | ✔ |
| 18 | Disclosure | ✔ tag "Link afiliasi" 34 px setiap frame, tinta di atas #FBF6EA | ✔ |
| 19 | Compliance data | ✔ tanpa harga/coret/persen; "10RB+", "4,7", "26rb+" persis dari data_layar; compliance_note dicatat di brief | ✔ |
| 20 | Kategori diatur | ✔ tidak berlaku (Elektronik > Kipas Portable, `kategori_diatur` false) | |

**Lebih baik dari baseline:**
- Detail lokal Indonesia: pegangan gantung KRL, kursi panjang, desak-desakan, papan info stasiun.
- Demo yang layak diulang (tes tisu: tisu dari menggantung menjadi rata dan berkibar) di 9,1–10,9 s, yaitu 57 % durasi, sebelum 75 %.

Keputusan: semua butir WAJIB ✔ atau diukur QA server → boleh render.

## Render

| Render | Hasil QA | Perubahan sesudahnya |
|---|---|---|
| 1 (`final_r1.mp4`) | lolos; LRA 1,8; sinkron `nyala` +93 ms, `ini` +110, `layar` +106, `link` +140, `segel` −37, `warna` −33 | Hentakan di tengah kata dibuka dengan clack 1,15 + click 1,0. Musik mengembang di 4 celah VO (vibrafon + bass + kick). Level bagian 0,14–2,3 (masalah lebih tipis, produk/CTA lebih penuh) |
| 2 (`final_r2.mp4`) | lolos; LRA 2,0; `nyala` sinkron; sisa `ini` +111, `rpm` +124, `layar` +110, `link` +140 | Tekan tombol `ini` dipindah dari kata "ini" (frame 159) ke celah sunyi 6,30–6,64 (frame 153, cue tanpa kata; pratinjau `pratinjau_r5_ini.jpg`: jempol naik 6,25, tekan 6,375, angin 6,42). Clack `rpm`/`layar`/`link` 1,3. Celah VO lebih penuh (1,4–1,6). Level 0,1–2,3 |
| 3 (final, `final.mp4`) | **lolos**; LRA 2,2; `ini` sinkron; sisa `rpm` +124 ms, `enam` +148, `layar` +110, `link` +140, `segel` −37, `warna` −33 | Berhenti (batas 3 render). Sisa peringatan dijelaskan di `cek_akhir.md` |
