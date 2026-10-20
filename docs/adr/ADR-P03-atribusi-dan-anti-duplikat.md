# ADR-P03: Atribusi per video (sub_id) dan aturan anti-duplikat publikasi

- **Status:** Proposed (20 Oktober 2026). Nomor final mengikuti urutan ADR Fase 1.
- **Menyentuh:** rute publishing, kontrak feed (link affiliate).
- **Dirujuk dari:** doc 12, K4, §4.1, §4.3, `template.perbandingan.urutan`, B15.

## Konteks

Sistem eksperimen butuh dua hal yang belum ada di rute publishing:
1. **Klik dan order yang bisa ditelusuri ke satu video.** Kalau semua video sebuah produk memakai satu link, klik tidak bisa dibagi ke varian.
2. **Aturan publikasi yang mencegah pola duplikat:**
   - file identik di beberapa akun,
   - varian yang hanya beda tipis di akun yang sama dalam waktu dekat.

   Pola ini berisiko diperlakukan sebagai konten tidak orisinal atau spam (ringkasan pihak ketiga aturan TikTok; Shopee mensyaratkan konten orisinal).

## Keputusan yang diusulkan

**Atribusi**
- Setiap file yang diposting mendapat `video_id` unik dan link affiliate sendiri dengan `sub_id = video_id`, kalau program mendukung Sub ID (cek di dashboard; Shopee custom link punya kolom Sub ID).
- Untuk TikTok Shop, atribusi per video berasal dari anchor produk dan laporan per video.
- Tabel publikasi menyimpan: `video_id`, `variant_id`, `product_id`, `platform`, `akun`, `waktu_tayang`, `link`, `sha256_file`.

**Anti-duplikat (diperiksa penjadwal sebelum menjadwalkan, ditolak keras kalau dilanggar)**
- `sha256_file` yang sama tidak boleh tayang di lebih dari satu akun. Lintas platform di akun milik orang yang sama hanya boleh kalau platformnya berbeda dan rute publishing memang mengizinkan cross-post. Keputusan ini dibiarkan ke prompt induk.
- Dua video produk yang sama harus beda di ≥ 2 grup parameter (`varian.beda_minimal_grup`), dihitung dari snapshot.
- Jeda dan kuota mengikuti parameter berkunci: `posting.jeda_varian_produk_sama_hari`, `posting.maks_per_akun_per_hari`, `posting.jeda_produk_sejenis_jam`.

**Multi-produk (untuk template perbandingan dan kompilasi)**
- Satu video boleh merujuk 2–5 `product_id`. Link mengikuti kemampuan platform (keranjang/showcase berisi beberapa produk, atau komentar tersemat).

## Alternatif yang ditolak

- **Atribusi lewat waktu tayang** (klik di hari yang sama = video hari itu). Bias begitu ada lebih dari satu video per hari.
- **Hash perseptual saja tanpa aturan parameter.** Mudah lolos dengan perubahan warna; aturan "beda ≥ 2 grup" lebih jelas maknanya.

## Konsekuensi

- Penjadwal posting butuh tabel publikasi dan cek di atas.
- Laporan affiliate perlu diimpor per `sub_id`.
- Template `perbandingan` dan ide B15 tetap usulan sampai bagian multi-produk diterima.
