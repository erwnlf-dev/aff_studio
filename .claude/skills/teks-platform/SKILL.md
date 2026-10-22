---
name: teks-platform
description: Tulis teks_platform.json video affiliate (produksi langkah 12) - caption Shopee Video (<= 150 karakter), caption TikTok (kata kunci + 3-5 hashtag, tanpa Shopee/link), dan teks + topic tag + balasan pertama berisi link untuk Threads, lalu cek dengan `python3 tools/produksi.py <folder> teks`. Pakai setelah cek akhir, sebelum selesai.
---

# Teks per platform (doc 16)

Satu video master dipakai di Shopee Video, TikTok, dan Threads; ajakan di video universal ("cek di bawah"). Yang berbeda
per platform hanya teks ini. Platform yang wajib ada mengikuti `PLATFORM TUJUAN` di prompt (`semua` = ketiganya).

## Aturan bersama (dicek `teks`)

1. **Klaim sama dengan video**, hanya dari `key_features` dan `data_layar.json`. Angka yang tidak ada di data ditolak.
2. **Tanpa** Rp, %, diskon, promo, gratis, termurah; tanpa "Kenalin", "Fun fact", tanda pisah panjang (—).
3. **Suara manusia, bukan copywriter:** orang yang beneran pakai lalu cerita ke teman. Huruf kecil boleh, kalimat lisan
   ("ternyata", "udah", "nggak"), satu kata ganti "kamu". Baca keras-keras; kalau terdengar seperti iklan, tulis ulang.
4. **Sudut berbeda per platform** (konten repetitif dinilai tidak orisinal): jangan salin kalimat yang sama ke tiga
   tempat.

## Shopee Video: `{"caption": "..."}`

- ≤ 150 karakter (batas form; tidak bisa diedit setelah posting). Penonton sudah di toko: langsung manfaat + bukti
  dari data + ajakan ke keranjang oranye. Tanpa link/bio.
- Pola: `<manfaat konkret> + <bukti singkat> + cek keranjang oranye ya`.
- Contoh: `keset kamar mandi yang airnya langsung kering, alasnya nggak geser. ratingnya 4,9, cek keranjang oranye ya`

## TikTok: `{"caption": "..."}`

- Kalimat pertama = kata kunci yang diketik orang (nama benda + kegunaan), karena TikTok mencari dari caption, VO,
  dan teks layar. Lalu satu alasan konkret, lalu ajakan "cek keranjang kuning ya".
- **3–5 hashtag spesifik** di akhir (#kesetdapur #rumahminimalis #racuntiktok), tanpa #fyp/#viral.
- **Dilarang:** Shopee, link, bio, keranjang oranye (TikTok Shop melarang ajakan ke luar platform).
- Catatan: komisi TikTok hanya dari produk TikTok Shop yang ditautkan pemilik di aplikasi; teksmu tetap ditulis.

## Threads: `{"teks": "...", "topik": "...", "balasan": "..."}`

- `teks` ≤ 500 byte (emoji dihitung beberapa byte; maksimal 1 emoji selain baris narasi). Bercerita: masalah
  sehari-hari 1 kalimat → bagaimana produk ini membantu 1–2 baris → pertanyaan ke pembaca. **Tanpa link dan tanpa
  hashtag.** Baris terakhir wajib: `🔊 Narasi: suara AI` (Meta mewajibkan label narasi AI; API tidak bisa memasangnya).
- `topik`: satu topic tag 1–50 karakter tanpa ".", "&", "#" (mis. "Rumah Tangga", "Skincare", "Gadget").
- `balasan` (balasan pertama, otomatis lewat Zernio): wajib `{LINK}` dan kata "afiliasi", mis.
  `link-nya: {LINK} (link afiliasi, aku dapat komisi kalau kamu beli lewat sini)`. Konsol mengganti `{LINK}`.

## Selesai

`python3 tools/produksi.py <folder> teks` harus LOLOS. Perintah itu juga menulis `teks_post.txt` dari caption Shopee
(dipakai paket unggah). Catat di `cek_akhir.md` bila ada caption yang sengaja dibuat berbeda arah.
