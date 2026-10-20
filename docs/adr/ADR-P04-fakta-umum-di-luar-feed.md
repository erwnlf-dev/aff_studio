# ADR-P04: Fakta umum terverifikasi di luar feed untuk konten edu-commerce

- **Status:** Proposed (20 Oktober 2026). Nomor final mengikuti urutan ADR Fase 1.
- **Menyentuh:** aturan compliance "tidak ada klaim di luar data feed".
- **Dirujuk dari:** doc 12, B16.

## Konteks

Kekuatan yang sudah dibangun di Baru Tau adalah explainer "kenapa benda ini begitu" dengan fakta yang dikunci dua sumber (`facts.md`). Format ini berpotensi lebih orisinal dan lebih ditonton daripada video produk biasa (misalnya "kenapa botol minum ada garis ukurnya", lalu produknya). Masalahnya, fakta umum tentang benda bukan data feed.

## Keputusan yang diusulkan

Izinkan satu kelas pernyataan tambahan, **hanya** untuk template edu-commerce (B16), dengan batas berikut:

1. **Fakta umum** tentang jenis benda, sejarah, atau cara kerja boleh dipakai. Setiap kalimat tercatat di `facts.md` per video dengan ≥ 2 sumber dari 2 domain berbeda dan kutipan persis (aturan Baru Tau).
2. **Klaim tentang produk spesifik** (khasiat, daya tahan, bahan, "lebih baik dari") tetap **hanya** dari feed. Fakta umum tidak boleh dijembatani menjadi klaim produk. Contoh terlarang: "garis ukur membantu minum 2 liter → botol ini bikin kamu sehat".
3. Kategori dengan `category_regulated = true` (ADR-P01) tidak boleh memakai template ini.
4. QA (B3) menandai setiap kalimat naskah sebagai `feed`, `fakta_umum` (dengan id di `facts.md`), atau `ajakan`. Kalimat tanpa tanda ditolak.
5. Pemilik melihat `facts.md` di tahap naskah (ADR-P02).

## Alternatif yang ditolak

- **Memperluas feed dengan "fakta produk" dari LLM.** Mengarang dengan nama lain.
- **Tidak membuat edu-commerce sama sekali.** Ini tetap default sampai ADR ini diterima.

## Konsekuensi

- Biaya per video naik (web search, verifikasi), dan template ini butuh waktu produksi lebih lama.
- Risiko compliance terbesar ada di jembatan fakta umum → produk. Karena itu aturan 2 dan 4 dicek mesin dan manusia.
