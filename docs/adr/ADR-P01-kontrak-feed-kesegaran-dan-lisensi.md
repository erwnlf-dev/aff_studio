# ADR-P01: Kontrak feed — kesegaran harga, tampilan bukti, lisensi media

- **Status:** Proposed (20 Oktober 2026). Nomor final mengikuti urutan ADR Fase 1.
- **Menyentuh:** kontrak feed.
- **Dirujuk dari:** doc 12, K5, K6, §3.7, B11.

## Konteks

Aturan inti: video tidak boleh memuat klaim di luar data feed. Data feed sendiri punya umur:
- harga marketplace berubah per jam (flash sale, voucher, harga coret),
- rating bisa turun,
- jumlah terjual hanya naik.

Video yang dibakar dengan angka hari ini tetap tayang berbulan-bulan. Tanpa tahu kapan angka diambil dan dalam bentuk apa marketplace menampilkannya, pipeline tidak bisa membedakan angka yang aman dari angka yang akan basi.

Foto dan video penjual juga dipakai tanpa keterangan hak pakai, padahal program affiliate dan platform menuntut konten orisinal.

## Keputusan yang diusulkan

Tambahkan field berikut ke kontrak feed. Semuanya opsional, supaya feed lama tetap sah. Pipeline memperlakukan field yang tidak ada sebagai "tidak boleh dipakai".

| Field | Tipe | Dipakai untuk |
|---|---|---|
| `price_captured_at` | ISO 8601 WIB | `harga.umur_data_maks_jam`; tanpa field ini beat harga selalu dibuang |
| `price_is_promo` | bool | Harga promo (flash sale, voucher) tidak pernah tampil sebagai angka |
| `price_display` | string persis seperti di marketplace | Angka di layar disalin, bukan diformat ulang |
| `sold_display` | string persis ("10rb+ terjual") | Bukti sosial tanpa pembulatan ke atas |
| `rating`, `rating_count` | angka | `bukti.rating_min_tampil`, `bukti.jumlah_rating_min_tampil` |
| `category_regulated` | bool | Memblok hook `pain` dan klaim manfaat (kesehatan, kosmetik, suplemen) |
| `media[]` | `{url, kind: photo/video, source: seller/brand/own, license: none/affiliate_allowed/explicit, has_watermark}` | Pemilihan foto, B11, `foto.tolak_watermark_pihak_lain` |
| `review_snippets[]` | `{text, rating, captured_at}`, hanya kalau program mengizinkan | Membuka format bukti "kutipan ulasan" (masih perlu persetujuan terpisah) |

## Alternatif yang ditolak

- **Mengambil harga sendiri saat render (scraping).** Ini rute data baru yang bisa melanggar ketentuan marketplace, dan tidak menyelesaikan basinya angka setelah tayang.
- **Tidak pernah menampilkan harga.** Ini aman, dan memang menjadi default MVP. Tapi tanpa field ini, EXP-09 tidak pernah bisa menjawab apakah harga menaikkan klik.

## Konsekuensi

- Penyedia feed perlu menambah field. Sampai itu terjadi, `harga.mode` tetap `tanpa_angka` dan EXP-09 berstatus antre.
- Validasi feed menolak `price_display` yang tidak cocok dengan `price` numerik, supaya angka yang salah format tidak lolos.
- Registry tidak berubah: aturan yang memakai field-field ini sudah ada sebagai parameter berkunci.
