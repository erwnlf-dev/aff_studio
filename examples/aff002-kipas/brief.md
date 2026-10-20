HOOK: demonstrasi + pertanyaan. Frame 0: kipas cutout di tangan, angin sudah meniup poni penumpang KRL, kipas dilingkari tinta merah, "Kipas kecil, / angin kencang?" 150 px

# Brief: Mini Kipas Turbo Genggam LED 23000 RPM (41671303438)

**Gaya: `midcentury-toon`** (kit Slate `midcentury`: toon.js, chars.js + kit affiliate `engine/aff.js`). Alasan: gaya yang terbukti di Baru Tau dan aff001, dan bahasanya cocok untuk demo benda kecil ala film edukasi 1950-an: tangan yang berakting, tes tisu di depan kipas, kaca pembesar bertinta untuk isi motor, cap karet untuk bukti. Ringan di CPU.

**Produk:**
- Hero `kipas` (hitam-ungu) dari foto 0, crop 495,470,790,945. Cutout rembg `isnet-general-use`; teks penjual ("Kipas Turbo Portable", "UP to 10H", "100 Level Kipas") ada di latar dan ikut hilang, HP di belakang tidak terbawa. Cek mata `cutout_sheet.jpg`: tepi bersih, rumah motor utuh.
- Varian `kipas_abu` (abu-ungu) dari foto 2, crop 578,40,740,315, hanya di end card (290 px).
- **Ditolak:**
  - kipas lilac dari foto 0 (rumah motor hilang karena menyatu dengan HP lilac di belakangnya) dan dari foto 2 (badan semi-transparan),
  - foto 1 dan 4 (tulisan "3000mAh" tercetak di sel baterai, data 6000mAh),
  - foto 6 ("16900 r/min" tercetak, data 23.000 RPM),
  - foto 5 (USB-C, tidak ada di `key_features`),
  - foto 7 dan 8 (model foto, tangan/wajah).
- Angka "100" di layar kipas adalah tampilan produk sendiri (persen baterai, foto 2 "Tampilan Baterai"), bukan badge penjual.

**Benchmark:**
- **Dipelajari:**
  - *Baru Tau.* #003: cap karet bukti, tangan dengan antisipasi, slab caption, wipe blok warna, warna per bagian;
  - aff001 keset: hentakan produk setelah hening, demo yang dilabeli "ilustrasi", end card dengan varian;
  - film edukasi 1950-an (UPA): satu benda diuji di depan penonton (tes tisu di depan kipas), kaca pembesar untuk bagian dalam.
- **Tidak diambil:** garis kecepatan/motion blur palsu di produk, angka putaran yang berjalan (angka acak = TERLARANG 7), "turbo" dengan api/kilat, angka "10H"/"100 level"/"16900" dari foto penjual, harga dan diskon.

**Snapshot parameter:** variant_id `v_1fbf2a6b0bf1`. Suara "Erwin" (`p1y62Xa1WwNReXz59xPE`, sama dengan Baru Tau; EXP-04 belum dipilih).

**Data layar** (`data_layar.json`, persis): terjual "10RB+", rating "4,7", ulasan "26rb+", varian Warna 10, harga `null` (tidak tampil).

**compliance_note:** "Harga coret Rp199rb (-86%) terindikasi inflasi diskon: jangan tonjolkan '% diskon' di video. Rating 4.7 (terendah di shortlist); toko non-Mall." Dipatuhi: tanpa harga, harga coret, atau persen di video maupun teks post. Rating 4,7 ditulis persis di segel (tidak dibulatkan), tidak diucapkan dan tidak ditonjolkan; bukti utama adalah "10RB+ terjual". Kategori tidak diatur.

## Voiceover (vo.json, job 2026-10-20-bd860a)

- Durasi 18,88 s → `META.dur` = 19,18. 41 kata, 256 karakter.
- **Jendela sunyi terukur** (`vo.mp3`, ≥ 0,3 s): 2,50–3,08 · 5,24–5,80 · 6,30–6,64 · 8,52–9,12 · 11,38–11,96 · 14,20–14,74 · 16,40–16,98.
  - **Calon hening** (≥ 0,45 s): 2,53–3,05 · 5,27–5,77 · 8,55–9,09 · 11,41–11,93 · 14,23–14,71 · 16,43–16,95.
  - **Onset digeser:** "Desak-desakan" 3,02→3,08; "ini" 6,59→6,64; "Motornya" 8,61→9,12; "Enam" 11,44→11,96; "Ada" 16,96→16,98.
  - Catatan: "Udah" tercatat 14,157 padahal jendela sunyi 14,20–14,74 ada di dalam kata itu, jadi suaranya mulai ±14,74. Tidak ada cue di kata itu.
  - Jeda "…" setelah "Nah" hanya 0,34 s (6,30–6,64), di bawah 0,4. Karena itu hening diletakkan di jeda bagian sebelum "Nah…".
- **HENING = 5,27–5,77** (0,50 s, di dalam jendela 5,24–5,80, setelah "banget?"). Kipas mendarat di "Nah…" (kata 11, 5,83 s, frame 140); bunyi pertama frame 141.
- **PERLU DICEK telinga:** "RPM" (suara berlabel Inggris), "Desak-desakan".

## Blok arahan

```
TUJUAN:    detik 0–2,75: "kipas sekecil ini kok anginnya kencang?" sambil melihat poni tertiup rata; detik 3–5,3: ikut gerah di KRL;
           detik 5,83: lega waktu kipas keluar dari tote bag; akhir: klik link untuk pilih dari 10 warna
OUTPUT:    1080×1920, 24 fps, META.dur = 18,88 + 0,3 = 19,18 s, loop ke frame 0 (iris 18,91–19,14, frame ≥ 19,14 = renderSemua(0))
WAKTU:     hook 0–2,75 (14,3 %); masalah 2,75–5,708 (hening 5,27–5,77); produk 5,708–8,875; fitur ① 8,875–11,708;
           fitur ② 11,708–14,5; bukti 14,5–16,75; CTA 16,75–19,18. Demo pertama (angin naik) 0,21 s, turbo di "sekencang" 1,64 s;
           produk mendarat di kata 11 (5,83 s, 30 %). Potongan di jendela sunyi
LOOK:      midcentury-toon; latar per bagian = tempat di KRL: hook jendela gerbong (langit #B5C8DE, gedung #7F9CC0, kusen #FBF6EA);
           masalah dinding gerbong #F0B4A8 + jendela + kursi #3FA7A0 + palang/pegangan #C9CFCB (samping, lebar);
           produk dinding #8ACFC6 + jendela + tiang #C9CFCB + tote #E8B43A (tengah); fitur ① pintu gerbong #CBD08E + daun pintu #FBF6EA;
           fitur ② kain kursi #7F9CC0 berpola #5B789E; bukti papan info gabus #DDB47F + bingkai #7B4B2E; CTA #F4EAD5 + sinar #F3D37F.
           Benda hero = kipas cutout (selalu sama). Angin = garis tinta putih #FBF6EA bergulung (demo, berlabel ilustrasi).
           Tinta #2B2420; cap #B8452B di atas #FBF6EA. Font kit: Barlow Condensed 800 (hook 150 px, angka cap), Slab (teks kunci 92 px),
           Jost 600 (caption 68 px, label 30–44 px). Subjek ≥ 640 px: kipas 716–846 px (produk, ①, ②, CTA); kepala+bahu 760 px (hook);
           penumpang 1.075 px (masalah). Caption dasar y = 1.470; disclosure "Link afiliasi" 34 px di (60, 175) setiap frame
MOTION:    antisipasi 4–5 frame (jempol naik 14 px sebelum menekan, penumpang mundur 20 px sebelum mendesak, tangan cap naik 60 px);
           produk naik dari tas 3 frame eo + lewat 30 px + squash 1,08 × 0,92 (≤ 12 %); tisu: sudut 90°→178° dengan ombak 2 gelombang,
           amplitudo 26 px × angin; poni: sudut helai 90°→200° + kibas 0,25 rad 4 Hz × angin; rotor ilustrasi maks 18°/frame;
           pegas label back(·,1,8) 7 frame; sekunder (pegangan KRL, tas) 50–70 % jarak hero, mulai 3–5 frame kemudian; ambient < 5 %
           (gerbong goyang ±0,6°, gedung bergeser 40 px/s, dorongan kamera 1→1,04)
SHOTS:     7 shot, satu gerak hero per shot. Transisi: potong keras (hook→masalah 2,75; masalah→produk 5,708, kipas sudah terlihat naik),
           wipe dari konten (produk→① wipe kiri 8,55–8,875; ①→② wipe bawah 11,4–11,708; ②→bukti wipe atas 14,2–14,5),
           iris dari kipas (bukti→CTA 16,4–16,75), iris ke frame 0 (loop). Frame setelah transisi sudah berisi kipas/penumpang
TERLARANG: daftar BIBLE Baru Tau + A1–A7 affiliate + episode ini: tanpa garis kecepatan atau blur di kipas; tanpa angka RPM berjalan;
           tanpa sinar matahari/rays di adegan gerah (matahari = cakram datar); tanpa onomatope ("wush", "WOW"); tanpa "10H", "100 level",
           "16900" dari foto penjual; tanpa harga/diskon; tanpa logo KRL/KAI; demo angin, rotor, dan layar diberi label "ilustrasi"
QA:        audit_film.py (kontrak render, CUES ±1 frame terhadap kata_koreksi, hit +1 frame) → ledger; pratinjau lokal ≥ 2 putaran 16–24 momen
           + pratinjau Slate; BASELINE affiliate 1–20 di ledger; QA server: beku, loop ≤ 2/255, kedip, hening, kontras, LRA
```

## Tiga momen andalan

1. **Frame 0:**
   - wajah penumpang (June, kepala + bahu 760 px) di jendela KRL, poni dan rambut samping sudah tertiup ke kiri,
   - kipas hitam-ungu 540 px di tangan kanan bawah, dilingkari tinta merah, garis angin bergulung ke wajahnya,
   - teks hook "Kipas kecil," / "angin kencang?" (pelat mustard).

   Di 0,21 s jempol menekan tombol (antisipasi naik 14 px, 4 frame) dan angin naik satu tingkat. Di "sekencang" (1,64 s) angin turbo: poni rata ke belakang, butir keringat terlempar, mata terpejam lega.
2. **Produk (5,83 s):** setelah hening di gerbong yang padat, potong ke tote bag. Kipas melesat keluar dari mulut tas dan berhenti di "Nah…" dengan lewat 30 px dan squash 8 %. Di "ini" jempol menyalakan: tali tas berkibar.
3. **Tes tisu (9,1–10,9 s):** tangan menjepit selembar tisu tepat di depan ring kipas. Tisu menggantung lalu terangkat sampai rata dan berkibar di "RPM". Kaca pembesar menunjukkan rotor (ilustrasi) yang makin cepat.

## Storyboard

| Waktu | Di layar | Gerak hero | Teks kunci | Audio | Keluar |
|---|---|---|---|---|---|
| 0–2,75 Hook | Jendela KRL (langit biru, gedung bergeser). June close-up kiri (kepala (320, 930), 1,2×), kipas 330×537 di (770, 1.060) dipegang tangan dari kanan bawah | Jempol naik 14 px (f0–4), tekan f5 → angin 0,35→0,6 (6 frame eo); di "sekencang" (kata 4, f39) angin 1,0: helai poni 90°→200°, 3 butir keringat terlempar 160–260 px ke kiri (10 frame), mata lega | Kipas kecil, angin kencang? | klik tombol f6, desir angin naik, swish turbo f40; vibrafon + jentikan | Potong keras 2,75 |
| 2,75–5,708 Masalah | Gerbong samping: dinding pink, 2 jendela + matahari datar, palang + 4 pegangan, kursi toska. June 1,9× (1.075 px) memegang pegangan, tangan lain mengipas (2,6 Hz). Penumpang navy kiri + toska kanan | Di "Desak-desakan" (kata 6, f74) penumpang mundur 20 px (4 frame) lalu mendesak 70 px, June terjepit 0,96 × 1,03, pegangan berayun; di "gerah" (kata 9, f106) keringat jatuh 120 px dari dahi + kipasan tangan makin cepat. HENING 5,27–5,77: pose tahan, gerbong goyang ±0,6° | Gerah banget? | Desak (clack + scratch) f75; tetes keringat (pop) f107; musik tipis; berhenti 5,17; hening | Potong keras 5,708 (kipas sudah terlihat naik dari tas) |
| 5,708–8,875 Produk | Dinding toska + jendela + tiang. Tote mustard 600×520 di bawah. Kipas 430×700 di (540, 760) | Kipas naik dari mulut tas 3 frame, berhenti di "Nah…" (kata 11, f140), lewat 30 px + squash 1,08 × 0,92; tangan pegang dari kanan; di "ini" (kata 12, f159) jempol menekan → garis angin + tali tas berkibar; di "kipas" (kata 14, f174) pelat pop | Kipas turbo | Hentakan pertama setelah hening: stamp + clack + bell (f141); klik f160; desir | Wipe kiri 8,55–8,875 |
| 8,875–11,708 Fitur ① | Pintu KRL (daun pintu krem, kaca biru) di dinding avokad. Kipas 440×716 kiri bawah (400, 1.010). Kaca pembesar r 190 di (790, 640) | Di "Motornya" (kata 17, f219) kaca pembesar pop + garis putus-putus ke ring; rotor 7 bilah 2°→18°/frame (eio sampai "RPM"). Tangan dari atas menjepit tisu di depan ring: tisu 90°→178° di "RPM" (kata 22, f261), ombak 2 gelombang. Label "angin 20 m/s" pop 0,3 s kemudian | 23.000 RPM | Desir naik + whir rotor (pitch naik), cap kecil f262 | Wipe bawah 11,4–11,708 |
| 11,708–14,5 Fitur ② | Kain kursi biru berpola. Kipas close-up 520×846 (asli) di (380, 980). Kaca pembesar layar r 200 di (790, 800) | Di "Enam" (kata 23, f287) kaca pembesar pop menampilkan angka 1 (7 segmen) + ikon baterai; jempol menekan 5 kali (antisipasi 4 frame, interval 10 frame) → 2, 3, 4, 5, 6; tekan terakhir di "layar." (kata 28, f329). Garis angin bertambah per level | 6 level | Klik ×5 (pitch naik), tik angka; pluck rapat | Wipe atas 14,2–14,5 |
| 14,5–16,75 Bukti | Papan info stasiun (gabus + bingkai cokelat), kartu putih disemat 2 paku. Kipas 360×586 kiri bawah | Tangan + cap: antisipasi naik 60 px (5 frame), hentak 3 frame, mendarat di "sepuluh" (kata 31, f369) → "10RB+ / terjual"; di "lebih." (kata 33, f386) segel "★ 4,7 · 26rb+ ulasan" pop | — (cap = teks kunci) | Cap: stamp + clack + bell; segel pop | Iris dari kipas 16,4–16,75 |
| 16,75–19,18 CTA | Krem + sinar mustard. Kipas asli 440×716 di (400, 880); varian abu 230 px; kipas kertas 10 keping warna | Di "sepuluh" (kata 35, f412) keping warna membuka (stagger 2 frame) + varian abu pop + label "10 warna"; pelat "Cek warna di link" pop di "cek" (kata 37, f431); tangan menunjuk ke bawah lewat busur, tiba di "link" (kata 39, f439) | Cek warna di link | Kertas ×10 (tik), pop, bell di "link"; akor terselesaikan | Iris ke frame 0 (18,91–19,14) |

Tanpa suara: hook tertulis besar dan poni yang tertiup terlihat di thumbnail; setiap scene punya teks kunci ≤ 3 kata atau cap; caption tertanam ≤ 7 kata dengan satu kata disorot; kipas yang sama membawa cerita dari frame 0 sampai end card.
