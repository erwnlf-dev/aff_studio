# ADR-P05: `film.js` template berbasis snapshot, bukan sesi kreator per video

- **Status:** Digantikan ADR-P06 (20 Oktober 2026): prototipe template lolos QA teknis tapi dinilai pemilik di bawah standar Baru Tau. Dipertahankan sebagai catatan alasan.
- **Menyentuh:** stack, yaitu cara film dibuat (pipeline Baru Tau yang dicontek).
- **Dirujuk dari:** doc 12, K14, §5.1.

## Konteks

Di Baru Tau, satu sesi Claude Code headless (Opus 5.5, effort extra high) per episode mengerjakan semuanya:
- riset,
- naskah,
- VO,
- menulis `film.js` dari nol,
- pratinjau dan critic loop,
- partitur,
- render.

Cara ini cocok untuk satu explainer orisinal per hari. Video affiliate berbeda: volumenya 4–6 video per hari, strukturnya berulang (beat dari template), dan bahan visualnya foto produk.

Kalau setiap video tetap lewat sesi kreator penuh, ada tiga masalah:
1. **Biaya dan waktu** per video tinggi, dan worker render Slate dipakai bersama Baru Tau.
2. **Parameter tidak terkendali.** Model bebas menyimpang dari snapshot (ukuran caption, jumlah kata, gerak), sehingga `variant_id` tidak menjamin isi video dan eksperimen jadi bising.
3. **Compliance lebih sulit dibuktikan.** Teks di layar bisa muncul dari kode yang ditulis bebas, bukan dari data feed.

## Keputusan yang diusulkan

1. **Satu `film.js` template per template video** (`masalah_solusi`, `fitur_cepat`, `price_reveal`), disimpan di repo `aff_studio`. Template membaca dua file JSON yang dikirim sebagai `file_tambahan`:
   - `isi.json`: snapshot parameter, naskah per beat, timing kata dari `vo.json`, teks layar (hanya dari feed atau naskah yang disetujui), pilihan foto per beat,
   - `foto.json`: foto sebagai data URI base64.

   Semua angka gerak, caption, dan zona aman dibaca dari snapshot. Tidak ada angka di template.
2. **LLM dipanggil sekali per produk** dengan keluaran terstruktur: naskah per beat, 3 hook, pemilihan foto, teks post, reply pertama, alt text. Instruksi tetap memakai prompt caching. Model besar dipakai untuk naskah, model kecil untuk penilaian (B2, B3).
3. **Slate tetap dipakai apa adanya:** `buat_voiceover`, `pratinjau_film`, `render_film`, `qa_video`, partitur `slate_score`. Partitur dibuat dari template musik per mood, bukan ditulis per video.
4. **Template diuji seperti episode Baru Tau:** sebelum dipakai di produksi, setiap template harus lolos BASELINE yang relevan (frame 0, caption ≥ 64 px, diam ≤ 0,5 detik, kontras) dan `audit_film.py` dengan beberapa produk contoh.
5. **Sesi kreator penuh tetap tersedia** untuk format yang memang butuh tangan kreator: seri per niche (B4) dan edu-commerce (B16, ADR-P04).

## Alternatif yang ditolak

- **Sesi kreator per video dengan effort lebih rendah.** Masih menulis kode bebas per video, jadi masalah 2 dan 3 tetap ada.
- **Render di luar Slate (ffmpeg langsung).** Kehilangan QA, mix audio, dan alur job Slate yang sudah teruji. Membuat jalur kedua tidak sepadan.

## Konsekuensi

- Ada pekerjaan di depan: tiga template `film.js` + tes dengan produk contoh.
- Biaya per video turun ke kira-kira satu panggilan LLM + TTS + render.
- Snapshot benar-benar menentukan isi video, sehingga eksperimen bersih dan QA compliance (B3) bisa mencocokkan teks layar dengan `isi.json`.
- Kualitas bergantung pada template: kelemahan template berulang di semua video. Karena itu template ditinjau ulang setiap kali eksperimen dipromosikan.
