# Cek akhir — keset (55566811995)

**Render final:** job `2026-10-20-9fed21`, render ke-3, **QA Slate lolos**.
- 18,77 detik, 1080×1920, 24 fps, −14,0 LUFS, TP −1,9 dBFS.
- Tanpa frame beku, frame hitam, atau kedip berbahaya.
- Hening sungguhan 4,58–5,10 (0,52 s, puncak −77 dBFS).
- Loop ke frame 0: selisih 0,85/255 (batas 2).
- File: `final.mp4` (render 1 dan 2 disimpan sebagai `final_r1.mp4` dan `final_r2.mp4`).

**Peringatan QA yang tersisa (tidak menggagalkan):**
- **LRA 1,5 LU (target BASELINE 11: ≥ 2,5).**
  - Render 1: 1,2 → render 3: 1,5, setelah musik bagian masalah dan anti-slip ditipiskan (×0,3–0,38) dan bagian produk/CTA dipenuhkan (×1,7).
  - Batasnya struktural: 18 detik dengan narasi hampir tanpa jeda (jeda VO 0,4–0,6 s). Baru Tau #003 mencapai 2,5 dengan 44 detik dan jeda 0,7 s.
  - Video berikutnya: `vo.jeda_bagian_detik` 0,5 → 0,7, ditambah satu jeda musik di tengah.
- **Sinkron `kaki_basah` dan `balik` terukur +2,5 frame** (cue lain +1,0 frame).
  - Keduanya jatuh di tengah kata VO ("basah", "Alasnya"), sehingga korelasi QA menangkap konsonan narator. `balik` lolos di render 2 dan gagal di render 3 dengan partitur yang sama di titik itu.
  - Baru Tau #003 juga berakhir dengan peringatan sinkron.
- **Satu pop kecil** (tetes lepas, 1,15 s) −2,1 dB terhadap sekitarnya; bukan hentakan cue.

**Baca tanpa suara (`final_sheet.jpg`, 20 frame dari final.mp4):**

| Bagian | Yang terbaca dari gambar |
|---|---|
| Hook | keset + gayung + "Keset ini nyerap air?", lalu tetes hilang ke keset |
| Masalah | kaki menapak di genangan lalu tergelincir, "Lantai licin?" |
| Produk | keset jatuh, genangan hilang, "Keset diatomite", cincin "motif kucing" |
| Fitur ① | gayung meneteskan air ke keset, air hilang, segel centang, "Cepat kering" (+ label ilustrasi) |
| Fitur ② | keset membalik, sisi bawah berpola, tangan mendorong dan keset tidak geser, "Anti-slip" |
| Bukti | cap "10RB+ terjual / bulan" dan segel "4,89 · 9,5rb+ ulasan" |
| CTA | keset + 3 motif lain, "Cek motif di link", tangan menunjuk ke bawah |

Kesimpulan: cerita utuh tanpa suara, dan disclosure terlihat di setiap frame.

**PERLU DICEK telinga pemilik:**
- pengucapan "diatomite" dan "anti-slip",
- suara "Erwin" berlabel bahasa Inggris (EXP-04 belum dipilih).
