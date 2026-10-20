# ADR-P02: Gerbang approval dua tahap dan persetujuan batch

- **Status:** Proposed (20 Oktober 2026). Nomor final mengikuti urutan ADR Fase 1.
- **Menyentuh:** gerbang approval manusia.
- **Dirujuk dari:** doc 12, K13, §5.1.

## Konteks

Pipeline Baru Tau yang dicontek punya dua gerbang: `setuju N` (topik, sebelum VO dan render) dan `posting NNN` (sebelum tayang). Keduanya dirancang untuk satu video per hari:
- tahap 1 hanya menampilkan judul dan hook layar, bukan naskah,
- tahap 2 meminta pemilik menonton setiap video penuh di HP (1–2 menit per video).

Dengan 4–6 video affiliate per hari, menyalin pola ini apa adanya membuat pemilik jadi leher botol. Di sisi lain, kalau naskah baru dinilai setelah render, setiap penolakan sudah menghabiskan karakter ElevenLabs dan waktu render.

## Keputusan yang diusulkan

Manusia tetap memutuskan di dua titik. Tidak ada yang tayang tanpa persetujuan.

1. **Tahap naskah (sebelum TTS dan render).** Pemilik melihat satu kartu per video:
   - produk, harga feed dan umurnya,
   - hook terpilih + 1 cadangan,
   - naskah,
   - gambar frame 0 (still 540×960),
   - `variant_id` dan lengan eksperimen,
   - hasil QA compliance teks (B3).

   Pilihan: setuju, ganti hook, tolak. Bisa disetujui per batch (semua kartu yang lolos QA tanpa catatan).
2. **Tahap final (sebelum posting).** Video final dengan hasil QA (Slate dan B3), plus teks post, jadwal, dan akun. Bisa disetujui per batch per hari. Video yang punya peringatan QA tidak bisa ikut batch dan harus dibuka satu per satu.

## Alternatif yang ditolak

- **Approval hanya di akhir.** Boros TTS dan render untuk naskah yang ditolak.
- **Gerbang Baru Tau apa adanya (per item, tanpa batch).** Aman, tapi tidak bertahan di volume affiliate.
- **Auto-approve video yang lolos QA.** Ini menghapus gerbang manusia, jadi di luar mandat.

## Konsekuensi

- Modul affiliate di konsol web butuh dua antrean (naskah, final) dan aksi batch.
- TTS dan render hanya berjalan untuk naskah yang disetujui. Penghematannya sebanding dengan tingkat penolakan naskah.
- Snapshot parameter dikunci di tahap 1. "Ganti hook" menghasilkan snapshot dan `variant_id` baru.
