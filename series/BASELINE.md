# Baseline video affiliate

Setiap video harus **setara atau lebih baik** dari *Baru Tau.* #003 (`/data/apps/baru-tau-autopilot/episodes/003/final_sheet.jpg`) dalam hal craft. Sebelum `render`, letakkan contact sheet pratinjau video ini di samping contact sheet itu, lalu nilai setiap butir di bawah di `ledger.md` (✔ atau ✘ beserta angka). **Satu butir WAJIB yang gagal berarti belum boleh render.**

Butir 1–14 adalah BASELINE Baru Tau (`baru-tau-autopilot/series/BASELINE.md`) dengan angka yang sama, disesuaikan untuk produk. Butir 15–20 khusus affiliate. Butir bertanda **[QA server]** juga diukur gerbang QA Slate.

## WAJIB (dari Baru Tau)

1. **Frame 0 = thumbnail utuh:**
   - produk (cutout) terlihat,
   - teks hook ≥ 150 px dengan ≤ 5 kata yang memuat nama benda atau masalahnya,
   - yang aneh/menarik sudah **disorot**,
   - tidak dibuka dengan layar kosong.
2. **Hook terbaca dalam 1 detik tanpa suara.** Aksi pertama dalam 0,5 detik, dan hook selesai ≤ 15% durasi.
3. **Ada tangan/karakter yang berakting**, bukan sekadar benda yang bergerak. Antisipasi ≥ 4 frame, setiap aksi punya hasil yang terlihat, dan angkanya dari tabel "Gerak dalam angka" BIBLE Baru Tau.
4. **Setiap bagian punya warna dasar dan komposisi sendiri.** Tidak ada layout yang diulang (A3).
5. **Transisi dari konten.** Frame tepat setelah transisi sudah berisi subjek scene berikutnya.
6. **Subjek ≥ 640 px tinggi di setiap scene**, dan produk ≥ 640 px di scene produk, fitur, dan end card. Teks kunci ≥ 56 px.
7. **Tidak ada diam > 0,5 detik** **[QA server]**.
8. **Caption tertanam dengan gaya film:** ≥ 64 px, ≤ 7 kata, 1 kata disorot, di atas zona UI bawah (`zona_aman.*.bawah_px`), dan teksnya sama dengan yang diucapkan (angka sebagai digit).
9. **Momen puncak:** hening sungguhan ≥ 0,4 detik di dalam jeda VO, lalu produk atau demonstrasi mendarat tepat di katanya dengan hentakan 1 frame sesudahnya, tampil ≥ 1 detik.
10. **End card:**
    - produk cutout ≥ 640 px,
    - CTA ke tempat link (dibaca paling lambat),
    - label disclosure,
    - tanpa harga coret atau persen diskon.

    Loop ke frame 0 opsional (`META.loop = false` boleh untuk video affiliate, ditulis alasannya di brief).
11. **Musik:**
    - aransemen berbeda per bagian,
    - foley pada setiap aksi, dengan energi > 150 Hz,
    - hentakan 3–6 dB di atas musik **[QA server]**,
    - musik kontinu: di luar hening tidak pernah hilang, level antarbagian rata (0 lubang, rentang p10–p90 ≤ 12 dB) **[audit]**. Catatan pemilik 20 Okt: musik yang "hilang muncul" kurang enak ditonton.
    - LRA dicatat; peringatan "< 2,5 LU" diterima dan **tidak** dikejar dengan menaikturunkan volume musik.
12. **Klaim:** setiap kalimat naskah, teks layar, dan teks post bersumber dari data produk (`sumber` per beat lolos `siapkan_film.py`).
13. **Aman dan terbaca:** ≤ 3 kedipan per detik dan kontras teks ≥ 4,5:1 di setiap frame **[QA server]**.
14. **Audit numerik bersih:** kontrak render, CUES ±1 frame dari katanya, hentakan 1 frame setelah cue.

## WAJIB (khusus affiliate)

15. **Tidak ada teks penjual di layar (A2).** Setiap foto yang tampil sudah cutout atau crop tanpa teks; diperiksa per frame pratinjau, nantinya juga dengan OCR (TODO §6 butir 6).
16. **Tidak ada foto penjual utuh sebagai isi scene (A1)**, dan tidak ada tangan atau wajah model foto (A6).
17. **Demonstrasi fitur digambar.** Setiap scene fitur menunjukkan fiturnya bekerja dengan animasi gaya episode, bukan teks di atas foto.
18. **Disclosure** "Link afiliasi" terlihat di setiap frame, ≥ 32 px, kontras ≥ 4,5:1.
19. **Compliance data:**
    - tidak ada harga coret, persen diskon, atau "termurah",
    - angka bukti persis seperti data ("10RB+", "4,9"; tidak dibulatkan ke atas),
    - `compliance_note` dipatuhi dan dicatat di brief.
20. **Kategori diatur** (`compliance.kategori_diatur`): tanpa hook masalah/pain, tanpa before/after hasil (A7), dan klaim hanya dari `key_features` apa adanya.

## LEBIH BAIK DARI BASELINE (kejar minimal satu per video)

- **Demonstrasi yang bikin orang mengulang tonton**, misalnya tetes air yang hilang ke keset atau rambut yang tertiup kipas, ditempatkan sebelum 75% durasi.
- **Detail lokal Indonesia** di adegan masalah (KRL, kos-kosan, kamar mandi dengan gayung).
- **Ajakan uji langsung yang aman**: penonton bisa mengecek sendiri sesuatu yang benar dari data ("lihat ulasannya, 264 ribu lebih").

## Contoh yang ditolak

Uji 20 Oktober, Hanasui, template `kartu`, job `2026-10-20-dfe4ae`. Video ini lolos QA teknis tapi gagal butir 3, 4, 5, 9, 11 (tanpa musik), 15, 16, dan 17. Dinilai **jelek** oleh pemilik. Bentuk ini jangan diulang.
