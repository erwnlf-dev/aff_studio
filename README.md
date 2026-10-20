# aff_studio

Pipeline video affiliate (foto produk → naskah → voiceover → video → posting), dibangun di atas pelajaran seri *Baru Tau.* dan Slate Studio.

Isi repo saat ini adalah bagian §1.7 (optimasi dan eksperimen). Dokumen Fase 1 lainnya (01–11) belum ada di repo.

| Path | Isi |
|---|---|
| `docs/12-optimization-and-experiments.md` | Kritik rencana, parameter, sistem eksperimen, ide, optimasi teknis |
| `docs/adr/ADR-P0*.md` | Usulan yang mengubah keputusan inti (status *Proposed*) |
| `config/video-params.yaml` | Registry semua parameter video (nilai, rentang, alasan, sumber, kunci compliance) dan eksperimen |
| `tools/cek_params.py` | Cek registry; snapshot parameter + `variant_id` per video |

```
pip install pyyaml
python3 tools/cek_params.py
python3 tools/cek_params.py snapshot --eksperimen EXP-02 --lengan B
python3 -m unittest discover -s tests
```
