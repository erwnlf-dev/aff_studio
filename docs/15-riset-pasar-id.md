# 15 — Riset pasar Indonesia untuk video affiliate (20 Oktober 2026)

Dikerjakan untuk pertanyaan pemilik "untuk video affiliate yang proper apa sudah OK?" setelah empat video pertama (keset, kipas, Hanasui, Kalisha) lolos QA teknis. Penanda: **[resmi]** halaman Shopee/TikTok/BPOM, **[resmi-MY/SG]** halaman resmi pasar lain, **[data]** studi/survei, **[praktisi]** blog/agensi/kreator. "Tidak ditemukan" berarti dicari dan tidak ada.

## 1. Kesimpulan

Video kita sudah rapi secara teknis dan patuh. Tapi untuk pasar Indonesia ada tiga celah:
1. **Komisi:** voiceover AI saja sudah mewajibkan label AI, dan di MY/SG label itu mematikan Komisi Shopee. Status Indonesia belum terverifikasi; **uji satu video berlabel sebelum produksi diperbanyak** (§4).
2. **CTA salah tempat:** keempat video ditutup "cek di link", padahal produk Shopee Video ada di keranjang oranye kiri bawah dan tautan keluar aplikasi dilarang (§2).
3. **Struktur seragam dan hook lemah:** keempat video berpola identik (pertanyaan → masalah → "Kenalin…" → 2 fitur → cap → CTA). Praktisi ID menyarankan hook masalah/nilai/hasil ≤ 8 kata tanpa pengantar, dan Shopee menilai konten repetitif tidak valid untuk level kreator (§2, §3).

Aturan yang lahir dari dokumen ini: `cta.tempat`, `hook.vo_kata_maks`, `template.variasi`, `variasi.beda_dari_terakhir` (registry, sumber `R-PASAR-ID`), dicek `siapkan_film.py` (perintah `naskah`), plus `panahKeranjang` di kit.

## 2. Shopee Video

- **Keranjang oranye di kiri bawah video** [resmi] https://shopee.co.id/inspirasi-shopee/keranjang-orange-shopee-video/ (29-10-2022, cek ulang di aplikasi). Produk ditautkan lewat "Tambah Produk" [resmi] https://help.shopee.co.id/portal/10/article/156367.
- **Tautan keluar aplikasi dilarang** di pedoman komunitas Shopee Video [resmi-SG] https://help.shopee.sg/10/article/171845. Jadi "link di bio"/"cek di link" tidak relevan di Shopee Video.
- **CTA eksplisit ke keranjang** adalah saran praktisi yang paling konsisten. CTA yang tidak menyuruh menekan keranjang disebut penyebab komisi gagal [praktisi] https://masoemuniversity.ac.id/?p=125854 (27-08-2026). Gunakan teks kontras dan panah ke keranjang, maksimal 2 kali [praktisi] https://www.dami.co.id/blog/practical-tiktok-affiliate-video-structure-from (18-09-2026).
- **Ranking** tidak dipublikasikan. Tips resmi: layar penuh, sound/hashtag tren, tag produk, 2–3 video per hari [resmi] https://shopee.co.id/inspirasi-shopee/video-promosi-produk/ (15-12-2023). Banyak posting di hari yang sama dan konten identik berulang termasuk pelanggaran spam (bobot 0) [resmi] https://help.shopee.co.id/portal/4/article/71981.
- **Level Kreator ID**: video harus orisinal, penilaian 28 hari, Influence Score "3M" (Menarik, Menghibur, Menjual) [resmi] https://help.shopee.co.id/portal/10/article/199900. SG: video repetitif (gaya, caption, produk serupa) tidak valid [resmi-SG] https://help.shopee.sg/portal/10/article/199073 (4-09-2026).
- **Komisi video**: sejak 3-11-2025 Komisi Shopee di Live/Video disebut hanya untuk kreator Golden Tick, pada produk Komisi XTRA dari toko Star/Star+/Mall. Kreator lain praktis hanya XTRA [praktisi] https://meamcn.com/komisi-affiliate-shopee/ (19-10-2026). Golden Tick butuh Level 2 dan konten orisinal [resmi] https://help.shopee.co.id/portal/4/article/95291.
- **Durasi** 15–20 detik, hook di 3 detik pertama [praktisi] Jubelio (16-10-2025), Lemon8. Video kita 18,8–21,4 detik: sesuai.
- **Disclosure "Link afiliasi"** tidak diwajibkan S&K Shopee maupun regulasi Indonesia; aman dipertahankan [resmi] https://help.shopee.co.id/portal/4/article/71217, /109485, /71216.

## 3. Format, hook, dan naskah yang dipakai affiliator Indonesia

- **#RacunShopee** (rekomendasi, review, unboxing) adalah jenis video yang paling banyak dibuat dan ditonton di Shopee Video [resmi] (29-10-2022, URL §2).
- **Tanpa wajah** yang disebut berhasil: unboxing, demo tangan, stop-motion, POV. Slideshow teks + musik dinilai paling lemah [praktisi] https://www.industry.co.id/read/155846/ (12-09-2026), https://techno.viva.co.id/platform/5639-... (12-04-2025).
- **Akun affiliate animasi/kartun di Indonesia: tidak ditemukan**, baik yang berhasil maupun yang gagal. Format kita belum punya pembanding, jadi metrik sendiri (klik produk, CTR) yang menentukan.
- **Struktur yang disarankan**: masalah spesifik di 0–3 s (tanpa "Halo semuanya" atau pengantar), solusi di 3–5 s, demo di tengah, CTA setelah hasil terlihat. Hook sekitar 8 kata [praktisi] dami.co.id (18-09-2026).
- **Hook yang dominan** di contoh Indonesia: nilai/harga ("Harga aslinya di atas 100 ribu…"), rasa rugi/FOMO ("Nyesel deh beli offline…"), dan hasil dengan waktu ("…dalam 3 hari") [praktisi] Lemon8, VIVA, Industry.co.id. Hook harga dan klaim waktu tetap **tidak** kita pakai (kunci `harga.*`, klaim hanya dari data); hook nilai tanpa angka dan hook hasil dari `key_features` boleh.
- **Pemicu belanja**: gratis ongkir (72%) dan diskon (61%) [data] Populix, Kontan (Jul 2023). Kata "promo"/"diskon" tetap diblok di layar oleh `qa_compliance` (§5). Yang selalu benar: "cek harganya di keranjang oranye".
- **Demo** dinilai paling berguna untuk beauty, teknologi, dan kebugaran [resmi] https://ads.tiktok.com/business/id/blog/tiktok-short-video-best-practice (24-11-2024). Swatch/tekstur adalah kunci beauty [praktisi]. Untuk hijab/fashion: data try-on tidak ditemukan.

## 4. Konten AI, TTS, dan komisi

- **Shopee ID**: konten AI mencakup "narasi atau suara yang dihasilkan AI"; toggle "Konten Dihasilkan AI" wajib, caption/#AI tidak menggantikannya, ada deteksi otomatis, sanksi sampai suspend [resmi] https://help.shopee.co.id/portal/4/article/197077.
- **Shopee MY**: "For creators who label their content as AI-generated, Shopee commissions will be turned off… remain eligible to receive AMS commissions"; label otomatis tidak bisa dihapus [resmi-MY, via cuplikan] https://seller.shopee.com.my/edu/article/27547; diulang BigSeller (12-06-2026). **Versi ID tidak ditemukan.**
- **Shopee SG**: konten AI tidak diizinkan untuk Creator Levelling (4-09-2026); AIGC wajib toggle, poin penalti sampai hilang hak komisi (1-08-2026) [resmi-SG] https://help.shopee.sg/portal/10/article/199073, /201777.
- **TikTok**: label AI (toggle + C2PA); TikTok Shop US mensyaratkan ≥ 3 detik konten dinamis dan melarang suara AI di LIVE [platform, via pers] https://ppc.land/tiktok-shops-quality-rules-ban-ai-voices-and-still-images-from-lives/ (23-05-2026). Toggle commercial content wajib untuk tautan afiliasi.
- **Penerimaan penonton**: "suara Google" (TTS bawaan TikTok) dikenal luas. Data penolakan TTS dalam video jualan tidak ditemukan. Studi kecil: pengaruh konten AI ke minat beli lewat persepsi keaslian dan kepercayaan [data] Ekonomipedia (3-08-2026, n = 32); positif ke kepercayaan pada Gen Z Surabaya [data] (2-06-2026, n = 149).

**Tindakan pemilik:** unggah 1 video dengan toggle AI menyala dan lihat apakah komisi tercatat di dashboard affiliate (Komisi Shopee vs XTRA/AMS). Kalau Komisi Shopee hilang, pilihan yang jujur adalah suara rekaman pemilik ditambah sebagian footage produk nyata, bukan menyembunyikan label (doc 14 §1, ADR-P01/EXP-04).

## 5. Regulasi

- **Kosmetik** (Hanasui): PerBPOM 18/2024 (transisi 12 bulan sejak 15-11-2024). Promosi harus objektif dan tidak menyesatkan, klaim harus berbukti, testimoni tidak boleh mewakili masyarakat luas, dan pemeran tidak boleh tenaga kesehatan. Iklan oleh influencer/masyarakat ikut diatur [resmi] standar-otskk.pom.go.id, waskos.pom.go.id (FAQ Jan 2024). Aturan kita (klaim hanya dari data, tanpa before/after untuk kategori diatur) sudah sejalan.
- **Label AI pemerintah**: Perpres AI menunggu tanda tangan (Kontan, 3-09-2026); Komdigi masih mengkaji label wajib konten AI (CNN Indonesia, 19-10-2026). Belum ada aturan yang berlaku.
- **Musik**: akun bisnis TikTok hanya boleh Commercial Music Library [resmi] https://ads.tiktok.com/resources/help/article/commercial-music-library (Jul 2025). Musik sintesis kita aman.

## 6. Yang belum diketahui

- Status komisi video berlabel AI di Shopee **Indonesia** (uji upload, §4).
- Angka zona aman Shopee Video (doc 14 §2: perlu screenshot pemutaran).
- Perbandingan konversi wajah vs tanpa wajah, kartun vs footage nyata, gaul vs baku: tidak ada data publik. Ini perlu diukur sendiri lewat metrik Pusat Kreator (doc 12 K7).
