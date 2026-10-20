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
- [x] Paket data 2026-10-19 dibaca: 9 produk `link_ready` (temuan di §3); 71 gambar diunduh ulang.
- [x] `tools/paket.py`, `tools/siapkan_film.py`, `tools/pratinjau.py`, prototipe `templates/kartu/film.js` + tes (MVP butir 1, 2, dan sebagian 4).

## 3. Temuan dari paket data 2026-10-19

1. **Gambar tidak ada di zip.** Semua folder `products/<id>/images/` kosong. Sudah diatasi 20 Oktober: 71 gambar diunduh ulang dengan `fetch_images_zip.py` ke `/data/apps/affiliate-data/2026-10-19/products/<id>/images/`, ditambah `affiliate_assets_2026-10-20.zip` (28,6 MB). Semuanya JPEG yang valid.
   - Sisi pendek 1.024 px untuk hampir semua foto.
   - Satu foto Omura 512 px dan satu foto pupuk 616 px. Keduanya di bawah `foto.sisi_pendek_min_px` (800), jadi hanya boleh tampil sebagai kartu kecil.
   - Omura hanya punya 3 foto, kurang untuk 8 beat. Foto dipakai ulang dengan crop berbeda, atau pakai video penjual (ADR-P01, lisensi).
2. **Field yang sudah memenuhi ADR-P01:**
   - `scraped_at` (= waktu harga diambil),
   - `sold_30d` sebagai teks tampilan ("10RB+"),
   - `reviews` (= jumlah rating),
   - `category`,
   - `has_video`,
   - `transparent_bg`, tapi **bukan foto transparan**: JPEG RGB tanpa kanal alpha. 5 dari 9 produk `null`; dari 4 yang terisi, 3 sudah ada di daftar `images` dan 1 (Hanasui) gambar terpisah yang ikut diunduh (`<id>_tbg.jpg`). Kartu produk di atas latar warna butuh penghapus latar (mis. `rembg`, CPU) atau memakai foto utuh sebagai kartu.

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
7. **Teks yang tercetak di foto penjual ikut tampil di video, dan sering bertentangan dengan data produk.** Contoh:
   - Kipas: foto 6 "16900 r/min" (data: 23.000 RPM); foto 0 "100 level" dan "UP to 10H" (data: 6 level, 2,5–20 jam); foto 7 "10.7 Hrs".
   - Keset: foto 2 "1S/5S/10S" dan foto 1 "bebas formaldehida" (tidak ada di fitur).
   - Hanasui: cover "Dermatologically tested" (tidak ada di fitur).

   Teks di layar adalah klaim, apa pun asalnya. Akibatnya:
   - generator naskah memilih foto dan crop yang tidak memuat teks bertentangan,
   - QA compliance membaca teks foto dengan OCR (butir 12),
   - foto yang bertentangan ditandai, misalnya `foto.tolak`, di kartu naskah tahap 1.
8. **Angka di caption masih ditulis dengan huruf** ("dua puluh tiga ribu"), karena caption = teks VO. Generator naskah perlu menulis dua versi per kalimat: `vo` (angka dengan huruf, untuk TTS) dan `layar` (digit, untuk caption), seperti aturan Baru Tau.
9. **Repo ini publik.** Paket data mentah tidak di-commit: ada email pemilik di `CONTEXT.md`, link affiliate, dan data toko. Tes memakai fixture yang sudah disamarkan.

## 4. Keputusan pemilik (yang lain menunggu ini)

- [x] **[pemilik]** Gambar 2026-10-19: diunduh ulang dengan `fetch_images_zip.py` (disetujui pemilik 20 Oktober).
- [ ] **[pemilik]** Paket berikutnya: sertakan gambar di zip, atau jalankan `fetch_images_zip.py` sebagai langkah tetap. Folder Download Chromium (`/data/storage/chrome-webgui/Downloads`, milik `opc`, mode 700) belum terbaca user `ubuntu`. Kalau mau dipakai langsung, beri izin baca grup/ACL, misalnya `setfacl -R -m u:ubuntu:rX`; Claude tidak mengubah izin folder profil browser tanpa diminta.
- [x] **[pemilik]** Lokasi paket data di server: `/data/apps/affiliate-data/<tanggal>/` (di luar repo; repo publik).
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

1. [x] **[Claude]** **Loader + validator paket data:** `tools/paket.py` (folder atau zip, produk ditolak/peringatan, `kategori_diatur`, angka di `video_angle` yang tidak ada di `key_features`, umur harga). Paket 2026-10-19: 9/9 siap. Tes dengan fixture yang disamarkan (`tests/fixture.py`).
2. [x] **[Claude]** **Parameter baru dari temuan §3:** `harga.tampilkan_harga_coret`, `compliance.kategori_diatur`, `disclosure.teks` (dikunci), `foto.embed_total_maks_kb`. Zona aman Shopee Video masih angka sementara (480 px) sampai diukur.
3. [ ] **[Claude]** **Generator naskah:** satu panggilan LLM terstruktur per produk dari snapshot + data produk. Keluarannya: naskah per beat, 3 hook, pilihan foto per beat, teks post, dan **sumber setiap klaim** (`key_features[i]`, deskripsi, atau angka feed).
4. [~] **[Claude]** **Template `film.js`** (ADR-P05). Prototipe `templates/kartu/film.js` sudah ada:
   - kartu foto di atas latar warna dari foto cover, Ken Burns ke titik fokus, crop detail di beat panjang, punch-in di kata disorot,
   - teks kunci per beat, chip bukti dari data feed, caption per frasa dari timing kata, label disclosure persisten.

   Bahan disusun `tools/siapkan_film.py` (`isi.json` + `foto.json` + `naskah.txt` + `scenes.json`), dan dipratinjau lokal dengan `tools/pratinjau.py` (Chromium headless, tanpa Slate). Sudah dicoba dengan naskah contoh untuk Hanasui, Keset, dan Kipas (`/data/apps/affiliate-data/2026-10-19/naskah/`, di luar repo): durasi 19–22 detik, 257–292 karakter VO.

   **Belum:**
   - render penuh lewat Slate + `qa_video`,
   - penilaian BASELINE di HP,
   - transisi selain potong keras,
   - loop ke frame 0.
5. [ ] **[Claude]** **Integrasi Slate:** `buat_voiceover`, `pratinjau_film`, `render_film`, `qa_video` lewat helper seperti `baru-tau-autopilot/tools/slate.py`, dengan foto sebagai base64 JSON. Batas renderer Slate 2 MB **total** untuk semua file film (bukan 8 MB seperti helper Baru Tau).
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
