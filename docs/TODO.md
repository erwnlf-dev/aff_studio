# TODO: status dan pekerjaan berikutnya

Per 20 Oktober 2026. Tanda **[pemilik]** berarti keputusan atau aksi pemilik; tanda **[Claude]** berarti bisa dikerjakan Claude Code di server tanpa menunggu keputusan lain.

## 1. Pembagian kerja

| Tahap | Siapa | Alat |
|---|---|---|
| Riset market, pilih produk, scrape data + gambar, buat link affiliate | pemilik | Claude in Chrome (`CONTEXT.md` di paket data) |
| Data produk → naskah → VO → video → QA → antrean approval | aff_studio | Slate Studio (VO, render `film.js`, QA, mix) |
| Approval naskah dan video | pemilik | konsol web (`web/modules/affiliate`, belum ada) |
| Upload ke platform | pemilik | Claude in Chrome, dengan konfirmasi per batch |

Input aff_studio adalah **paket data hasil scrape**, contohnya `/data/apps/affiliate_pipeline_data_2026-10-19.zip`:
- `products/products.json`: daftar lengkap, satu objek per produk,
- `products/<product_id>/meta.json`: objek yang sama per produk,
- `products/manifest_slim.json`: versi ringkas, plus `compliance_note` dan `image_files`,
- `products/shortlist.csv`,
- `market-analysis/YYYY-MM-DD_analysis.md`,
- `CONTEXT.md`: memori kerja sesi Chrome.

Format ini menjadi patokan input frontend (§3).

## 2. Sudah selesai

- [x] `docs/12-optimization-and-experiments.md`: kritik rencana, parameter, sistem eksperimen, ide, optimasi teknis.
- [x] `config/video-params.yaml` + `tools/cek_params.py` + tes: registry parameter, snapshot, `variant_id`.
- [x] ADR-P01–P05 berstatus *Proposed*.
- [x] Branch `main` jadi default; pekerjaan berikutnya lewat PR.
- [x] Paket data 2026-10-19 dibaca: 9 produk `link_ready` (temuan di §3).

## 3. Temuan dari paket data 2026-10-19

1. **Gambar tidak ada di zip.** Semua folder `products/<id>/images/` kosong. Ke-71 gambar ada di folder Download Chromium (`/data/storage/chrome-webgui/Downloads`), yang tidak bisa dibaca user `ubuntu` (permission denied).
2. **Field yang sudah memenuhi ADR-P01:**
   - `scraped_at` (= waktu harga diambil),
   - `sold_30d` sebagai teks tampilan ("10RB+"),
   - `reviews` (= jumlah rating),
   - `category`,
   - `transparent_bg` (foto tanpa latar, cocok untuk kartu produk di atas latar warna),
   - `has_video`.

   **Field yang belum ada:**
   - penanda harga promo/flash sale,
   - lisensi media (foto dan video penjual),
   - penanda kategori yang klaimnya diatur. Ini bisa diturunkan dari `category`: Perawatan & Kecantikan, Makanan & Minuman.
3. **`video_angle` buatan sesi Chrome memuat klaim yang tidak ada di `key_features`.** Contoh:
   - Hanasui: "Satu usap langsung pink",
   - Keset: "Air langsung hilang dalam 3 detik?!",
   - DUZI: "Coba duo ini 2 minggu". Ini bertentangan dengan `compliance_note`-nya sendiri ("hindari … hasil instan").

   Akibatnya `video_angle` hanya boleh dipakai sebagai **saran sudut**. Setiap klaim di naskah dan layar tetap harus ditemukan di `key_features`, deskripsi penjual, atau angka feed (QA compliance, butir 12).
4. **`compliance_note` mencampur aturan compliance dengan catatan bisnis.** Contoh catatan bisnis: "dorong bundling 5+1"; contoh aturan: "jangan tonjolkan % diskon". Usulannya: dua field, `compliance_note` (aturan, wajib dipatuhi) dan `business_note` (saran).
5. **Harga coret bisa menyesatkan.** Contohnya kipas: Rp199rb → Rp26,9rb (−86%). Aturan baru (dikunci): harga coret dan persen diskon tidak pernah tampil (`harga.tampilkan_harga_coret = false`).
6. **Platform fase 1 = Shopee Video** (roadmap di `CONTEXT.md`), bukan TikTok/Threads. Zona aman Shopee Video belum diukur.
7. **Repo ini publik.** Paket data mentah tidak di-commit: ada email pemilik di `CONTEXT.md`, link affiliate, dan data toko. Tes memakai fixture yang sudah disamarkan.

## 4. Keputusan pemilik (yang lain menunggu ini)

- [ ] **[pemilik]** Gambar: pilih salah satu.
  - Salin ke `/data/apps/affiliate-data/<tanggal>/products/<id>/images/`.
  - Atau izinkan `fetch_images_zip.py` (dari paket data) mengunduh ulang dari CDN Shopee ke server: 71 file, jeda 1,5–3,5 detik.
  - Ke depan: zip sebaiknya sudah berisi gambar.
- [ ] **[pemilik]** Lokasi paket data di server: usulan `/data/apps/affiliate-data/<tanggal>/` (di luar repo).
- [ ] **[pemilik]** ADR-P05: template `film.js` berbasis snapshot, bukan sesi Opus per video.
- [ ] **[pemilik]** ADR-P02: persetujuan naskah + frame 0 sebelum VO, dan persetujuan batch.
- [ ] **[pemilik]** ADR-P01: tambahan field penanda promo, lisensi media, `business_note` (lihat §3 butir 2 dan 4).
- [ ] **[pemilik]** ADR-P03 dan P04: bisa ditunda sampai MVP jalan.
- [ ] **[pemilik]** 3 kandidat suara native Indonesia dari Voice Library ElevenLabs (EXP-04).

## 5. Verifikasi

- [ ] **[Claude]** Zona aman Shopee Video: screenshot UI lewat Chrome di server, ukur area tombol, keranjang, dan caption.
- [ ] **[Claude]** Aturan konten Shopee Video untuk affiliate: disclosure, klaim harga, konten orisinal, durasi/format.
- [ ] **[Claude]** Apakah link Shopee Affiliate mendukung Sub ID per video (halaman *Link Khusus*).
- [ ] **[Claude]** Metrik per video yang tersedia di Shopee Video dan dashboard affiliate (views, retensi, klik, order), dan bisa diekspor atau tidak.
- [ ] **[Claude]** (fase 2) Aturan TikTok dan Threads untuk link affiliate, dan API tautan produk TikTok.

## 6. MVP (urut)

1. [ ] **[Claude]** **Loader + validator paket data:** baca zip/folder, validasi skema `meta.json`, tolak produk tanpa `affiliate_link`/gambar, turunkan `category_regulated`, tulis antrean produk. Disertai fixture tes yang disamarkan.
2. [ ] **[Claude]** **Parameter baru dari temuan §3:** `harga.tampilkan_harga_coret` (dikunci), zona aman Shopee Video (setelah diukur).
3. [ ] **[Claude]** **Generator naskah:** satu panggilan LLM terstruktur per produk dari snapshot + data produk. Keluarannya: naskah per beat, 3 hook, pilihan foto per beat, teks post, dan **sumber setiap klaim** (`key_features[i]`, deskripsi, atau angka feed).
4. [ ] **[Claude]** **Template `film.js` `masalah_solusi`** (ADR-P05):
   - kartu produk dari `transparent_bg`/cover di atas latar warna, Ken Burns, caption dari timing kata, label disclosure persisten,
   - diuji dengan 3 produk shortlist sampai lolos BASELINE Baru Tau + `audit_film.py`.

   Prototipe bisa dimulai sebelum ADR diputuskan.
5. [ ] **[Claude]** **Integrasi Slate:** `buat_voiceover`, `pratinjau_film`, `render_film`, `qa_video` lewat helper seperti `baru-tau-autopilot/tools/slate.py`, dengan foto sebagai base64 JSON (maks 2 MB per file, 8 MB total).
6. [ ] **[Claude]** **QA compliance:**
   - setiap kalimat naskah punya sumber,
   - angka di layar ⊂ data produk,
   - tidak ada harga coret atau persen diskon,
   - disclosure ada di setiap frame (OCR),
   - `compliance_note` dipatuhi,
   - kategori yang klaimnya diatur tidak memakai hook `pain`.
7. [ ] **[Claude]** **Modul konsol `web/modules/affiliate`** (di repo `baru-tau-autopilot`, pola modul `barutau`):
   - unggah/pilih paket data,
   - antrean naskah (setuju/ganti hook/tolak),
   - antrean video final,
   - unduh paket upload,
   - input metrik.
8. [ ] **[Claude]** **Paket upload untuk sesi Chrome:** `final.mp4`, caption, link affiliate, `video_id`, `variant_id`, ditambah baris baru di `uploads/upload_log.csv` (format paket data).
9. [ ] **[Claude]** **Tabel publikasi + log biaya per video:** karakter TTS, token LLM, detik render.

## 7. Setelah MVP jalan

- [ ] Pilot 30 video → hitung σ metrik → mulai eksperimen sesuai doc 12 §4.7, diawali EXP-04 (suara) dan EXP-02 (hook).
- [ ] Ide B2–B19 dari doc 12 §6. B1 (skor produk) sudah dikerjakan pemilik di sisi Chrome (`CONTEXT.md` §4); aff_studio hanya membaca `score`.
- [ ] Fase 2 platform: TikTok, Threads (lewat Zernio yang sudah ada di Slate).
