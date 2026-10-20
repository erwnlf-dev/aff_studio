# 14 — Aturan platform (riset 20 Oktober 2026)

Hasil verifikasi TODO §5. **[RESMI]** = halaman resmi Shopee/TikTok/Meta; **[RESMI-SG/MY]** = halaman resmi pasar lain (versi Indonesia tidak ditemukan); **[BLOG]** = pihak ketiga. "Tidak ditemukan" berarti dicari dan tidak ada, bukan diasumsikan.

## 1. Shopee Video (fase 1)

**Label AI wajib.** Konten yang sepenuhnya dibuat atau banyak disunting dengan AI wajib diberi label. Ini **termasuk narasi atau suara yang dihasilkan AI** dan gambar produk yang dibuat atau diperbaiki AI.
- Caranya: toggle **"Konten Dihasilkan AI"** di layar Posting. Hashtag tidak menggantikan toggle ini.
- Konten tanpa label bisa diturunkan atau disanksi.
- Video kita memakai VO ElevenLabs, jadi **toggle ini wajib dinyalakan di setiap unggahan** (daftar periksa di halaman Unggah konsol).
- Sumber: https://help.shopee.co.id/portal/10/article/197077 [RESMI]

**Konsekuensi label AI:** kriteria Top Creator mengecualikan repost "termasuk video AI generated" dan menyarankan suara serta wajah kreator sendiri. https://help.shopee.co.id/portal/4/article/201359 [RESMI]. Ini ikut menimbang pemilihan suara (EXP-04) dan opsi rekaman suara pemilik.

**Harga dan promo.**
- Harga, diskon, dan bundling harus sama dengan halaman produk "saat Video di-upload".
- Dilarang: klaim Flash Sale kedaluwarsa, diskon berlebihan, syarat promo yang tidak disebut.
- Video lama harus diperbarui atau dihapus kalau harga berubah.
- Sanksi: keranjang oranye dicabut dan 1 poin.
- Ini mendukung keputusan **tanpa harga di video** (kunci `harga.diucapkan`, `harga.tampilkan_harga_coret`, `harga.mode = tanpa_angka`).
- Sumber: https://help.shopee.co.id/portal/4/article/199053 [RESMI]

**Pelanggaran lain** (https://help.shopee.co.id/portal/4/article/71981 [RESMI]):
- watermark platform lain,
- repost/spam konten yang sama,
- hak cipta/merek dagang (berat, 12 poin),
- musik tanpa lisensi (audio dibisukan),
- URL tak dikenal.

**Syarat Affiliate Shopee** (https://help.shopee.co.id/portal/4/article/71217 [RESMI]):
- 7.1: tidak menyesatkan.
- 2.7(i): **tidak boleh memakai nama, merek dagang, atau logo Shopee** di media sosial yang didaftarkan. Video kita tidak memakainya; CTA cukup "cek di link".
- 7.2(b): materi milik penjual hanya dengan hak/persetujuan. Ini mendukung ADR-P01 (lisensi media). Cutout foto penjual untuk mempromosikan produk penjual itu sendiri adalah praktik umum affiliate; risikonya dicatat di ADR-P01.
- 7.2(e): tidak ada link e-commerce lain.

Tidak ditemukan kewajiban hashtag #ad di Shopee Video. Label "Link afiliasi" di video tetap dipakai (kunci compliance).

**Format dan menautkan produk.**
- Minimal 3 detik.
- Seller Centre bisa mengunggah dari PC, sampai 30 video sekaligus.
- Disarankan jarak ≥ 1 jam antar postingan (registry `posting.jeda_min_antar_post_menit` = 180, sudah memenuhi). https://seller.shopee.co.id/edu/article/12942 [RESMI]
- Produk ditautkan lewat **Tambah Produk** di aplikasi (affiliate dan penjual, maksimal 6 produk), lalu tampil di ikon keranjang. Link `s.shopee.co.id` **tidak ditempel**; yang dipakai tag produk. https://help.shopee.co.id/portal/10/article/156367 [RESMI]
- Durasi maksimal, ukuran file, dan rasio resmi: tidak ditemukan. Pihak ketiga menyebut MP4, 5 detik–3 menit, ≥ 480p, 9:16 (BigSeller [BLOG]).

## 2. Zona aman Shopee Video

- **Angka resmi tidak ditemukan.**
- Satu-satunya fakta resmi: keranjang oranye ada di **kiri bawah** video. https://shopee.co.id/inspirasi-shopee/keranjang-orange-shopee-video/ [RESMI]
- Angka zona aman TikTok dari pihak ketiga tidak seragam: bawah 480–707 px, kanan 140–242 px (socialync, revid, adkit [BLOG]).

**Dipakai sementara:**
- Registry `zona_aman.shopee_video.bawah_px` = 620: keranjang dan caption aplikasi di kiri bawah.
- Video yang sudah jadi menaruh dasar caption di y = 1.470 (450 px dari bawah). Keranjang di kiri bawah bisa menutupi sebagian caption kiri.

**Tindakan [pemilik]:** kirim satu screenshot pemutaran Shopee Video dengan produk tertaut (HP, layar penuh). Dari situ angka pasti diukur, lalu `buatCaption` (kit) dan BIBLE disesuaikan. Sampai ada screenshot, kreator diminta menjaga aksi penting di atas y = 1.300 (BIBLE).

## 3. Atribusi dan laporan

- **Shopee Video:** atribusi per video lewat **tag produk di aplikasi** dan laporan Performa Konten (Video). Tidak perlu Sub ID. https://help.shopee.co.id/portal/4/article/123077 [RESMI]
  - Laporan memuat klik, pesanan, produk terjual, Pesanan (Rp), dan Komisi Kotor.
  - Diperbarui harian pukul 16.30 WIB.
  - Ekspor CSV untuk Indonesia: tidak ditemukan.
- **Sub ID** (untuk link yang dibagikan di luar Shopee Video, misalnya Threads/Facebook): Link Khusus mendukung sampai 5 Sub ID, dengan format `&sub_id=v1-v2-v3-v4-v5`. https://help.shopee.co.id/portal/10/article/184879 [RESMI]. Laporan per Sub ID tersedia di SG; untuk ID belum terkonfirmasi [RESMI-SG].
- **Validasi komisi:** sampai ±14 hari kerja, dan pemeriksaan fraud bisa sampai ±2 bulan. Pembayaran mingguan, biaya 0,5% (maks Rp20.000), wajib NPWP. https://help.shopee.co.id/portal/10/article/124523, https://help.shopee.co.id/portal/10/article/174001 [RESMI]
- **Metrik per video di aplikasi** (Pusat Kreator → Performa Video): penonton, suka, komentar, bagikan, klik produk, pesanan, CTR. https://help.shopee.co.id/portal/4/article/201194 [RESMI]
  - Watch time dan retensi: tidak ditemukan.
  - API untuk kreator: tidak ditemukan.
  - Akibatnya metrik `hold_3s` dan `avg_watch_pct` (doc 12 §4.2) **tidak tersedia di Shopee Video**. Eksperimen di Shopee memakai views, klik produk, pesanan, dan CTR, diinput manual (doc 12 K7).

## 4. Fase 2: TikTok dan Threads

- **TikTok Shop Indonesia** (lewat Tokopedia Seller Center):
  - Syarat affiliate: ≥ 600 pengikut, 18+, posting dalam 28 hari terakhir, KTP dan data pajak.
  - Produk ditautkan dengan "Add Link" dari Showcase (maks 10 per video), atau ke video yang diposting ≤ 30 hari. https://seller-id.tokopedia.com/university/essay?knowledge_id=6837812658128641 [RESMI]
  - API affiliate TikTok untuk Indonesia: tidak ditemukan.
- **Link Shopee di TikTok:** kebijakan TikTok Shop melarang mengalihkan pengguna ke luar platform [RESMI-MY]. Fase 2 TikTok memakai produk TikTok Shop, **bukan** link Shopee.
- **Disclosure TikTok:** komisi affiliate termasuk Branded Content, jadi toggle "Disclose commercial content" wajib. Konten AI yang realistis wajib berlabel AI. https://www.tiktok.com/legal/page/global/bc-policy/en [RESMI]
- **Threads:**
  - Konten bermerek memakai "Mark as paid partnership" [RESMI].
  - Aturan khusus link affiliate: tidak ditemukan.
  - Integrasi resmi Shopee–Meta hanya untuk Facebook Feed/Reels. https://help.shopee.co.id/portal/10/article/186601 [RESMI]
  - Pastikan Threads disetujui sebagai kanal promosi di akun affiliate sebelum dipakai.
