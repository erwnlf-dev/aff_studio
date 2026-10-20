# 12 — Optimasi dan eksperimen

Dokumen ini menjalankan mandat §1.7: mengkritisi rencana, menjadikan spesifikasi video parameter yang bisa di-tune, merancang sistem eksperimen, mengumpulkan ide di luar rencana, dan mencari optimasi teknis.

| File | Isi |
|---|---|
| `config/video-params.yaml` | Registry parameter: nilai, rentang aman, alasan, sumber, status, kunci compliance, dan daftar eksperimen |
| `tools/cek_params.py` | Cek konsistensi registry, plus snapshot parameter dan `variant_id` per video |
| `tests/test_cek_params.py` | Tes aturan registry (`python3 -m unittest discover -s tests`) |
| `docs/adr/ADR-P0*.md` | Usulan yang mengubah keputusan inti (P01–P05), berstatus *Proposed* |

**Label di seluruh dokumen:**
- **[Default]**: dipakai di MVP.
- **[Usulan]**: perlu persetujuan pemilik (atau ADR kalau menyentuh keputusan inti).
- **[Eksperimen]**: MVP memakai nilai kontrol, lalu diuji lewat A/B.

## 0. Fondasi: pipeline Baru Tau

`aff_studio` mencontek pipeline *Baru Tau.* yang sudah berjalan di server ini. Hal-hal di bawah sudah dicek dari kode, bukan asumsi:

| Bagian | Di Baru Tau (dicek 20 Oktober 2026) | Untuk affiliate |
|---|---|---|
| Kreator | Claude Code headless, Opus 5.5 effort extra high, satu sesi panjang per episode (`baru-tau-autopilot/CLAUDE.md`, `lib.sh`) | Mahal dan lambat kalau satu sesi per video (K14, ADR-P05) |
| VO | Slate `buat_voiceover`: `eleven_v3`, stability 0,5, ruang napas 0,38/0,7 detik, timing per kata di `vo.json` | Dipakai apa adanya |
| Render | Slate `render_film`: `film.js` (canvas 1080×1920) dirender Chromium per frame di CPU, `RENDER_WORKERS=3`, fps 8–60 (bawaan 24) | Ken Burns = `drawImage` di canvas; foto masuk sebagai teks (§5.1) |
| Musik dan mix | `slate_score.py` (partitur JSON), ducking dinamis 7 dB, −14 LUFS | Dipakai apa adanya |
| QA | `qa.py`: loudness, frame beku/hitam, kedip, loop, kontras | Ditambah QA compliance (B3) |
| Gerbang | Dua gerbang: `setuju N` sebelum VO, `posting NNN` sebelum tayang | Pola yang sama (ADR-P02 tinggal menambah batch) |
| Posting | Hanya **Threads**, lewat Upload-Post (paket gratis 10 per bulan) atau Zernio (tanpa batas jumlah posting) | TikTok/Reels/Shorts belum ada rutenya (K15) |
| Konsol | `web/` dengan modul di `web/modules/` (barutau, kunci); inbox + Web Push | Modul baru `web/modules/affiliate/` |

**Input dan platform (dari paket data pemilik, 2026-10-19):**
- **Input:** produk dipilih, di-scrape, dan diberi link affiliate oleh pemilik lewat Claude in Chrome. Paket datanya (`products.json`, `meta.json` per produk, `manifest_slim.json`) menjadi kontrak input. Field dan celahnya ada di `docs/TODO.md` §3.
- **Platform fase 1:** Shopee Video, diunggah lewat Chrome dengan konfirmasi per batch. TikTok dan Threads menyusul. Bagian dokumen ini yang menyebut TikTok/Reels/Shorts berlaku untuk fase 2.

Nomor ADR `P01–P05` diganti nomor urut final saat digabung dengan ADR proyek.

## 1. Asumsi yang saya ragukan

Setiap butir ditulis dalam urutan: asumsi → kenapa saya ragu → alternatif. Urutannya dari dampak terbesar.

**K1. "Parameter video adalah tuas utama."**
- **Kenapa ragu:** Untuk affiliate, pemilihan produk (komisi × harga × peluang konversi) dan kesehatan akun hampir pasti lebih menentukan daripada warna caption atau BPM. Registry yang diminta §1.7 hanya mencakup video.
- **Alternatif:**
  - [Usulan] Skor pemilihan produk (B1) dengan registry sendiri (`config/product-scoring.yaml`, belum dibuat).
  - Eksperimen video diprioritaskan menurut dampak (§4.7), bukan menurut urutan daftar §1.7.

**K2. "Semua angka bisa dioptimasi lewat A/B."**
- **Kenapa ragu:** volumenya kecil dan metriknya bising.
  - Dengan 4–6 video per hari, satu uji 2 lengan × 30 video butuh 10–15 hari. Artinya paling banyak 2–3 eksperimen yang benar-benar selesai per bulan.
  - Order dan komisi per video hampir selalu nol atau satu, dan baru tervalidasi berminggu-minggu kemudian. Pada level video, keduanya praktis tidak akan pernah signifikan.
- **Alternatif:**
  - Uji parameter memakai metrik hulu yang cepat (hold 3 detik, avg watch %, klik).
  - Metrik uang (komisi per 1.000 views) hanya untuk keputusan besar (durasi, harga) dan untuk audit kuartalan bahwa metrik hulu memang searah dengan uang.
  - Parameter berdampak kecil dibiarkan di default yang beralasan, tidak diuji (§4.7).

**K3. "Ken Burns di foto penjual sudah cukup jadi video."**
- **Kenapa ragu:**
  - Ribuan akun lain memakai foto yang sama dengan gerak yang sama.
  - TikTok menurunkan distribusi konten yang dianggap tidak orisinal. Ini menurut ringkasan pihak ketiga; aturan resminya belum saya baca (R-TIKTOK-ORI).
  - Shopee Affiliate mensyaratkan akun pribadi dengan konten orisinal (R-SHOPEE-AFF).
- **Alternatif:** lapisan orisinalitas wajib, yaitu:
  - komposisi sendiri (kartu produk di atas latar, teks kunci dari data feed),
  - naskah dan VO sendiri,
  - struktur beat,
  - urutan crop detail yang mengikuti naskah.

  Ken Burns hanya gerak dasarnya. Video asli penjual hanya dipakai kalau lisensinya jelas dan diolah ulang (B11, ADR-P01).

**K4. "Beberapa varian per produk, di beberapa akun."**
- **Kenapa ragu:** varian yang hanya beda tipis, apalagi file identik di dua akun, adalah pola duplikat/spam. Ini juga bertabrakan dengan desain A/B berpasangan: dua video produk yang sama yang hanya beda satu parameter adalah duplikat yang disamarkan.
- **Alternatif:**
  - [Default] `varian.per_produk` = 2, dan setiap varian harus beda di ≥ 2 grup parameter (hook, template, foto, naskah) (kunci compliance).
  - File identik lintas akun dilarang.
  - Varian kedua di akun yang sama paling cepat 7 hari kemudian.
  - Eksperimen diacak **per produk**, bukan berpasangan dalam produk (§4.3).

**K5. "Harga dimunculkan di video."**
- **Kenapa ragu:**
  - Video hidup berbulan-bulan, sementara harga marketplace berubah per jam (flash sale, voucher, harga coret).
  - Harga yang benar saat render bisa jadi klaim salah saat ditonton. Ini tetap "data feed", tapi data feed yang sudah basi.
  - Harga yang diucapkan tidak bisa diberi tanggal.
- **Alternatif:**
  - [Default] `harga.mode = tanpa_angka`, kontrol EXP-09.
  - [Eksperimen] Lengan B memakai angka dari feed, hanya di layar, dengan tanggal kecil. Syaratnya: umur data ≤ 24 jam saat tayang dan feed membawa `price_captured_at` (ADR-P01).
  - `harga.diucapkan = false` dikunci.
  - Template `price_reveal` hanya boleh kalau lengan B aktif.

**K6. "Bukti sosial dari feed aman."**
- **Kenapa ragu:** jumlah terjual hanya naik, jadi "10rb+ terjual" tetap benar sebagai batas bawah. Rating bisa turun.
- **Alternatif:**
  - [Default] Tulis persis seperti tampilan marketplace saat diambil, tanpa membulatkan ke atas.
  - Rating hanya disebut kalau ≥ 4,6 **dan** jumlah rating ≥ 50.
  - Kutipan ulasan tidak dipakai sampai feed membawanya secara resmi.

**K7. "Retensi 3 detik bisa diukur sama di semua platform."**
- **Kenapa ragu:** definisi dan aksesnya berbeda:
  - Shorts memberi "viewed vs swiped away".
  - TikTok memberi kurva retensi di aplikasi/Studio.
  - Threads tidak memberi retensi sama sekali.
  - Tidak ada ambang resmi yang universal; panduan pihak ketiga sepakat untuk membandingkan dengan video sendiri (R-SHORTS-BENCH).
  - API untuk akun pribadi belum tentu membuka metrik ini.
- **Alternatif:**
  - Bandingkan hanya di dalam platform yang sama.
  - [Default] MVP menyediakan input manual per video di konsol, seperti `hasil NNN` di Baru Tau.
  - Otomasi API menyusul per platform setelah diverifikasi.

**K8. "Lima tipe hook setara."**
- **Kenapa ragu:**
  - `pain` di kategori kesehatan, kosmetik, atau suplemen menyiratkan klaim khasiat.
  - `visual_shock` sulit dibuat dari foto statis (tanpa footage, isinya biasanya hanya teks besar).
  - `price_reveal` bergantung pada K5.
- **Alternatif:**
  - [Default] `pertanyaan`, pola terkuat Baru Tau dan paling aman.
  - `pain` diblok untuk kategori yang klaimnya diatur (lewat `compliance_note` atau flag kategori di feed).
  - Lima tipe diuji di EXP-02, yang menjadi kandidat bandit pertama.

**K9. "Durasi per beat adalah angka tetap."**
- **Kenapa ragu:** pelajaran utama Baru Tau adalah bahwa VO adalah jam. Semua timing film mengikuti timing kata `vo.json`, dan audit #001 menunjukkan apa yang terjadi kalau gambar dan suara diatur terpisah (hening yang tertimpa suara).
- **Alternatif:** registry hanya menyimpan **batas** (`beat.durasi_min/maks_detik`, `beat.hook_maks_detik`). Durasi tiap beat = durasi potongan VO-nya.

**K10. "Angka dari Baru Tau sudah terbukti."**
- **Kenapa ragu:**
  - Angka Baru Tau adalah angka **craft dan QA** (ukuran caption, kontras, diam ≤ 0,5 detik, loudness), yang diukur dari audit, bukan dari performa. `episodes/index.json` belum punya satu pun data `hasil` (views/reply).
  - Baru Tau dioptimasi untuk reply per 1.000 views di Threads, sedangkan affiliate untuk klik dan komisi.
- **Alternatif:**
  - Angka craft dan QA diwarisi sebagai batas bawah (beberapa dikunci `qa`).
  - Angka gaya (tempo, durasi, hook) diperlakukan sebagai hipotesis H01–H12.
  - Ajakan reply A/B ala Baru Tau tidak menggantikan CTA (B17).

**K11. "Musik bisa dioptimasi per genre/BPM."**
- **Kenapa ragu:**
  - Dampaknya kecil dibanding hook dan produk.
  - Lagu tren tidak bisa dibakar ke file: ada risiko hak cipta, dan akun bisnis TikTok dibatasi ke Commercial Music Library.
  - Suara tren biasanya hanya bisa dipasang manual di aplikasi.
- **Alternatif:**
  - [Default] Musik sintesis satu bed per mood (cara Slate).
  - Hanya ada/tidaknya musik yang diuji (EXP-08).
  - Kalau suara tren terbukti penting, itu keputusan rute posting manual, bukan parameter.

**K12. "Jam tayang per platform bisa ditetapkan dari riset umum."**
- **Kenapa ragu:** data umum (Buffer untuk Threads) tidak berlaku untuk belanja, dan dengan sedikit akun efek jam bercampur dengan efek hari.
- **Alternatif:**
  - [Default] Hipotesis malam untuk TikTok/Reels.
  - Threads tetap pagi (data Baru Tau).
  - EXP-11 dijalankan paling akhir dengan rotasi slot per hari.

**K13. "Gerbang approval Baru Tau cukup untuk volume affiliate."**
- **Kenapa ragu:** Baru Tau sudah punya dua gerbang (`setuju N` sebelum VO, `posting NNN` sebelum tayang), tapi keduanya per episode dan dirancang untuk satu video per hari.
  - Kalau pemilik menonton setiap video final di HP (sekitar 1–2 menit per video), 10 video per hari memakan 20 menit atau lebih per hari.
- **Alternatif:** [Usulan, ADR-P02] pertahankan dua gerbang Baru Tau, tambahkan:
  - kartu tahap 1 yang memuat naskah + frame 0 (bukan hanya judul topik),
  - persetujuan batch untuk video yang lolos QA tanpa catatan.

**K14. "Satu sesi kreator Opus per video, seperti Baru Tau."**
- **Kenapa ragu:**
  - Di Baru Tau, satu sesi Opus 5.5 effort extra high menulis `film.js` dari nol, lalu menjalankan putaran pratinjau dan critic loop. Itu sepadan untuk satu explainer per hari.
  - Untuk 4–6 video produk per hari dengan struktur yang mirip, cara ini mahal dan lama.
  - Satu sesi per video juga membuat parameter sulit dikontrol: model bisa menyimpang dari snapshot, jadi `variant_id` tidak lagi menjamin isi video.
- **Alternatif:** [Usulan, ADR-P05] `film.js` template per template video, digerakkan oleh JSON dari snapshot. LLM hanya menulis naskah, hook, pemilihan foto per beat, dan teks post (satu panggilan terstruktur). Render, QA, musik, dan VO tetap lewat Slate. Sesi kreator penuh hanya untuk format khusus (B4 seri, B16 edu-commerce).

**K15. "Posting ke TikTok/Reels/Shorts dengan link affiliate bisa otomatis."**
- **Kenapa ragu:**
  - Slate saat ini hanya memosting ke Threads (Upload-Post, Zernio).
  - Paket gratis Upload-Post hanya 10 upload per bulan, jauh di bawah `posting.maks_per_akun_per_hari = 2`.
  - Saya tidak menemukan bukti bahwa Content Posting API TikTok bisa memasang tautan produk TikTok Shop. Panduan resmi yang ketemu hanya menyebut cara manual lewat aplikasi atau Seller Center. Ini belum pasti; perlu dicek ke referensi API.
  - Threads tidak punya anchor produk. Link harus di teks atau reply pertama, sementara aturan Baru Tau melarang link di teks post demi jangkauan.
- **Alternatif:**
  - [Default] MVP memakai rute yang sudah ada:
    - Threads lewat Zernio, dengan link di reply pertama,
    - TikTok/Reels: pipeline menyiapkan file + teks + daftar produk, lalu pemilik mengunggah dan memasang anchor produk di aplikasi (seperti Baru Tau, ada pilihan unggah manual).
  - Parameter `posting.jam_wib.*` selain Threads menjadi jam pengingat untuk unggahan manual.
  - Rute otomatis per platform adalah keputusan rute publishing (ADR-P03).

## 2. Registry parameter

### 2.1 Bentuk

Semua parameter ada di `config/video-params.yaml` dengan nama bertitik (`vo.tempo_kata_per_detik`). Setiap entri wajib memiliki:
- `status`,
- `nilai`,
- `rentang` **atau** `pilihan`,
- `alasan`,
- `sumber` (id yang terdaftar di `sumber` atau `hipotesis`).

Field `satuan`, `kunci`, dan `eksperimen` opsional. Field yang salah ketik ditolak.

```
python3 tools/cek_params.py                                   # ok: 99 parameter … / daftar kesalahan, exit 1
python3 tools/cek_params.py snapshot --eksperimen EXP-02 --lengan C
python3 tools/cek_params.py snapshot --set hook.tipe=pain     # ditolak kalau di luar rentang/pilihan atau berkunci
```

Kode pipeline membaca nilai **hanya** lewat snapshot. Tidak boleh ada angka spesifikasi yang di-hardcode di template atau prompt. Prompt LLM menerima nilai yang relevan (jumlah kata, tipe hook, kata maks per kalimat) dari snapshot.

### 2.2 Status

| Status | Arti | Di snapshot |
|---|---|---|
| `default` | [Default] dipakai MVP | selalu |
| `eksperimen` | [Eksperimen] `nilai` = lengan kontrol `A`; lengan lain di bagian `eksperimen` | selalu (nilai kontrol, atau nilai lengan) |
| `usulan` | [Usulan] belum aktif | hanya dengan `--setujui <nama>` |

### 2.3 Kunci: yang tidak boleh disentuh optimasi

Parameter dengan `kunci: compliance` atau `kunci: qa` tidak boleh menjadi lengan eksperimen atau bandit, dan tidak bisa di-override di snapshot (validator dan tes memeriksanya). Mengubah nilainya butuh ADR.

| Kunci | Parameter | Alasan |
|---|---|---|
| compliance | `disclosure.ada`, `disclosure.gaya`, `disclosure.font_px` | Disclosure selalu ada dan terbaca sejak frame 0 |
| compliance | `harga.diucapkan`, `harga.umur_data_maks_jam`, `harga.tampilkan_harga_coret` | Tidak ada harga basi, tidak ada diskon yang menyesatkan (K5, TODO §3) |
| compliance | `bukti.format` | Hanya angka feed, ditulis persis |
| compliance | `musik.sumber` | Tidak ada musik berlisensi yang dibakar ke file |
| compliance | `foto.tolak_watermark_pihak_lain`, `varian.beda_minimal_grup` | Orisinalitas (K3, K4) |
| compliance | `posting.maks_per_akun_per_hari`, `posting.jeda_varian_produk_sama_hari` | Bukan pola spam |
| qa | `teks.kontras_min`, `motion.diam_maks_detik`, `hook.aksi_pertama_dalam_detik`, `vo.tempo_maks_kalimat_kps`, `audio.lufs_target`, `audio.true_peak_maks_dbtp` | Batas bawah kualitas Baru Tau, diukur QA |

Aturan berikut **bukan parameter**, jadi tidak ada di registry dan tidak bisa dioptimasi sama sekali:
- tidak ada klaim di luar data feed,
- `compliance_note` produk dimasukkan ke prompt naskah dan dicek ulang di QA (B3),
- file identik tidak boleh diposting ke lebih dari satu akun,
- gerbang approval manusia tetap ada.

### 2.4 Mengubah default

1. Hanya lewat PR yang mengubah `nilai` di YAML, dengan id eksperimen pemenang atau alasan baru di `alasan`/`sumber`.
2. `python3 tools/cek_params.py` dan tes harus lolos.
3. Satu perubahan default per grup parameter per 14 hari, supaya efeknya tidak bercampur dengan perubahan algoritma platform.
4. Status parameter yang sudah selesai diuji kembali ke `default`, dan eksperimennya diberi status `selesai`.

## 3. Spesifikasi sebagai parameter

Tabel ini hanya memuat keputusan penting. Angka lengkap beserta rentang dan alasannya ada di YAML.

### 3.1 Durasi dan beat

| Parameter | Nilai | Label | Dasar |
|---|---|---|---|
| `durasi.target_detik` | 22 (lengan 15, 35) | [Eksperimen] EXP-01 | H01; Baru Tau 35–45 detik untuk explainer 7 bagian |
| `beat.durasi_min/maks_detik` | 1,5 / 4,0 | [Default] | ritme visual 2–4 detik (BT-VIRAL) |
| `beat.hook_maks_detik` | 3,0 | [Default] | hook ≤ 15% durasi (BT-BASELINE) |
| `template.default` | `masalah_solusi` (lengan `fitur_cepat`) | [Eksperimen] EXP-03 | satu template di MVP supaya hasil bisa dibandingkan |
| `template.pilih_per_kategori` | — | [Usulan] | aktif setelah EXP-03 punya pemenang per kategori (B9) |
| `template.perbandingan.urutan` | — | [Usulan] | butuh multi-produk (ADR-P03) |

Urutan beat per template adalah parameter (daftar dari kosakata `hook, masalah, produk, fitur, bukti, harga, cta`). Beat `harga` dibuang otomatis kalau `harga.mode = tanpa_angka` atau data harga lebih tua dari batas.

### 3.2 Voiceover

Jumlah kata dihitung dari parameter, bukan ditebak:

```
kata_target ≈ (durasi − ekor_loop − Σ jeda) × tempo
            ≈ (22 − 0,3 − (6 × 0,30 + 2 × 0,5)) × 2,6 ≈ 49  → vo.kata_target = 48
```

| Parameter | Nilai | Label | Dasar |
|---|---|---|---|
| `vo.tempo_kata_per_detik` | 2,6 (lengan 2,4; 2,8) | [Eksperimen] EXP-06 | Baru Tau 145–155 kpm efektif; CTA #001 261 kpm terdengar terburu-buru |
| `vo.tempo_maks_kalimat_kps` | 3,15 | [Default] kunci qa | 190 kpm per kalimat (BT-BIBLE) |
| `vo.kata_maks_per_kalimat` | 12 | [Default] | Baru Tau ≤ 14; satu kalimat ≈ 2–3 layar caption |
| `vo.voice_id` | 3 kandidat native Indonesia | [Eksperimen] EXP-04 | audit: kesan "AI" ada di ritme dan energi, bukan aksen |
| `vo.model`, `vo.stability` | `eleven_v3`, 0,5 (preset Natural) | [Default] | Slate; Creative rawan salah ucap angka dan nama produk |
| `vo.jeda_kalimat_detik` | 0,30 | [Default] | Baru Tau 0,38; jeda seragam 0,12–0,25 = tanda suara AI |
| `vo.jeda_sebelum_payoff_detik` | 0,45 | [Default] | hening ≥ 0,4 detik harus di dalam jeda VO (audit #001) |
| `vo.cta_paling_lambat` | true | [Default] | audit #001 |

Tempo diubah lewat jumlah kata naskah, bukan lewat `speed` TTS. Speed hanya ada di v2, dan di luar 0,9–1,15 artefaknya terdengar.

### 3.3 Hook

| Parameter | Nilai | Label | Dasar |
|---|---|---|---|
| `hook.tipe` | `pertanyaan` (lengan `klaim_angka`, `pain`, `visual_shock`) | [Eksperimen] EXP-02 | H03, K8 |
| `hook.produk_di_frame0` | true (lengan false: produk masuk ≤ 1,5 detik) | [Eksperimen] EXP-05 | H02; Baru Tau frame 0 = thumbnail utuh |
| `hook.teks_layar_kata_maks` | 5 | [Default] | BT-BASELINE 2, BT-VIRAL |
| `hook.kata_kunci_sebelum_detik` | 1,5 | [Default] | #001 terlambat (2,88 detik) |
| `hook.kandidat_dibuat` | 3 dalam satu panggilan | [Default] | generator besar = B2 |

### 3.4 Teks di layar dan zona aman

- **[Default] Caption:**
  - `per_frasa`, ≤ 5 kata per layar, font 68 px (batas bawah 64 px dikunci tes),
  - satu kata disorot `#FFD23F`,
  - kontras ≥ 4,5:1 di setiap frame,
  - teks kunci (harga, bukti) ≥ 60 px.

  Angka-angka ini diwarisi dari BASELINE Baru Tau (caption #001 42 px terlalu kecil di HP).
- **[Eksperimen] EXP-07:** `kata_per_kata` (H05).
- **Zona aman:** satu file untuk semua platform berarti memakai zona **terketat**: bawah ≥ 480 px (TikTok), kanan ≥ 140 px, atas ≥ 160 px. Angka TikTok/Reels/atas adalah perkiraan. Sebelum MVP dikunci, cek dengan screenshot UI terbaru tiap platform, termasuk posisi anchor produk TikTok Shop.
- **[Usulan]** Render per platform (zona aman dan CTA berbeda) hanya kalau zona terketat terbukti memakan terlalu banyak ruang. Biayanya satu encode tambahan per platform, tanpa TTS tambahan (§5).

### 3.5 Gerak

| Parameter | Nilai | Label | Dasar |
|---|---|---|---|
| `motion.fps` | 30 | [Default] | H11: pan lambat di 24 fps mudah terlihat patah; Baru Tau 24 fps untuk animasi terbatas |
| `motion.kenburns.zoom_per_detik` / `zoom_maks` | 3%/detik, maks 1,15 | [Default] | foto marketplace 800–1.000 px lembek di atas 1,15 |
| `motion.kenburns.arah` | `ke_saliensi` (ke fitur yang disebut VO) | [Default] | gerak harus deterministik, tidak acak |
| `motion.easing` | `ease_in_out_sine` | [Default] | linear termasuk TERLARANG Baru Tau |
| `motion.transisi` | `potong_keras` | [Default] | zoom blur, whip pan, dissolve termasuk TERLARANG Baru Tau |
| `motion.ganti_visual_maks_detik` | 3,0 | [Default] | beat panjang diisi crop detail kedua |
| `motion.diam_maks_detik` | 0,5 | [Default] kunci qa | QA Slate |

### 3.6 Audio

- **[Default]**
  - musik sintesis, 112 BPM, −12 dB relatif ke VO saat jeda, ducking dinamis 7 dB,
  - −14 LUFS, true peak ≤ −1,5 dBTP (semuanya dari rantai mix dan QA Slate),
  - foley di aksi yang terlihat, dengan energi > 150 Hz supaya terdengar di HP (sepertiga foley #001 tak terdengar).
- **[Eksperimen] EXP-08:** dengan vs tanpa musik.

### 3.7 Elemen affiliate

| Elemen | [Default] MVP | Diuji/diusulkan |
|---|---|---|
| Harga | tidak ada angka; "cek harga terbaru di keranjang" | [Eksperimen] EXP-09: angka feed + tanggal, di layar saja, umur ≤ 24 jam, di 72% durasi; perlu ADR-P01 |
| Bukti sosial | terjual (≥ 100) + rating (≥ 4,6 dan ≥ 50 rating), persis seperti tampilan marketplace | kutipan ulasan: [Usulan] lewat ADR-P01 |
| CTA | sekali di akhir, 2,2 detik, dibaca paling lambat, arah ke tempat link per platform | pertanyaan A/B sebelum CTA: B17 |
| Disclosure | label "Link afiliasi" 36 px sepanjang video + label/toggle di teks post | eksperimen hanya pada kata-kata dan posisi di dalam batas kunci (H12) |
| `compliance_note` | masuk prompt naskah + dicek di QA | — (bukan parameter) |

### 3.8 Varian dan foto

- **[Default] Varian:** 2 varian per produk, beda ≥ 2 grup parameter.
- **[Default] Foto:**
  - cover untuk hook/produk/CTA (akhir menyambung ke frame 0), detail untuk fitur,
  - satu foto per beat (dua kalau beat ≥ 3 detik), maks 6 foto,
  - sisi pendek ≥ 800 px untuk layar penuh,
  - foto berwatermark pihak lain ditolak.
- **[Eksperimen] EXP-10:** foto 1:1 ditaruh sebagai kartu di atas latar warna dominan (kontrol) vs `crop_isi` (H10).

### 3.9 Posting

- **[Default] Jam:** TikTok 19.00, Reels 19.30, Shorts 17.00, Threads 07.30 WIB.
- **[Default] Frekuensi:**
  - maks 2 video per akun per hari (dikunci; naik ke 3 hanya lewat ADR setelah 30 hari bersih),
  - jeda antar post ≥ 180 menit,
  - produk sekategori di akun yang sama ≥ 48 jam,
  - varian produk yang sama di akun yang sama ≥ 7 hari.
- **[Eksperimen] EXP-11:** slot TikTok 12.00 / 19.00 / 21.00, dirotasi per hari.
- **[Usulan] B6:** kalender gajian (tanggal 25–5) dan tanggal kembar menggeser **jam dan pilihan produk**, bukan menambah kuota.

## 4. Sistem eksperimen

### 4.1 Snapshot, `variant_id`, dan atribusi

1. **Snapshot:** saat naskah dibuat, pipeline memanggil `snapshot` (dengan lengan dari penjadwal eksperimen) lalu menyimpan JSON-nya bersama video: `variant_id`, `versi_skema`, `eksperimen {id, lengan}`, dan `params` lengkap.
2. **`variant_id`** = `v_` + 12 hex SHA-256 dari `params` (kunci terurut). Parameter identik selalu menghasilkan id yang sama, dari eksperimen mana pun. Snapshot tidak pernah diubah setelah render; re-edit (B18) menghasilkan video dan snapshot baru.
3. **`video_id`** unik per file yang diposting (satu `variant_id` bisa punya banyak video untuk produk berbeda).
4. **Atribusi klik dan order:** setiap video mendapat link affiliate sendiri dengan `sub_id = video_id` (Shopee custom link punya kolom Sub ID; cek ke dashboard). TikTok Shop mengatribusi per video lewat anchor produk. Ini menyentuh kontrak feed dan rute publikasi, jadi diusulkan lewat ADR-P03.
5. **Input metrik:** [Default] form per video di modul affiliate konsol web (pola `catat_hasil.sh` Baru Tau) pada jam ke-72 dan hari ke-7; komisi diimpor dari laporan affiliate (CSV). Integrasi API per platform menyusul setelah aksesnya diverifikasi (K7).

### 4.2 Metrik per tahap funnel

| Tahap | Metrik (id YAML) | Definisi | Sumber data | Kapan dibaca |
|---|---|---|---|---|
| Distribusi | `views_72j` | views 72 jam | analitik platform | 72 jam |
| Hook | `hold_3s` | fraksi penonton yang masih ada di detik 3 | Shorts: viewed vs swiped; TikTok: kurva retensi | 72 jam |
| Tonton | `avg_watch_pct`, `completion` | rata-rata persen ditonton; fraksi yang menonton sampai habis | analitik platform | 72 jam |
| Klik | `ctr_link` | klik link (sub_id) per 1.000 views | laporan affiliate | 7 hari |
| Order | `cvr_order` | order per klik | laporan affiliate | 7 hari (tertunda), 30–45 hari (tervalidasi) |
| Uang | `komisi_per_1000_views` | komisi tertunda + tervalidasi per 1.000 views | laporan affiliate | 7 hari / tervalidasi |
| Uang bersih | `komisi_bersih_per_video` | komisi tervalidasi − biaya TTS, LLM, compute | laporan + log biaya | bulanan |
| Pengaman | `laporan_negatif`, `keluhan_harga`, `cancel_retur` | sinyal buruk per 1.000 views / per order | platform, komentar, laporan | 7 hari |

**North star:** `komisi_bersih_per_video`. Metrik utama tiap eksperimen dipilih dari tahap yang **langsung** dipengaruhi parameternya:
- hook dan frame 0 → `hold_3s`,
- caption, tempo, suara, musik → `avg_watch_pct`,
- template dan harga → `ctr_link`,
- durasi → `komisi_per_1000_views`, karena video pendek selalu menang persentase tonton secara mekanis.

Setiap eksperimen juga mencatat pengaman supaya kemenangan di hulu tidak dibayar di hilir (contoh EXP-05: hold naik, klik turun).

Perbandingan hanya dilakukan **di dalam platform yang sama**. Angka TikTok dan Shorts tidak digabung.

### 4.3 Desain uji

- **Unit:** video. Satu video = satu baris data, dengan metrik rasio dari video itu.
- **Acak per produk:** lengan ditentukan `hash(product_id, exp_id) mod jumlah_lengan`. Akibatnya:
  - semua video satu produk dalam eksperimen itu ada di lengan yang sama,
  - tidak ada pasangan A/B dari produk yang sama yang hanya beda satu parameter (duplikat terselubung, K4).

  Varian kedua sebuah produk tetap beda ≥ 2 grup lewat parameter lain.
- **Blok:** platform × akun × kategori. Penjadwal menjaga jumlah lengan seimbang per blok, dan analisis dilakukan per blok lalu digabung.
- **Satu faktor per eksperimen.** Paling banyak 2 eksperimen berjalan bersamaan, dan hanya kalau parameternya di tahap funnel berbeda dan diacak ortogonal (hash dengan `exp_id` berbeda). Contoh yang boleh: EXP-02 (hook) bersama EXP-08 (musik).
- **Kontrol selalu lengan `A`** = nilai registry (dicek validator).
- **Metrik rasio per video** dianalisis dengan bootstrap di level video (resampling video, bukan views). Views sangat menceng: satu video viral tidak boleh menentukan pemenang, jadi laporkan median dan rata-rata terpangkas 10% di samping rata-rata.

### 4.4 Sampel minimum dan durasi

Rumus kasar per lengan, untuk metrik rasio per video dengan simpangan baku antar-video σ dan beda minimal yang ingin dideteksi δ:

```
n ≈ 2 · (z₁₋α/₂ + z₁₋β)² · σ² / δ²      α = 0,10 dua sisi, kuasa 80 % → 2 · 2,49² ≈ 12,4
σ = 9 pp, δ = 6 pp (hold_3s)  → n ≈ 12,4 · 81 / 36 ≈ 28  → 30 per lengan
```

α = 0,10 dipilih karena keputusan default bisa dibalik dan diawasi holdout (§4.5); ini bukan publikasi ilmiah. σ dihitung ulang dari 30 video pertama (masa pilot). Kalau σ ternyata jauh lebih besar, `sampel_min_per_lengan` di YAML dinaikkan, bukan α yang dilonggarkan.

| Eksperimen | Metrik utama | Min per lengan | Min hari |
|---|---|---|---|
| hook, frame 0, caption, tempo, musik, foto | hold / watch | 25–30 video | 14 (dua akhir pekan) |
| template | klik | 30 | 14 |
| durasi, harga | komisi / klik | 40 | 21 |
| jam posting | views | 30 | 21 |

**Realita volume:** dengan 6 video per hari, eksperimen 2 lengan × 30 selesai dalam sekitar 10 hari dan 4 lengan × 30 dalam sekitar 20 hari. Penjadwal mengantre eksperimen menurut prioritas §4.7.

### 4.5 Aturan promosi pemenang

Sebuah lengan menggantikan default kalau **semua** syarat berikut terpenuhi:
1. Sampel minimum dan hari minimum tercapai di semua lengan.
2. P(lengan > kontrol pada metrik utama) ≥ 0,90 (bootstrap per video), **dan** efeknya ≥ 5% relatif. Beda yang lebih kecil tidak sepadan dengan risiko drift.
3. Tidak ada metrik pengaman yang memburuk > 10% relatif dengan P ≥ 0,80.
4. Arahnya sama di ≥ 2 dari 3 blok terbesar. Kalau hanya menang di satu kategori, promosi dibatasi ke kategori itu (masuk pemetaan B9).
5. Nol insiden compliance yang terkait lengan itu.

**Lalu:**
- PR mengubah `nilai` (§2.4), dan eksperimen diberi status `selesai` dengan ringkasan angka di `catatan`.
- Default lama disimpan sebagai **holdout 10% selama 14 hari**. Kalau holdout ternyata menang, perubahan dikembalikan.
- **Tanpa pemenang setelah 2× sampel minimum:** eksperimen dihentikan, kontrol dipertahankan, dan hasilnya dicatat sebagai "tidak ada beda". Itu juga informasi: parameter itu tidak perlu diuji lagi dalam 90 hari.

### 4.6 Aturan sederhana vs multi-armed bandit

| Pakai aturan sederhana (§4.3–4.5) kalau… | Pakai bandit kalau… |
|---|---|
| volume < 15 video per hari | volume ≥ 15 video per hari di satu platform |
| 2–3 lengan | ≥ 4 lengan (tipe hook, template per kategori) |
| metrik lambat atau jarang (order, komisi) | metrik cepat dan sering (`hold_3s` dalam 72 jam) |
| tujuannya tahu mana yang lebih baik dan kenapa | tujuannya memaksimalkan hasil sambil tetap belajar |
| parameter berefek mekanis ke metrik (durasi → watch %) | lengan setara secara mekanis |
| menyangkut harga, disclosure, compliance | tidak pernah menyentuh parameter berkunci |

**[Usulan] Bandit pertama:** `hook.tipe` per kategori. Aktif hanya setelah EXP-02 selesai sekali secara manual (membuktikan rantai metrik bekerja) dan sudah ada ≥ 300 video terukur. Desainnya:
- Thompson sampling Beta per lengan per kategori.
- **Reward biner:** `hold_3s` video ≥ median 30 video terakhir di akun yang sama. Ini menghapus skala akun yang berbeda-beda.
- **Lantai eksplorasi:** 10% per lengan.
- **Peluruhan:** 0,98 per hari, untuk menangani drift algoritma.
- Snapshot tetap menyimpan lengan yang dipilih, jadi data bandit masih bisa dianalisis seperti A/B.

Bandit **tidak pernah** dipakai untuk durasi, harga, apa pun yang diukur dengan order/komisi, dan parameter berkunci.

### 4.7 Antrean eksperimen (prioritas = dampak × kemudahan)

| Urutan | Eksperimen | Kenapa urutan ini |
|---|---|---|
| 0 | EXP-04 suara (tes dengar buta dulu, lalu 2 kandidat terbaik diuji publik) | Suara adalah tanda "AI" pertama (audit Baru Tau); murah dites sebelum publik |
| 1 | EXP-02 tipe hook | 3 detik pertama menentukan semua tahap setelahnya; metrik cepat |
| 2 | EXP-05 produk di frame 0 | dampak hook, 2 lengan, cepat |
| 3 | EXP-03 template | menentukan B9 |
| 4 | EXP-01 durasi | dampak besar tapi butuh metrik uang (21 hari) |
| 5 | EXP-09 harga | butuh ADR-P01 dulu |
| 6 | EXP-06 tempo, EXP-07 caption, EXP-10 foto | perbaikan halus |
| 7 | EXP-08 musik, EXP-11 jam | dampak kecil atau paling bercampur |

## 5. Optimasi teknis

### 5.1 Biaya per video

```
biaya_video = karakter_TTS × harga_per_karakter
            + token_LLM × harga_token
            + menit_CPU_render × harga_menit
```

Isi harga dari tagihan aktual. Harga tidak ditulis di sini karena berubah.

- **TTS (biasanya komponen terbesar):**
  - 48 kata Indonesia ≈ 48 × ~7 karakter ≈ 330–350 karakter per naskah.
  - 2 varian dengan naskah berbeda ≈ 700 karakter per produk.
  - Paket gratis 10.000 karakter ≈ 14 produk atau 28 video per bulan (Baru Tau sudah memakai sebagian kuota yang sama kalau kuncinya digabung di pool Slate).
- **Penghematan TTS:**
  - **[Default] Cache TTS:** kunci = hash(teks, voice, model, settings). Retry, QA gagal, atau render ulang tidak pernah membuat VO baru (aturan Baru Tau: pakai ulang `vo.json`).
  - **[Default] Eksperimen visual memakai VO yang sama.** Lengan EXP-05/07/08/10 tidak mengubah naskah, jadi tidak menambah karakter.
  - **[Usulan] B10:** versi 15 dan 45 detik dari satu VO panjang, dipotong di batas kalimat yang sudah punya ruang napas.
  - **[Eksperimen]** Sambung kalimat hook baru ke badan VO lama (hemat sekitar 70% karakter varian kedua). Hanya boleh di jeda ≥ 0,3 detik, dan hanya kalau tes dengar buta pemilik tidak bisa menemukan sambungannya (≥ 8 dari 10 salah tebak).
  - **[Usulan, ADR-P02]** Tidak ada TTS sebelum naskah disetujui. Naskah yang ditolak hanya memakan token LLM.
- **LLM:**
  - Satu panggilan per produk menghasilkan naskah + 3 hook + teks post + alt text sebagai JSON terstruktur.
  - Instruksi tetap (aturan gaya, compliance, TERLARANG) diletakkan di awal prompt supaya bisa memakai prompt caching.
  - Generasi malam hari untuk antrean besok lewat Batch API (lebih murah, tidak mendesak).
  - Model besar untuk naskah; model kecil untuk klasifikasi dan penilaian (pemilihan foto, B2 penilai hook, B3 cek teks).
- **Sesi kreator (Claude Code):** di pipeline Baru Tau, ini kemungkinan komponen termahal per video (K14). [Usulan, ADR-P05] Ganti dengan template `film.js` + satu panggilan LLM terstruktur per produk.
- **Compute (Slate `render_film`, Chromium per frame di CPU):**
  - **Foto harus masuk sebagai teks.** `file_tambahan` hanya menerima file teks (.js/.css/.json/.svg/.html), maksimal 2 MB per file dan 8 MB total, dan jaringan film diblokir. Foto di-resize ke sisi panjang 1080 px, JPEG kualitas 80 (sekitar 150–250 KB), lalu ditaruh sebagai data URI base64 di `foto.json` (+33%). Enam foto ≈ 1,5 MB, aman di bawah batas (`foto.embed_*` di registry).
  - **Waktu render:** perkiraan Slate sendiri ≈ durasi × fps / worker × 0,35 detik. Video 22 detik dengan 3 worker ≈ 77 detik di 30 fps, atau ≈ 62 detik di 24 fps. `motion.fps = 30` (H11) menambah sekitar 25% waktu render; kalau EXP atau tes mata menunjukkan 24 fps tidak patah-patah untuk Ken Burns di canvas, turunkan ke 24.
  - **Ken Burns di canvas:** `drawImage` dengan transformasi subpiksel tidak punya masalah pembulatan seperti `zoompan` ffmpeg. Getaran yang tersisa hanya soal fps.
  - **Worker dipakai bersama Baru Tau** (`RENDER_WORKERS=3`). Antrean affiliate dijadwalkan di luar jam produksi Baru Tau, atau Slate diberi antrean prioritas [Usulan].
  - **`motion_blur` tetap 0.** Biayanya naik sebanding jumlah subframe, dan Ken Burns pelan tidak butuh.
  - **Pratinjau tahap 1:** `pratinjau_film` (still di beberapa waktu) untuk frame 0 dan 2–3 beat. Tanpa render video dan tanpa TTS.
  - **[Usulan] Cache layer gerak** (render per beat lalu digabung) belum ada di Slate karena Slate selalu merender film utuh. Baru layak kalau varian yang hanya beda caption/musik ternyata banyak.
- **Ukur sebelum optimasi:** catat per video `detik_render`, `karakter_tts`, dan `token_llm` di log biaya, lalu sasar komponen terbesar. Target awal (hipotesis): render ≤ 2× durasi video per video di server.

### 5.2 Di mana kualitas boleh turun tanpa terasa, dan di mana tidak

| Boleh turun | Jangan turun |
|---|---|
| bitrate di atas sekitar 8 Mbps; audio 44,1 vs 48 kHz | suara/prosodi VO (tanda "AI" pertama) |
| resolusi pratinjau dan jumlah putaran pratinjau | ukuran caption (≥ 64 px) dan kontras (≥ 4,5:1) |
| model LLM untuk klasifikasi dan penilaian | frame 0 dan waktu kata kunci hook |
| kerumitan musik sintesis (satu bed per mood) | resolusi foto layar penuh (upscale > 1,15× terlihat lembek) |
| kandidat hook di atas 3 | ketepatan angka dan disclosure |
| variasi foley | loudness dan true peak (QA) |

## 6. Ide di luar rencana

Skor = dampak (1–5) × (6 − effort), dengan effort 1 = ringan dan 5 = berat. Semua ide berstatus [Usulan] kecuali disebut lain.

| # | Ide | D | E | Skor | Catatan dan batas compliance |
|---|---|---|---|---|---|
| B1 | **Skor pemilihan produk:** ekspektasi komisi = komisi% × harga × sinyal konversi (laju terjual) × kualitas foto, ditambah penalti kategori jenuh | 5 | 2 | 20 | Tuas terbesar (K1); registry terpisah `config/product-scoring.yaml` |
| B2 | **Hook generator + penilai otomatis:** 8 kandidat, lalu aturan keras (≤ 5 kata, nama produk, hanya angka feed, `compliance_note`), lalu model kecil memberi skor rubrik, lalu 2 terbaik ke pemilik | 4 | 2 | 16 | Penilai tidak boleh meloloskan klaim; aturan keras lebih dulu |
| B3 | **QA compliance otomatis:** OCR frame → disclosure ada di setiap frame, semua angka di layar ⊂ feed, kontras, zona aman; plus QA Slate (LUFS, diam, kedip) | 4 | 2 | 16 | Gerbang sebelum approval manusia, bukan pengganti |
| B4 | **Seri per niche** ("Rp50rb-an buat anak kos #12"): nomor episode, end card seri, satu janji per seri | 4 | 2 | 16 | Identitas seri dan end card dari BIBLE Baru Tau |
| B5 | **Cover/thumbnail = frame 0**, plus cover terpisah untuk platform yang memintanya | 3 | 1 | 15 | BASELINE 1 Baru Tau |
| B6 | **Kalender gajian (25–5) dan tanggal kembar:** geser jam dan pilihan produk | 3 | 1 | 15 | Tidak menambah kuota harian (kunci) |
| B7 | **Daftar hitam produk:** cancel/retur tinggi, keluhan, rating turun di bawah ambang | 3 | 1 | 15 | Juga melindungi akun |
| B8 | **Teks post dan komentar pertama bersuara manusia** (aturan VIRAL Baru Tau: tanpa "Fun fact", tanpa kata baku) | 3 | 1 | 15 | Klaim di teks post ikut aturan feed |
| B9 | **Template otomatis per kategori** dari hasil EXP-03 | 3 | 2 | 12 | Mengaktifkan `template.pilih_per_kategori` |
| B10 | **Versi 15 dan 45 detik dari naskah yang sama** (naskah modular: inti 15 detik + blok tambahan) | 3 | 2 | 12 | Hemat TTS; tetap 2 file berbeda, bukan duplikat |
| B11 | **Video asli penjual** bila feed membawa `media_license` yang mengizinkan; diolah ulang (potong, VO, teks) | 4 | 3 | 12 | ADR-P01; tanpa lisensi = tidak dipakai |
| B12 | **Pemicu harga turun/flash sale** → produk naik di antrean | 3 | 2 | 12 | Harga tetap tidak masuk video kecuali EXP-09 menang |
| B13 | **Penilai foto:** resolusi, watermark/teks (OCR), latar polos vs ramai → pilih cover dan detail | 3 | 2 | 12 | Menegakkan `foto.tolak_watermark_pihak_lain` |
| B14 | **Laporan eksperimen mingguan** di modul affiliate konsol web (status lengan, P(menang), pengaman) | 3 | 2 | 12 | Push ke HP lewat inbox konsol Baru Tau |
| B15 | **Kompilasi mingguan** "5 barang terlaris minggu ini" dari data feed | 3 | 2 | 12 | Butuh multi-link (ADR-P03) |
| B16 | **Edu-commerce:** "kenapa benda ini bentuknya begitu" (DNA Baru Tau) lalu produknya | 5 | 4 | 10 | Butuh fakta umum di luar feed → ADR-P04; tidak pernah klaim produk |
| B17 | **Pertanyaan A/B sebelum CTA** ("tim botol kaca atau plastik?") untuk mendorong komentar | 2 | 1 | 10 | Tanpa umpan engagement ("komen X") |
| B18 | **Re-edit otomatis video berperforma rendah:** hook 3 detik dan cover baru, jadi video baru (beda ≥ 2 grup), di akun lain atau setelah ≥ 14 hari | 3 | 3 | 9 | Bukan posting ulang file yang sama |
| B19 | **Balas komentar dengan video** untuk pertanyaan produk yang berulang | 3 | 3 | 9 | Jawaban hanya dari data feed |

## 7. Usulan yang mengubah keputusan inti (ADR *Proposed*)

Tidak ada satu pun yang diterapkan di registry atau kode; parameter yang bergantung padanya berstatus usulan atau eksperimen dengan `syarat`.

| ADR | Judul | Menyentuh | Membuka |
|---|---|---|---|
| [ADR-P01](adr/ADR-P01-kontrak-feed-kesegaran-dan-lisensi.md) | Kontrak feed: kesegaran harga, tampilan bukti, lisensi media | kontrak feed | EXP-09, B11, kutipan ulasan |
| [ADR-P02](adr/ADR-P02-gerbang-approval-dua-tahap.md) | Gerbang approval dua tahap dan persetujuan batch | gerbang approval manusia | hemat TTS dan render (§5.1) |
| [ADR-P03](adr/ADR-P03-atribusi-dan-anti-duplikat.md) | Atribusi per video (sub_id) dan aturan anti-duplikat publikasi | rute publishing, kontrak feed | §4.1, template perbandingan, B15 |
| [ADR-P04](adr/ADR-P04-fakta-umum-di-luar-feed.md) | Fakta umum terverifikasi di luar feed untuk konten edu-commerce | aturan "tidak ada klaim di luar feed" | B16 |
| [ADR-P05](adr/ADR-P05-film-template-bukan-sesi-kreator.md) | `film.js` template berbasis snapshot, bukan sesi kreator per video | stack (cara film dibuat) | K14, §5.1, `variant_id` yang bisa dipercaya |

## 8. Sumber

**Temuan Baru Tau (di server):**
- `baru-tau-autopilot/series/BIBLE.md`, `BASELINE.md`, `VIRAL.md`
- `docs/AUDIT-2026-10-19.md`, `docs/audit/audio.md`
- `examples/ep001/NOTES.md`
- `slate-studio/slate_sound.py` (ducking 7 dB, musik −6/−12 dB), `app.py` (jeda 0,38/0,7 detik, stability 0,5), `qa.py` (−14 LUFS ±1,5, kontras 4,5:1, diam)

**Riset web (20 Oktober 2026):**
- Aturan konten tidak orisinal TikTok, dari ringkasan pihak ketiga (belum dicek ke teks resmi Community Guidelines):
  - [bigseller.pro](https://www.bigseller.pro/blog/articleDetails/3778/tiktok-unoriginal-content.htm)
  - [openclip.app](https://openclip.app/guides/tiktok-slideshow-unoriginal-content-flag)
- Kebijakan TikTok Shop (Content Policy 22 Mei 2026, Branded Content Policy 31 Agustus 2026), disebut di sumber berikut; teks resminya belum dibaca:
  - [ppc.land](https://ppc.land/tiktok-shops-tightening-grip-new-rules-that-could-freeze-your-account/)
  - [canopymanagement.com](https://canopymanagement.com/tiktok-branded-content-policy-sellers/)
- Shopee Affiliates: akun pribadi, konten orisinal, produk terlarang:
  - [shopee.co.id](https://shopee.co.id/inspirasi-shopee/shopee-affiliates-program/?camp=1%2F)
- Retensi Shorts: tidak ada ambang resmi, bandingkan dengan video sendiri:
  - [subscribr.ai](https://subscribr.ai/youtube-strategy/youtube-shorts-analytics-metrics-viral)
  - [contentstudio.io](https://contentstudio.io/blog/youtube-shorts-analytics-guide)
  - [socialmediaexaminer.com](https://www.socialmediaexaminer.com/?p=251758)
- ElevenLabs v3, stability sebagai preset Creative/Natural/Robust:
  - [elevenlabs.io/docs/best-practices/prompting](https://elevenlabs.io/docs/best-practices/prompting)
- Tautan produk TikTok: Content Posting API (Direct Post/Upload) tidak menyebut tautan produk; panduan yang ditemukan menambahkannya lewat aplikasi atau Seller Center:
  - [developers.tiktok.com/products/content-posting-api](https://developers.tiktok.com/products/content-posting-api)
  - [ads.tiktok.com/help — add product links](https://ads.tiktok.com/help/article/add-product-links-tiktok-videos?lang=en)
  - [videowise.com](https://videowise.com/live-commerce/how-to-post-a-shoppable-video-on-tiktok-for-higher-conversions)

**Yang masih perlu diverifikasi sebelum MVP dikunci:**
- angka zona aman per platform (screenshot UI),
- teks resmi aturan orisinalitas TikTok dan TikTok Shop,
- syarat lengkap Shopee Affiliate soal klaim harga dan disclosure,
- dukungan Sub ID di link affiliate,
- apakah ada API resmi untuk memasang tautan produk TikTok Shop (K15),
- metrik retensi apa saja yang bisa diambil lewat API untuk jenis akun yang dipakai.
