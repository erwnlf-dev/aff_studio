"""{{NAMA}} — partitur. Waktu dari kata_koreksi.json (vo.json job {{JOB}}). Pola: examples/aff001-keset/score.py.

Palet gaya (midcentury: vibrafon, bass petik digandakan oktaf/marimba, brush, jentikan, celesta). Aransemen per bagian.
Hentakan di atas gambar: put(<cue> + 1/24, ..., cue=<id>), dibuka bunyi ber-attack tajam (click/clack/stamp/pop pendek),
dan sebaiknya di celah kata VO (di tengah kata, korelasi QA menangkap konsonan narator). Swish/paper/riser = bunyi
antisipasi yang mulai 1–3 frame sebelum benturan. Hening hanya di jendela sunyi terukur (tools/sunyi.py "calon hening").
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, '/data/apps/aff_studio/tools')
from slate_score import Recorder, hz

HERE = Path(__file__).resolve().parent
R = Recorder()
DUR = 0.0
FR = 1 / 24
HEN = []
CUE = {}                                   # id: frame (sama dengan CUE_LIST film.js)
CUE = {k: v / 24 for k, v in CUE.items()}

# ... musik per bagian, hit(cue, [...]) dan fol(t, ...), level per bagian, aturan mix: salin dari examples/aff001-keset/score.py

json.dump(R.score(DUR, HEN, room=0.006, lufs=-16), open(HERE / 'score.json', 'w'))
