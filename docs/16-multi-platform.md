# 16 — Multi-platform: satu master, teks per platform (22 Oktober 2026)

Permintaan pemilik: Baru Tau dan affiliate sama-sama berakhir sebagai video yang dibagikan ke beberapa platform (Shopee Video, TikTok, Threads lewat Zernio). Video dan copy harus cocok per platform. Riset tiga agen 22 Okt; penanda **[resmi]**, **[data]**, **[praktisi]** seperti doc 15.

## 1. Keputusan

**Satu video master per produk, ajakan universal "cek di bawah", teks berbeda per platform.**
- Di Shopee Video keranjang oranye ada di kiri bawah, di TikTok keranjang kuning (anchor produk) di kiri bawah, di Threads link ada di balasan pertama (di bawah post). "Cek di bawah ya" + panah ke kiri bawah benar di ketiganya, tanpa menyebut fitur platform lain (TikTok Shop melarang ajakan ke luar platform; menyebut Shopee di TikTok = pelanggaran) [resmi-US] https://seller-us.tiktok.com/university/essay?knowledge_id=4588077398099713 (22-06-2026), [praktisi-ID] techno.viva.co.id/platform/4486.
- Render dan voiceover hanya sekali: varian video per platform butuh render (dan VO CTA) terpisah, dan Slate memosting video final sebuah job (satu final per job). Riset tidak menemukan data bahwa video "native" per platform mengalahkan unggahan identik secara terukur; yang terbukti merugikan hanya watermark platform lain [resmi] (Shopee help 71981; Instagram, Facebook 2025). Selalu unggah dari master pipeline.
- Platform khusus (`shopee_video` / `tiktok` / `threads`, doc 15) tetap bisa dipilih saat Produksi kalau satu video memang hanya untuk satu platform; bawaan sekarang `semua`.

**Zona aman = irisan yang paling ketat** (TikTok dan Reels): atas 240 px, bawah 660 px (dasar caption y = 1.260), kiri 120 px, kanan 240 px (x ≤ 840; tombol kanan TikTok mulai y ≈ 840). Turunan template iklan TikTok [praktisi] adchecklab.com (2025), upload-post.com; Reels bawah 35% (≈670 px) [praktisi mengutip Meta]. Threads dan Shopee Video tidak punya angka resmi; Threads mungkin memotong ke 4:5 di tengah (y 285–1.635, sumber bertentangan), yang sudah tercakup.

**Disclosure di video: "Konten afiliasi"** (bukan "Link afiliasi": di TikTok, "link" terbaca sebagai ajakan ke luar; pedoman berbagi konten TikTok melarang aplikasi menumpuk link/teks promosi [resmi] developers.tiktok.com/doc/content-sharing-guidelines, 04-08-2026). OCR compliance tetap mencari "afiliasi".

## 2. Teks per platform (`teks_platform.json`, ditulis kreator, dicek `produksi.py teks`)

| Platform | Isi | Aturan |
|---|---|---|
| Shopee Video | `caption` | ≤ 150 karakter (batas form, diamati 22 Okt), tidak bisa diedit setelah posting [resmi-SG], tanpa "link"; ajakan ke keranjang oranye |
| TikTok | `caption` | ≤ 2.200 [resmi API]; kalimat pertama berisi kata kunci produk (TikTok SEO [resmi Creator Academy]); 3–5 hashtag spesifik, tanpa #fyp/#viral [praktisi; batas 5 dilaporkan 2025]; tanpa "Shopee", "link", "bio"; ajakan "keranjang kuning" |
| Threads | `teks`, `topik`, `balasan` | `teks` ≤ 500 byte UTF-8 (emoji dihitung per byte [resmi]), **tanpa link** (link = engagement terendah, 2,34% [data] Buffer 2026; Meta "tidak memberi banyak nilai" pada link [resmi]); baris "🔊 Narasi: suara AI" (Meta mewajibkan label untuk narasi AI realistis; API tidak punya field label [resmi] meta.com/help/artificial-intelligence/1783222608822690); `topik` 1 tag 1–50 karakter tanpa "." dan "&" [resmi]; `balasan` = balasan pertama berisi `{LINK}` + "link afiliasi" (Meta: link afiliasi = branded content [resmi via SMT 10-03-2026]) |

Semua: klaim hanya dari data produk; angka yang tidak ada di data ditolak; tanpa Rp/%/diskon/promo/gratis/termurah.

## 3. Rantai posting

| Platform | Jalur | Manual tersisa |
|---|---|---|
| Shopee Video | Telegram (video + caption + link) → aplikasi HP | unggah, Tambah Produk, toggle "Konten dihasilkan AI" (Seller Centre web hanya produk toko sendiri, diuji 22 Okt) |
| Threads | Slate `posting` (Zernio), `teks` + `reply_pertama` = `balasan` dengan link | label "AI"/"paid partnership" di aplikasi kalau mau (tidak ada di API) |
| TikTok | Slate `posting` platform tiktok (perlu dukungan TikTok di Slate): `video_made_with_ai`, `commercialContentType: brand_content`, affiliate sebagai **draft** | **affiliate**: tautkan produk TikTok Shop di aplikasi (API tidak bisa memasang anchor [resmi] docs.zernio.com/platforms/tiktok/fields); Baru Tau: tidak ada |

## 4. Tindakan pemilik

1. **TikTok Shop Affiliate** (hanya kalau affiliate mau komisi dari TikTok): akun ≥ 600 followers, 18+, posting dalam 28 hari terakhir [resmi] seller-id.tokopedia.com knowledge_id=8818745439487745. Produk harus ada di TikTok Shop (link Shopee tidak boleh). Menautkan produk ke video mensyaratkan suara dari Commercial Music Library [resmi-US] knowledge_id=5178002307598122: musik sintesis kita mungkin perlu diganti `musicSoundInfo` CML (Business) — uji pada draft pertama.
2. **Zernio–TikTok**: pastikan aplikasinya lolos audit TikTok (kalau belum, semua post privat [resmi]) dan tersambung sebagai **Business** (`video_made_with_ai` dan musik CML hanya untuk Business [resmi Zernio]).
3. **Threads di Shopee Affiliate**: Media Sosial → "Lainnya" (Threads tidak ada di daftar contoh [resmi] help.shopee.co.id 200825); Sub ID per platform kalau link dibuat ulang.

## 5. Baru Tau (repo baru-tau-autopilot)

TikTok: caption = kata kunci topik + pertanyaan di kalimat pertama, 1 kalimat fakta tanpa membocorkan jawaban, ajakan simpan/bagikan, 3–5 hashtag (#barutau #faktaunik #<topik>); `video_made_with_ai: true`, komersial `none`; cover dari kartu judul. Threads: tambah baris "🔊 Narasi: suara AI". Pakai paket posting yang sama (skill `paket-posting`), dicatat di doc ini sebagai acuan.
