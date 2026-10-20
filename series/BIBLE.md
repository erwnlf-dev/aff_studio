# Bible video affiliate

Standar kreatif video produk aff_studio. **Batas bawahnya adalah hasil seri *Baru Tau.***: film animasi yang digambar dengan kode, karakter/tangan yang berakting, partitur musik per bagian, foley, dan critic loop yang terukur. Contoh yang harus ditandingi: `/data/apps/baru-tau-autopilot/episodes/003/final_sheet.jpg` dan `examples/ep001/contact_sheet.jpg`.

Aturan Baru Tau di `baru-tau-autopilot/series/BIBLE.md` (Narasi, Gerak dalam angka, Suara, TERLARANG) **berlaku penuh** kecuali ditimpa di bawah. Dokumen ini hanya menulis yang khusus untuk video produk. Sumber dan alasannya ada di `docs/13-acuan-kualitas-video.md`.

## Pelajaran dari uji 20 Oktober (yang ditolak)

Video Hanasui dari template `kartu` lolos semua QA teknis Slate, tapi pemilik menilainya **jelek**. Penyebabnya bukan hal teknis, melainkan bentuknya:
- **Slideshow foto penjual.** Isinya foto marketplace di dalam kartu, dengan zoom pelan dan latar polos. Tidak ada adegan, tidak ada aksi, tidak ada cerita yang digambar.
- **Teks marketing penjual tampil di layar.** Contohnya "INSTANT GLOSS", "Dermatologically tested", dan "3X hydrating". Teks itu membuat video berantakan, dan sebagian klaimnya tidak ada di data.
- **Tidak ada karakter, tangan, atau benda yang berakting.** Tidak ada antisipasi, squash, pegas, maupun hasil aksi yang terlihat.
- **Satu komposisi untuk semua beat**, yaitu kartu di tengah. Padahal Baru Tau mewajibkan warna dan komposisi berbeda per bagian.
- **Sunyi**, tanpa musik maupun foley.
- **Dibuat oleh template, bukan disutradarai.** Tidak ada brief berangka, storyboard, pratinjau berulang, atau ledger.

Ini sekarang masuk TERLARANG (A1–A6 di bawah).

## Identitas

- **Format:** 1080×1920, 24 fps (seperti Baru Tau; animasi terbatas), **15–25 detik, bawaan 20** (doc 13 §4: video TikTok Shop viral tanpa wajah median 13,5 detik; Shopee Video 12–20 detik). Satu produk per video.
- **Penonton:** pembeli Shopee/TikTok Indonesia, Gen Z dan milenial. Video berputar tanpa suara di feed, jadi cerita harus terbaca tanpa suara.
- **Janji ke penonton:** satu masalah sehari-hari yang dikenal, satu produk yang menjawabnya, dan buktinya dari data. Tidak ada janji di luar data.
- **Penutup tetap:** end card dengan produk (cutout), CTA ke tempat link, dan label disclosure. Pilihan berikutnya: identitas seri per niche (doc 12 ide B4).

## Cara produksi (sama dengan Baru Tau)

Setiap video **disutradarai**, bukan diisi ke template. Satu sesi kreator per video menjalankan urutan berikut:

| Langkah | Isi |
|---|---|
| Naskah | Ditulis dari data produk; setiap klaim punya sumber `fitur:N`, `rating`, dan seterusnya (`tools/siapkan_film.py` memvalidasi) |
| Gaya | Dipilih dari library dengan alasan |
| Brief | Blok arahan 8 baris berangka + storyboard, persis format Baru Tau (CLAUDE.md langkah 6) |
| Film | `film.js` sendiri per video, memakai kit gaya dan kit affiliate (§Kit) |
| Critic loop | `audit_film.py` + minimal **2 putaran** pratinjau 16–24 momen; per putaran perbaiki 1–2 masalah teratas, dicatat di `ledger.md` dengan nomor frame dan angka |
| Partitur | `score.json` per bagian + foley + hening |
| Perbandingan baseline | Contact sheet video ini di samping contact sheet Baru Tau |
| Render | Lewat Slate + QA, lalu `contact_sheet` final + cek tanpa suara |

Template `kartu` hanya boleh dipakai untuk **pratinjau tahap naskah** (cek urutan dan timing), tidak untuk video yang diunggah. Keputusannya ada di ADR-P06.

## Produk sebagai hero

- **Produk asli = benda hero.** Diambil dari foto penjual sebagai **cutout** (latar dihapus, tanpa teks marketing), lalu ditaruh di dunia yang digambar dalam gaya episode, dengan bayangan kontak dan garis tinta/registrasi gaya itu supaya menyatu. Foto penjual utuh tidak pernah tampil sebagai latar atau kartu.
- **Cutout disiapkan sebelum storyboard** (`foto/cutout/<id>_NN.png`), dan setiap cutout dicek mata:
  - tepi bersih,
  - tidak ada sisa teks atau badge,
  - tidak ada bagian produk yang terpotong.

  Foto yang tidak bisa dibersihkan tidak dipakai.
- **Menyatu dengan dunia gambar, wujud tetap asli** (kit `produk()`, bawaan):
  - garis tinta stiker 4,5 px,
  - bayangan lembut dua lapis: kontak rapat blur 7 px dan bayangan jatuh blur 26 px ke kanan bawah, searah cahaya kiri atas; menjauh dan memudar saat benda di udara (`tinggi`),
  - pencahayaan ulang 2.5D: sorot hangat kiri atas, bayangan kanan bawah,
  - warna ambien adegan meresap tipis (`cahaya` = warna latar, tint ≤ 0,15, kunci `visual.produk_tint_maks`),
  - tekstur kertas `paperFinish` di atas semuanya,
  - pengikat terkuat: benda yang digambar **menutupi** produk (tangan memegang, air di atasnya).

  **End card dan close-up memakai warna asli** (`asli: true`). Bentuk produk tidak didistorsi selain squash mendarat ≤ 12%. Perbandingan sebelum/sesudah: `examples/aff001-keset` (render v2).
- **Detail fitur** (tekstur, alas anti-slip, layar LED) memakai crop foto yang **tidak memuat teks**, dibingkai sebagai call-out gaya episode (lingkaran/kaca pembesar bertinta), bukan kartu.
- **Hanya satu produk asli per frame.** Produk lain, merek lain, atau logo pihak lain tidak tampil. Kemasan produk dengan mereknya sendiri boleh, karena itu produk yang dipromosikan.
- **Ukuran:** produk ≥ 640 px tinggi di scene produk, fitur, dan end card (BASELINE 6). Di scene masalah, produk boleh absen atau kecil.

## Struktur cerita (15–25 detik, 5–7 scene)

Data (doc 13 §4): produk terlihat di median 0,07 detik, dan manfaat/bukti di median 2,73 detik. Penonton Indonesia lebih percaya demo daripada iklan. Jadi produk tampil di frame 0, demonstrasi pertama sebelum detik 3, dan masalah diceritakan singkat sesudahnya.

| Bagian | Detik (bawaan 20 s) | Isi | Visual |
|---|---|---|---|
| Hook | 0–2,5 | Produk + pertanyaan/kejanggalan; demonstrasi terkuat sudah mulai sebelum detik 3 | Frame 0 = thumbnail utuh: produk cutout + teks hook ≤ 5 kata + yang menarik disorot; aksi pertama ≤ 0,5 detik |
| Masalah | 2,5–5 | Situasi yang dikenal (lantai basah, bibir kering, gerah di KRL) | Adegan digambar dengan tangan/karakter yang berakting; detail lokal |
| Fitur ① | 5–10 | Fitur utama dari `key_features`, didemonstrasikan | Demonstrasi **digambar**: tetes air mengecil masuk ke keset, garis angin + rambut tertiup, olesan warna pada bibir kartun |
| Fitur ② | 10–14 | Fitur kedua | Komposisi dan warna berbeda dari ① |
| Bukti | 14–17 | Rating/terjual persis dari data | Dicap tangan (cap karet "★ 4,9", "10RB+ terjual/bulan") seperti cap Baru Tau |
| CTA | 17–20 | Ajakan ke tempat link | End card: produk cutout, CTA, disclosure; dibaca paling lambat |

**Hening dan payoff.** Satu hening sungguhan (≥ 0,4 detik, di dalam jeda VO) tepat sebelum produk masuk atau sebelum demonstrasi fitur terkuat; bunyi pertama sesudahnya adalah hentakan produk. Momen yang paling layak ditonton ulang ditempatkan sebelum 75% durasi.

## Visual

- **Gaya dipilih per produk** dari library lemo-opuscar, dengan alasan satu baris di brief. Utamakan gaya 2D yang sudah terbukti di Slate (`midcentury-toon`). Calon lain untuk produk: `paper-popup`, `crayon-book`, `pictogram-motion`, `swiss-motion`, `teardown` (cara kerja benda). Gaya yang memakai produk fiktif atau WebGL berat (`glass-product`) tidak dipakai, karena produknya nyata dan server tanpa GPU.
- **Warna dan komposisi berbeda per bagian** (BASELINE 4): masalah, produk, setiap fitur, dan bukti punya warna dasar dan tata letak sendiri. Satu benda atau bentuk membawa film dari bagian ke bagian (biasanya produk itu sendiri).
- **Latar = tempat dari cerita** (kamar mandi, meja rias, gerbong), digambar dengan palet gaya. Tidak ada latar polos, gradien polos, atau blob mesh.
- **Transisi dibuat dari konten** (BASELINE 5): wipe blok warna, iris lewat produk, atau tangan yang membawa produk ke scene berikutnya. Bawaannya potong keras.
- **Caption** memakai slab gaya episode (kertas bertinta untuk midcentury): ≥ 64 px, ≤ 7 kata, 1 kata disorot, di atas zona UI bawah. Angka sebagai digit di caption, sebagai huruf di VO.
- **Teks kunci** ≤ 3 kata per scene (≥ 56 px), bisa dibaca tanpa caption.
- **Label disclosure** "Link afiliasi" tampil di setiap frame (kunci compliance), digambar dengan gaya episode (tag kecil bertinta), tetap terbaca (≥ 32 px, kontras ≥ 4,5:1).
- **Saat unggah ke Shopee Video:**
  - toggle **"Konten Dihasilkan AI" wajib**, karena narasi memakai suara AI (doc 14 §1),
  - produk ditautkan lewat Tambah Produk,
  - tanpa nama/logo Shopee di video,
  - aksi dan teks penting tetap di atas y = 1.300 sampai zona keranjang (kiri bawah) diukur.

## TERLARANG khusus affiliate (tambahan daftar Baru Tau)

- **A1.** Slideshow foto penjual: foto utuh di kartu/layar penuh sebagai isi utama scene.
- **A2.** Teks, badge, stiker, atau angka marketing penjual yang tercetak di foto ("INSTANT GLOSS", "10.7 Hrs", "100 level", testimoni, harga). Pakai cutout atau crop tanpa teks.
- **A3.** Satu komposisi diulang di semua beat (kartu di tengah + teks atas + caption bawah).
- **A4.** Video tanpa musik dan foley.
- **A5.** Harga coret, persen diskon, "termurah", "terlaris" (kecuali angka terjual dari data), atau klaim apa pun di luar `key_features`/angka feed (kunci compliance).
- **A6.** Tangan, wajah, atau tubuh orang **foto** (model penjual) sebagai aktor. Aktor selalu digambar dalam gaya episode.
- **A7.** Before/after yang menyiratkan hasil (kulit, bibir, berat badan) untuk kategori diatur (`compliance.kategori_diatur`).

## Suara

Seperti Baru Tau:
- partitur `slate_score.py` dengan aransemen per bagian sesuai palet gaya,
- dua hening di dalam jeda VO,
- foley untuk setiap aksi yang terlihat, dengan energi di atas 150 Hz,
- hentakan 1 frame setelah gambarnya, 3–6 dB di atas musik.

Khusus affiliate:
- **Musik adalah alas yang kontinu** (catatan pemilik 20 Okt): tidak hilang-muncul di luar hening, level antarbagian rata (±3 dB), dinamika lewat aransemen. Di sekitar hentakan musik diredam 3 dB, tidak dihapus. Ini berbeda dari Baru Tau, yang memakai kontras level antarbagian untuk LRA.
- **Musik lebih rapat ritmenya** (100–120 BPM) karena video lebih pendek. Potongan scene jatuh di ketukan kalau memungkinkan (`frame per ketukan = 24 × 60 / BPM`).
- **Tanpa lagu berlisensi atau suara tren** yang dibakar ke file (kunci `musik.sumber`).
- **Suara VO:** native Indonesia (EXP-04). Sampai dipilih, pakai suara yang sama dengan Baru Tau, dan catat hal itu di brief.
