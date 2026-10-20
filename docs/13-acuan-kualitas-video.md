# 13 — Acuan kualitas video

Kumpulan acuan untuk membuat video affiliate setara output *Baru Tau.*. Aturan yang mengikat ada di `series/BIBLE.md` dan `series/BASELINE.md`; dokumen ini mencatat **sumbernya**, aturan yang diambil, dan cara menyelesaikan aturan yang bertentangan. Disusun 20 Oktober 2026, setelah uji template `kartu` dinilai jelek oleh pemilik.

Label sumber:
- **[RESMI]**: panduan platform atau studi yang dipesan platform.
- **[DATA]**: pengukuran pihak ketiga.
- **[PRAKTISI]**: repo/skill dari praktisi, tanpa data.
- **[LOKAL]**: file di server ini yang sudah terbukti di produksi.

## 1. Urutan prioritas kalau aturan bertentangan

1. **Catatan pemilik dan BASELINE/BIBLE Baru Tau [LOKAL].** Ini standar yang sudah disetujui pemilik dan terbukti di #001–#003.
2. **Panduan resmi platform [RESMI].**
3. **Data pihak ketiga [DATA].**
4. **Skill dan repo praktisi [PRAKTISI].**

**Konflik yang sudah diputuskan:**

| Topik | Skill/repo praktisi | Baru Tau | Dipakai |
|---|---|---|---|
| Latar | "Never a flat solid background": blob mesh gradien + grade + grain + vignette | Gradien polos dan glow TERLARANG; latar = tempat dari cerita | **Baru Tau.** Latar digambar sebagai tempat. Tekstur dari gaya (`paperFinish` kit midcentury), bukan grain/vignette generik |
| Glow | Boleh pada satu elemen hero | TERLARANG | **Baru Tau** |
| Ken Burns | Wajib di setiap still | Tidak relevan; tidak ada still, semua digambar | **Baru Tau.** Foto hanya sebagai cutout produk, digerakkan sebagai benda (squash, pegas), bukan zoom pelan |
| SFX | Whoosh mulai 2–3 frame **sebelum** visual mendarat | Hentakan 1 frame **setelah** gambar | **Keduanya, untuk bunyi yang berbeda.** Whoosh/riser (bunyi antisipasi) mulai 2–3 frame sebelum benda mendarat; bunyi benturan (cap, klik, pop) 1 frame setelahnya |
| Diam | "Holds": ≥ 3 momen diam 15–20 frame ("constant motion reads amateur") | Tidak ada diam > 0,5 detik (QA) | **Keduanya.** Hold = benda hero diam, tapi ambient tetap hidup (< 5% gerak hero) supaya tidak terdeteksi beku. Hold maks 0,5 detik total diam di layar |
| fps | 30 | 24 | **24** (animasi terbatas, tabel gerak Baru Tau ditulis dalam frame 24) |

## 2. Metode: video disutradarai, bukan diisi template

| Sumber | Yang diambil |
|---|---|
| **[LOKAL]** `baru-tau-autopilot/CLAUDE.md` Mode PRODUKSI langkah 3–13; `episodes/003/brief.md` dan `ledger.md` | Brief 8 baris berangka (TUJUAN, OUTPUT, WAKTU, LOOK, MOTION, SHOTS, TERLARANG, QA); tiga momen andalan; storyboard dengan gerak hero (benda, jarak px, durasi frame, kata `vo.json`); critic loop: audit numerik lalu pratinjau 16–24 momen, 1–2 perbaikan per putaran dengan nomor frame (#003: 5 putaran); perbandingan contact sheet dengan baseline |
| **[LOKAL]** `/data/apps/lemo-opuscar/DIRECTOR.md` | Film dinilai berurutan: **suara, ritme, kamera, penyutradaraan**. Pilih **benchmark** dulu (yang dipelajari / yang tidak diambil). Satu subjek, satu tujuan, satu belokan. Hook ≤ 3 detik. Satu "native move" di puncak. Treatment dengan 3 calon struktur sebelum menggambar. Setiap aksi punya bunyi, ≥ 2 hening. Teks tampil ≥ huruf/15 + 1,5 detik. Subjek ≥ ⅓ tinggi frame di momen kunci |
| **[PRAKTISI]** claude-motion — https://github.com/whaleyxbt/claude-motion (dirujuk DECISIONS Baru Tau #1) | Satu timeline menggerakkan gambar dan suara. Skill `review-loop`: render, lihat frame, perbaiki. Frame 0 tidak boleh kosong (jadi thumbnail). Satu momen hero per video. Transisi dimotivasi benda di layar, bukan wipe generik |
| **[PRAKTISI]** Skill `remotion-motion-graphics` (sesi ini; salinan di `/data/apps/video-maker/references/claude-remotion-skill/`) | Wajib render → ambil frame → lihat → perbaiki → render ulang; jangan pernah menyerahkan render yang belum dilihat. Daftar cek sebelum serah (§4) |

## 3. Gerak, tipografi, ritme

**[LOKAL] BIBLE Baru Tau "Gerak dalam angka"** (berlaku penuh):
- antisipasi 4–5 frame,
- squash 1,25 × 0,7 dan stretch 0,85 × 1,28,
- pegas redaman 0,55,
- busur ≥ 10% jarak,
- gerak sekunder 50–70% jarak hero, mulai 3–5 frame kemudian,
- ambient < 5%,
- hentakan ±1 frame dari kata.

**[PRAKTISI] Angka pelengkap** (claude-motion, skill remotion), dipakai bila BIBLE Baru Tau tidak mengatur:
- **Easing:**
  - masuk `cubic-bezier(0.16, 1, 0.3, 1)` (easeOutExpo),
  - pindah antar-keadaan `(0.65, 0, 0.35, 1)`,
  - keluar `(0.6, 0, 0.9, 0.35)`,
  - mendarat dengan overshoot `(0.55, 0, 0.2, 1.12)`.
- **Pegas** (damping/stiffness/mass): bawaan 14/140/0,8; pop 9–11/200–230/0,7; elastis 8/200 paling banyak sekali per video.
- **Masuk dan keluar:**
  - masuk menganimasikan 2–3 properti sekaligus (posisi + skala + opasitas), tidak boleh fade saja,
  - keluar ≈ setengah durasi masuk (10 vs 20 frame).
- **Stagger:** kata 3 frame (0,09 detik), chip/daftar 4–6 frame, blok besar 6 frame. Tidak ada yang masuk serentak (sama dengan TERLARANG 6 Baru Tau).
- **Ritme:**
  - HENTAK → tahan → bangun,
  - ada yang bergerak dalam 15 frame pertama,
  - elemen visual baru paling lambat setiap 90 frame (3,75 detik di 24 fps).
- **Tipografi:**
  - teks hero 80–140 px (Baru Tau: hook ≥ 150 px di frame 0), tebal 600–800, tracking −0,02 s.d. −0,03 em, satu kata disorot per judul,
  - maksimal 3 keluarga font (font kit Slate),
  - uji HP: pesan kunci tetap terbaca di lebar 360 px,
  - konten > 60 px dari tepi.
- **Waktu baca:** ≥ 1 detik untuk frasa pendek, plus 0,25 detik per kata di atas tiga; baris terakhir ≥ 2 detik; teks yang harus dibaca tidak bergerak.

## 4. Struktur video produk (platform dan data)

- **[RESMI] TikTok Creative best practices:**
  - proposisi konten di 3 detik pertama, hook di 6 detik pertama,
  - teks di layar 5–10 kata per detik,
  - di dalam zona aman,
  - pakai suara, akhiri dengan CTA yang jelas.

  Sumber: https://ads.tiktok.com/help/article/creative-best-practices
- **[RESMI, studi pesanan platform] TikTok top-performing ads:**
  - 90% dampak ingatan iklan terjadi di 6 detik pertama,
  - produk di layar: +65% afinitas merek, +25% ingatan (Lumen 2021),
  - kartu CTA: +45% ingatan,
  - 88% pengguna menyebut suara penting (Kantar 2022).

  Sumber: https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads
- **[DATA] Playhead, 19 video viral TikTok Shop** (3,8–39 juta views, Mei–September 2026; sampel kecil, korelasional):
  - produk pertama terlihat di median **0,07 detik** (15/19 dalam 1 detik),
  - bukti/manfaat di median **2,73 detik**,
  - 14/19 tanpa wajah; video tanpa wajah median 13,5 detik, 13/14 tetap jalan tanpa suara,
  - 16/19 hook memakai ≥ 2 saluran (gambar, suara, teks, bunyi),
  - CTA di 12% terakhir.

  Sumber: https://tryplayhead.com/blog/tiktok-shop-hooks
- **[DATA] OpusClip, 34.635 klip:** hook "pamer produk/hasil" peringkat pertama, sekitar 2× views hook terburuk. Sumber: https://www.opus.pro/blog/tiktok-hooks-that-go-viral-2026
- **[RESMI, pesanan] Accenture/TikTok Shoppertainment 2024 (SEA, termasuk Indonesia):** sekitar 79% konsumen lebih terpengaruh konten non-promosi (ulasan, demo) daripada iklan terang-terangan. Sumber: https://iabseaindia.com/wp-content/uploads/2024/10/sea-shoppertainment-playbook-1.pdf
- **[PRAKTISI] Blog Shopee Video:** 12–20 detik, buka dengan keunggulan produk. Sumber: https://shopee.co.id/inspirasi-shopee/video-promosi-produk/

**Yang dipakai di BIBLE:**
- produk terlihat di frame 0,
- manfaat/demo pertama terlihat sebelum detik 3,
- durasi 15–25 detik (bawaan 20),
- cerita jalan tanpa suara,
- terasa seperti demo, bukan iklan,
- CTA di akhir.

**Belum ada data** untuk frekuensi potongan, ukuran/posisi teks di iklan toko terbaik, atau norma BPM; angka di BIBLE untuk hal-hal itu berasal dari Baru Tau.

## 5. Zona aman

[LOKAL, belum diverifikasi ke platform] `/data/apps/video-maker/config/platforms.json`, px di kanvas 1080×1920:

| Platform | Atas | Bawah | Kiri | Kanan |
|---|---|---|---|---|
| TikTok | 150 | 320 | 60 | 140 |
| Reels | 220 | 450 | 70 | 70 |
| Shorts | 120 | 280 | 60 | 120 |
| Threads | 250 | 670 | 65 | 65 |

Baru Tau memakai caption di atas y = 1480 (440 dari bawah) untuk Threads. Shopee Video belum diukur; sementara memakai angka TikTok (registry `zona_aman.*`).

## 6. Foto penjual → produk premium (CPU)

- **[DATA] Penghapus latar, uji CPU tanpa GPU:**

  | Model | Waktu per foto | RAM | Catatan |
  |---|---|---|---|
  | rembg `u2net` | 0,12 detik | 2,1 GB | |
  | rembg `isnet-general-use` | 0,33 detik | 2,8 GB | tepi sedikit lebih baik |
  | `isnet-general-use` + ViTMatte (`-vm`) | ±1,7 detik | | tepi terbaik |

  - Hindari `-ppm`; pakai `-dc` untuk menghapus halo warna.
  - Produk transparan/kaca sering gagal.
  - Lisensi u2net/isnet: Apache-2.0. BRIA tidak boleh (CC BY-NC).

  Sumber: https://www.creativeainews.com/articles/rembg-background-removal-models-tested-2026/
- **Urutan menangani teks penjual (usulan, belum diuji di server):**
  1. Pilih foto paling bersih dari 3–9 foto, crop menjauhi teks.
  2. Cutout dengan rembg; kebanyakan teks penjual ada di latar, jadi ikut hilang.
  3. Sisa kecil dibersihkan dengan inpaint (OpenCV Telea atau LaMa) setelah dideteksi OCR.
  4. Foto dengan teks **di atas produk** ditolak.
- **Menyatukan cutout dengan dunia gambar:**
  - bayangan kontak cokelat hangat, bukan hitam (kit `3d-lite`: opasitas 0,7 dan 0,38),
  - garis tinta/registrasi gaya episode di tepi cutout (diuji di pratinjau),
  - satu grade warna halus untuk menyamakan foto yang berbeda-beda.

## 7. Suara

- **[RESMI]** Pakai suara; idealnya dirancang untuk video itu sendiri. Musik +120% awareness pada iklan sound-on (Kantar 2021); bunyi merek khas menaikkan keterkaitan merek > 8× dibanding logo (Ipsos 2020). Sumber: https://ads.tiktok.com/business/en-US/blog/evolution-of-sound-volume-1
- **[LOKAL] BIBLE Baru Tau "Suara" + rantai mix Slate:**
  - partitur per bagian,
  - dua hening di dalam jeda VO,
  - foley > 150 Hz, hentakan 3–6 dB di atas musik,
  - ducking 7 dB, −14 LUFS.
- **[PRAKTISI]**
  - Riser masuk ke potongan, bass hit tepat di potongan.
  - Potongan di kelipatan `frame per ketukan = fps × 60 / BPM`.
  - Musik sekitar −18 dB di bawah SFX/VO.
  - Kit SFX 10 bunyi cukup (2 whoosh, 2 klik, riser, bass hit, shimmer, tick, pop, reverse swoosh); `slate_score.py` sudah menyintesisnya.
- **[RESMI via panduan sekunder] Lisensi:** konten bisnis/afiliasi di TikTok terbatas pada Commercial Music Library. Paling aman: musik sintesis sendiri (kunci `musik.sumber`). Sumber: https://www.soundstripe.com/blogs/tiktok-music-licensing-rules

## 8. Library gaya: mana yang cocok untuk produk

[LOKAL] `/data/apps/lemo-opuscar/styles/` (52 gaya; indeks `styles/README.md`) dan kit Slate `/data/apps/slate-studio/kits/`.

| Gaya | Cocok untuk | Catatan |
|---|---|---|
| `midcentury-toon` | Semua; terbukti di Baru Tau, kit sudah di Slate (tangan `drawHand`, tinta, bentuk, `paperFinish`) | Pilihan pertama untuk video pertama |
| `paper-popup`, `crayon-book` | Produk rumah tangga, anak, cerita hangat | Engine dikirim sebagai `file_tambahan` |
| `pictogram-motion`, `swiss-motion` | Spesifikasi, perbandingan, angka (rating, terjual) | Datar, satu warna sinyal |
| `game-show`, `microgame` | Gaya ceria khas Indonesia, ritme cepat | |
| `teardown`, `iso-infographic` | Cara kerja benda (kipas, keset diatomite) | `teardown` aslinya butuh CAD; yang dipakai tata bahasa label dan cahayanya |
| `dark-keynote` | Beat bukti (satu angka raksasa) | Hanya untuk satu beat, bukan seluruh video |
| `glass-product` | **Tidak dipakai** | Mensyaratkan produk fiktif, three.js/GPU |
| Kit `3d-lite` | Satu shot hero 3D, maks 2 × 2–4 detik | Hanya kalau ada model 3D produk; foto tidak cukup |

## 9. Daftar cek sebelum serah (gabungan)

Selain BASELINE 1–20:
- [ ] Benchmark ditulis di brief (dipelajari / tidak diambil).
- [ ] Tidak ada easing linear pada gerak yang terlihat; setiap masuk 2–3 properti + stagger; keluar lebih cepat dari masuk.
- [ ] Ada yang bergerak di 15 frame pertama; elemen baru ≤ 90 frame; hold dengan ambient hidup.
- [ ] Satu warna hero per frame; tidak ada glow, gradien polos, atau blob mesh.
- [ ] Whoosh 2–3 frame sebelum mendarat, benturan 1 frame sesudahnya; riser ke potongan; potongan di ketukan bila bisa.
- [ ] Frame diambil dari `final.mp4` dan **dilihat** (minimal 12 frame + setiap frame setelah transisi), lalu cek tanpa suara.
