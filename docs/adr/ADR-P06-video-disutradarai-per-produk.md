# ADR-P06: Video disutradarai per produk (metode Baru Tau), bukan template

- **Status:** Proposed (20 Oktober 2026). Menggantikan ADR-P05. Nomor final mengikuti urutan ADR proyek.
- **Menyentuh:** stack (cara film dibuat), biaya dan kadens produksi.
- **Dirujuk dari:** `series/BIBLE.md`, `series/BASELINE.md`, `docs/13-acuan-kualitas-video.md`.

## Konteks

ADR-P05 mengusulkan template `film.js` yang diisi data, supaya murah dan parameternya terkendali. Prototipenya (`templates/kartu`) dirender penuh lewat Slate pada 20 Oktober (Hanasui, job `2026-10-20-dfe4ae`). Hasilnya **lolos semua QA teknis**, tapi pemilik menilainya **jelek**: di bawah standar output *Baru Tau.*

Analisisnya ada di BIBLE "Pelajaran dari uji 20 Oktober". Template yang diisi data menghasilkan slideshow, dan kualitas Baru Tau datang dari hal-hal yang tidak bisa diisi data:
- adegan yang digambar per topik,
- tangan/karakter yang berakting di kata yang tepat,
- warna dan komposisi per bagian,
- transisi dari konten,
- partitur dan foley per aksi,
- critic loop 2–5 putaran dengan catatan bernomor frame (ledger #003: 5 putaran).

## Keputusan yang diusulkan

1. **Setiap video dibuat seperti satu episode Baru Tau:** sesi kreator Claude Code (Opus, effort tinggi) per produk, mengikuti `series/BIBLE.md` dan `series/BASELINE.md` aff_studio. Urutannya:
   - naskah bersumber,
   - brief berangka + storyboard,
   - `film.js` sendiri,
   - audit + pratinjau berulang,
   - partitur,
   - perbandingan baseline,
   - render + QA.
2. **Yang distandarkan hanya bagian berulang yang menyangkut compliance dan identitas**, dalam satu kit kecil `kits/affiliate/aff.js`:
   - label disclosure,
   - slab caption dari timing kata,
   - menggambar cutout produk dengan bayangan kontak,
   - cap bukti dari data,
   - end card.

   Isi adegan selalu digambar per video, memakai kit gaya (mis. `midcentury`: tangan, tinta, bentuk, `paperFinish`).
3. **Cutout produk** disiapkan otomatis sebelum sesi kreator: penghapus latar di CPU, lalu dicek mata di kartu naskah (tahap 1 ADR-P02).
4. **Parameter registry tetap berlaku sebagai batas, bukan isi.** Naskah, durasi, tempo, caption, zona aman, compliance, dan posting tetap dari snapshot, dan kreator mencatat `variant_id` di brief. Eksperimen visual (EXP-05, -07, -10) ditinjau ulang: banyak yang tidak relevan lagi tanpa template.
5. **Template `kartu` dipertahankan hanya untuk pratinjau tahap naskah** (cek timing dan urutan sebelum VO), tidak untuk video yang diunggah.

## Konsekuensi

**Biaya dan kadens.** Satu sesi kreator per video. Episode Baru Tau memakan waktu dan token jauh lebih besar dari template (5 putaran pratinjau di #003). Video affiliate lebih pendek (20–30 detik vs 35–45 detik), tapi tetap realistisnya **1–3 video per hari**, bukan 4–6. Akibatnya:
- angka volume di doc 12 (§4.4, sampel eksperimen) harus dihitung ulang,
- uji A/B menjadi lebih lambat; ini memperkuat K2 (uji hanya parameter berdampak besar).

**Lebih banyak yang dipakai ulang dari Baru Tau:**
- alur `CLAUDE.md` Mode PRODUKSI,
- `audit_film.py`,
- `slate_score.py`,
- kit `midcentury`,
- pola ledger.

aff_studio perlu salinan yang disesuaikan, bukan menulis dari nol.

**Snapshot tidak lagi menjamin isi visual secara penuh.** Kreator bebas menggambar, jadi kepatuhan dijaga dengan:
- validasi naskah (`siapkan_film.py`),
- kit compliance (disclosure dan cap bukti dari data),
- butir BASELINE 15–20,
- QA OCR.

## Alternatif yang ditolak

- **Memperbaiki template saja** (latar mesh, grain, transisi, musik). Sudah ditimbang: template yang lebih rapi tetap slideshow tanpa adegan dan tanpa akting (gagal BASELINE 3, 5, 17).
- **Template per kategori dengan adegan siap pakai** (kamar mandi untuk keset, meja rias untuk kosmetik). Bisa jadi langkah kedua, setelah beberapa video yang disutradarai menunjukkan adegan mana yang benar-benar berulang. Membuatnya sekarang berarti menebak.
