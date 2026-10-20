# Cek akhir — mini kipas turbo genggam (41671303438)

**Render final:** job `2026-10-20-bd860a`, render ke-3, **QA Slate lolos** (`masalah` kosong).
- 19,17 detik, 1080×1920, 24 fps (460 frame), −14,0 LUFS, puncak −2,0 dBFS.
- Tanpa frame beku atau frame hitam.
- Kedip maksimal 3 transisi/detik (di potongan 2,75 s; batas 3).
- Kontras teks 6/6 pasangan lolos (4,73–14,15 : 1).
- Hening sungguhan 5,27–5,77 (0,50 s, puncak −75,5 dBFS), lalu hentakan kipas di frame 141.
- Loop ke frame 0: selisih 0,89/255 (batas 2).
- File: `final.mp4`. Render 1 dan 2 disimpan sebagai `final_r1.mp4` dan `final_r2.mp4`.
- Hentakan: semua 16 hit 13–99 dB di atas bed pada pitanya; 9 dari 14 cue yang terukur sinkron +1,0 frame (motor +1,5).

**Peringatan QA yang tersisa (tidak menggagalkan):**
- **LRA 2,2 LU (target BASELINE 11: ≥ 2,5).**
  - Naik dari 1,8 (r1) → 2,0 (r2) → 2,2 (r3) setelah musik bagian masalah dan fitur ② ditipiskan (×0,1–0,2), produk/CTA dipenuhkan (×2,3), dan musik dibiarkan mengembang di celah VO 8,52 · 11,38 · 14,20.
  - Batasnya struktural, sama seperti aff001 (1,5): 19 detik narasi dengan jeda VO 0,34–0,6 s, sementara loudness jangka pendek (jendela 3 s) didominasi suara.
  - Untuk video berikutnya: `vo.jeda_bagian_detik` 0,5 → 0,7, ditambah satu jeda musik ≥ 1 s di tengah (misalnya sebelum bukti).
- **Sinkron, empat cue terukur +2,6 sampai +3,5 frame:**

  | Cue | Selisih | Terjadi di |
  |---|---|---|
  | `rpm` | +124 ms | "RPM." |
  | `enam` | +148 ms | "Enam" |
  | `layar` | +110 ms | "layar." |
  | `link` | +140 ms | "link" |

  - Keempatnya jatuh di dalam kata VO. Untuk `rpm`, `enam`, dan `link` QA memakai metode *onset* (korelasi gagal), jadi yang tertangkap adalah konsonan narator ("p" di "er-pe-em", "n", "k").
  - Partitur menaruh setiap hit tepat +1,0 frame (audit lokal 33/0).
  - `enam` baru muncul di r3 karena musik di celah 11,45 berada tepat sebelum hentakan.
  - `segel` −37 ms dan `warna` −33 ms berarti bunyi 0,1–0,2 frame setelah gambar (target +1). Itu masih di dalam ±1 frame dari gambar dan tidak terasa di telinga.
  - Baru Tau #003 dan aff001 juga berakhir dengan peringatan sinkron serupa.
- **Gagang kaca pembesar** di fitur ① dan ② keluar sampai x ±1.000 (zona aman kanan 940). Bingkai, isi, dan semua teks ada di dalam 940; gagangnya kayu tanpa teks.

**Baca tanpa suara (`final_sheet.jpg`, 20 frame dari final.mp4):**

| Bagian | Yang terbaca dari gambar |
|---|---|
| Hook (0–2,75) | Penumpang di jendela KRL, kipas kecil di tangan dilingkari merah, "Kipas kecil, angin kencang?". Poni tertiup lalu wajah lega. |
| Masalah (2,75–5,7) | Gerbong padat: pegangan gantung, penumpang mendesak, June berkeringat mengipas dengan tangan, "Gerah banget?" |
| Produk (5,7–8,9) | Kipas keluar dari tote bag, jempol menyalakan, pita di tali tas berkibar, "Kipas turbo" |
| Fitur ① (8,9–11,7) | Di depan pintu KRL: tisu di depan kipas terangkat sampai rata, kaca pembesar menunjukkan rotor, "23.000 RPM" + "angin 20 m/s" (label ilustrasi) |
| Fitur ② (11,7–14,5) | Kipas close-up, jempol menekan, layar di kaca pembesar berganti 1→6, "6 level" |
| Bukti (14,5–16,75) | Papan info stasiun: tangan mengecap "10RB+ terjual", segel "★ 4,7 · 26rb+ ulasan" |
| CTA (16,75–19,18) | Kipas + varian abu + kipas kertas 10 keping warna, "Cek warna di link", "10 warna", tangan menunjuk ke bawah |

Kesimpulan: cerita utuh tanpa suara. Disclosure "Link afiliasi" terlihat di setiap frame. Tidak ada harga, harga coret, persen diskon, atau teks penjual.

**Compliance:** angka layar persis dari `data_layar.json` ("10RB+", "4,7", "26rb+", 10 warna; harga `null` tidak tampil). `compliance_note` dipatuhi: tidak ada diskon atau harga coret, dan rating 4,7 hanya tampil di segel, tidak diucapkan atau ditonjolkan. Teks post memakai klaim yang sama dengan video (23.000 RPM, 6 level, layar, 10 warna).

**PERLU DICEK telinga pemilik:**
- Pengucapan "RPM" (suara "Erwin" berlabel bahasa Inggris; EXP-04 belum dipilih).
- "Desak-desakan".
- "Nah…" dibaca dengan jeda 0,34 s sebelum "ini dia". Hening yang dipakai ada di jeda sebelum "Nah…".
