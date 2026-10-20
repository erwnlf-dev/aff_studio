"""{{NAMA}} — partitur. Waktu dari kata_koreksi.json (vo.json job {{JOB}}). Pola aransemen dan foley:
examples/aff001-keset/score.py; level dan aturan mix: blok di file ini (aturan musik 20 Okt), BUKAN LEVEL ×0,1–2,3 dan
penghapusan musik 'crowded' di contoh lama.

Palet gaya (midcentury: vibrafon, bass petik digandakan oktaf/marimba, brush, jentikan, celesta). Aransemen per bagian.
Hentakan di atas gambar: put(<cue> + 1/24, ..., cue=<id>), dibuka bunyi ber-attack tajam (click/clack/stamp/pop pendek),
dan sebaiknya di celah kata VO (di tengah kata, korelasi QA menangkap konsonan narator). Swish/paper/riser = bunyi
antisipasi yang mulai 1–3 frame sebelum benturan. Hening hanya di jendela sunyi terukur (tools/sunyi.py "calon hening").

Musik = alas yang KONTINU (catatan pemilik 20 Okt: "musik backsound hilang muncul ... kurang enak ditonton"):
- di luar hening musik tidak pernah hilang: alas tipis per birama di bawah aransemen bagian (blok ALAS),
- dinamika antarbagian dari aransemen (instrumen, kerapatan), bukan volume: faktor LEVEL 0,7–1,4, tetangga beda ≤ 3 dB,
- di sekitar hentakan musik diredam 3 dB (×0,7), tidak dihapus,
- audit_film memeriksanya: 0 lubang (jendela 0,5 s > 12 dB di bawah median) dan rentang level p10–p90 ≤ 12 dB.
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
BPM = 112
BEAT, T0 = 60 / BPM, 0.05
CUE = {}                                   # id: frame (sama dengan CUE_LIST film.js)
CUE = {k: v / 24 for k, v in CUE.items()}

MUS, HIT = [], []
mus = lambda t, d, g=1.0, p=0.0: MUS.append([t, d, g, p, None])
def hit(cue, parts):
    t = CUE[cue] + FR
    for i, (d, g, p) in enumerate(parts):
        HIT.append([t, d, g, p, cue if i == 0 else None])
def fol(t, d, g=1.0, p=0.0):
    HIT.append([t, d, g, p, None])

CH = {'F6': ['F3', 'A3', 'C4', 'D4'], 'Gm7': ['G3', 'Bb3', 'D4', 'F4'], 'C7': ['C3', 'E3', 'G3', 'Bb3'], 'Am7': ['A2', 'C3', 'E3', 'G3'],
      'Dm7': ['D3', 'F3', 'A3', 'C4'], 'Bbmaj7': ['Bb2', 'D3', 'F3', 'A3'], 'G6': ['G3', 'B3', 'D4', 'E4'], 'Cmaj7': ['C3', 'E3', 'G3', 'B3']}
beats = lambda a, z, b=BEAT: [T0 + k * b for k in range(0, int(DUR / b) + 4) if a <= T0 + k * b < z]
def vibes(t, ch, vel=0.5, g=0.5, d=1.2):
    for i, nt in enumerate(CH[ch]): mus(t + 0.012 * i, R.vib(hz(nt), d, vel), g, -0.3 + 0.2 * i)

# ---------------------------------------------------------------- musik per bagian, hentakan, foley
# ... aransemen per bagian (pola examples/aff001-keset/score.py), hit(cue, [...]) dan fol(t, ...)

# ---------------------------------------------------------------- alas musik kontinu (sesuaikan akor dengan aransemen)
ALAS = ['F6', 'Dm7', 'Bbmaj7', 'C7']
for i, t0 in enumerate(beats(0.05, DUR - 0.3, 4 * BEAT)):
    t1, d = t0, 4 * BEAT
    for a, z in HEN:                                       # tidak menembus hening: mulai lagi sesudahnya
        if a - 0.3 < t0 + d and t0 < z:
            t1, d = z + 0.05, max(0.3, t0 + d - z - 0.05)
    vibes(t1, ALAS[i % len(ALAS)], 0.35, 0.22, d)

# ---------------------------------------------------------------- level per bagian: 0,7–1,4, tetangga beda ≤ 3 dB
LEVEL = []                                 # [(mulai, akhir, faktor)], mis. masalah 0,8 · produk 1,25 · CTA 1,3
for e in MUS:
    for a, z, k in LEVEL:
        if a <= e[0] < z: e[2] *= k

# ---------------------------------------------------------------- aturan mix
HT = sorted({round(h[0], 4) for h in HIT if h[4]})
for e in MUS:                                              # musik diredam 3 dB di sekitar hentakan, TIDAK dihapus
    if any(-0.12 <= e[0] - t <= 0.25 for t in HT): e[2] *= 0.7
CLEAR = [(t - 0.15, t + 0.1) for t in HT]
def crowded(e):                                            # hanya foley yang menabrak hentakan yang dibuang
    return e[4] is None and not any(abs(e[0] - h) < 1e-6 for h in HT) and any(a <= e[0] < z for a, z in CLEAR)
HIT[:] = [e for e in HIT if not crowded(e)]
TAIL = {'bell': 1.6, 'celesta': 0.9, 'marimba': 0.6, 'ride': 1.2, 'kick': 0.4, 'stamp': 0.5, 'clack': 0.25, 'woodblock': 0.25,
        'tick': 0.08, 'click': 0.06, 'snap': 0.15, 'musicbox': 1.0, 'iris': 0.4, 'switch_off': 0.3}
def end_of(name, a):
    if name in ('vib', 'pluck', 'flute', 'stab', 'pad'): return a[1] + 0.3
    if name in ('swish', 'scratch', 'paper', 'brush', 'swell'): return a[0]
    if name in ('whistle', 'pop'): return a[2]
    if name == 'ratchet': return a[1]
    return TAIL.get(name, 0.5)
kept, dropped = [], []
for t, d, g, p, cue in sorted(MUS + HIT, key=lambda e: e[0]):
    name, a = d
    stop = t + end_of(name, a)
    bad = t >= DUR - 0.2 or any(s0 - 0.1 <= t < s1 or (t < s0 and stop > s0 - 0.1) for s0, s1 in HEN)
    if bad and cue:
        raise SystemExit('hit %s at %.3f collides with a silence or the end' % (cue, t))
    (dropped if bad else kept).append((t, d, g, p, cue))
for t, d, g, p, cue in kept:
    R.put(t, d, g, p, cue=cue)

json.dump(R.score(DUR, HEN, room=0.006, lufs=-16), open(HERE / 'score.json', 'w'))
print('events', len(R.events), 'hits', len(R.hits), 'dropped', len(dropped))
