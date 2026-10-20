# aff001 — Keset diatomite motif kucing

Video affiliate pertama yang disutradarai per produk (ADR-P06), sebagai contoh tingkat kualitas, seperti `examples/ep001` di Baru Tau. Tirukan tingkat kualitasnya, bukan isinya.

Berkas kerja lengkap ada di server: `/data/apps/affiliate-data/2026-10-19/produksi/55566811995/`. Folder itu berisi `final.mp4`, `vo.json`, `aset/foto.js`, cutout, dan pratinjau. Berkas-berkas itu tidak di-commit karena repo publik: `vo.json` memuat token link job, dan aset diturunkan dari foto penjual.

| File | Isi |
|---|---|
| `naskah.json` | Naskah per beat dengan sumber klaim (divalidasi `tools/siapkan_film.py`) |
| `kata_koreksi.json` | Onset kata yang dikoreksi ke jendela sunyi terukur di `vo.mp3` |
| `brief.md` | Blok arahan 8 baris berangka, tiga momen andalan, storyboard |
| `film.js` | Film v2: kit `midcentury` + kit affiliate `engine/aff.js` (cutout dengan blend), `aset/foto.js` dari `tools/cutout.py` |
| `score.py` | Partitur `slate_score` dan aturan mix |
| `ledger.md` | Critic loop 4 putaran + perbandingan BASELINE + 3 render + versi 2 (kit, blend) |
| `cek_akhir.md` | QA final, baca tanpa suara, peringatan tersisa |
| `teks_post.txt` | Caption unggahan |
