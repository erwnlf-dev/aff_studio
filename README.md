# aff_studio

Pipeline video affiliate (foto produk → naskah → voiceover → video → posting), dibangun di atas pelajaran seri *Baru Tau.* dan Slate Studio.

Repo ini mencontek pipeline Baru Tau di server ini (`/data/apps/baru-tau-autopilot` + Slate Studio): VO, render `film.js`, QA, dan posting tetap lewat Slate. Isi saat ini: bagian optimasi dan eksperimen.

| Path | Isi |
|---|---|
| `docs/TODO.md` | Status, keputusan pemilik, dan urutan kerja berikutnya |
| `series/BIBLE.md`, `series/BASELINE.md` | Standar kreatif dan batas bawah kualitas video (minimal setara *Baru Tau.*) |
| `docs/13-acuan-kualitas-video.md` | Sumber acuan kualitas: Baru Tau, lemo-opuscar, skill motion graphics, panduan platform, data |
| `docs/12-optimization-and-experiments.md` | Kritik rencana, parameter, sistem eksperimen, ide, optimasi teknis |
| `docs/adr/ADR-P0*.md` | Usulan yang mengubah keputusan inti (P01–P05, status *Proposed*) |
| `config/video-params.yaml` | Registry semua parameter video (nilai, rentang, alasan, sumber, kunci compliance) dan eksperimen |
| `tools/cek_params.py` | Cek registry; snapshot parameter + `variant_id` per video |
| `tools/paket.py` | Baca dan validasi paket data produk dari sesi Claude in Chrome |
| `tools/siapkan_film.py` | Naskah + produk + snapshot → `isi.json`, `foto.json`, `naskah.txt`, `scenes.json` |
| `tools/pratinjau.py` | Pratinjau lokal (contact sheet / frame) dengan Chromium headless, tanpa Slate |
| `tools/slate.py` | Slate Studio per folder video: kuota, VO, render, tunggu, QA, pratinjau (template atau `--film` sendiri) |
| `tools/cutout.py` | Cutout produk dari foto penjual (rembg, `.venv`), dikemas ke `aset/foto.js` |
| `tools/audit_film.py`, `tools/slate_score.py` | Audit numerik film dan penulis partitur (dari Baru Tau) |
| `examples/aff001-keset/` | Video pertama yang disutradarai: naskah, brief, film, partitur, ledger, cek akhir |
| `templates/kartu/film.js` | Template film prototipe (ADR-P05, digantikan ADR-P06): hanya untuk pratinjau tahap naskah |

Alur saat ini (paket data di luar repo, mis. `/data/apps/affiliate-data/<tanggal>/`):

```
python3 tools/paket.py cek /data/apps/affiliate-data/2026-10-19
python3 tools/siapkan_film.py --paket /data/apps/affiliate-data/2026-10-19 \
    --naskah /data/apps/affiliate-data/2026-10-19/naskah/<id>.json --keluar /tmp/film/<id>
python3 tools/pratinjau.py /tmp/film/<id> --keluar /tmp/film/<id>/sheet.jpg
```

```
pip install pyyaml pillow
python3 -m venv --system-site-packages .venv && .venv/bin/pip install "rembg[cpu]"   # untuk tools/cutout.py
python3 tools/cek_params.py
python3 tools/cek_params.py snapshot --eksperimen EXP-02 --lengan B
python3 -m unittest discover -s tests
```
