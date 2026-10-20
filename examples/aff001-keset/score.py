"""Keset diatomite — partitur. Waktu dari kata_koreksi.json (vo.json job 2026-10-20-9fed21, 18,42 s; META.dur 18,72 s).

Palet midcentury-toon (seperti Baru Tau): kombo cool-jazz — vibrafon, bass petik (selalu digandakan satu oktaf atau
marimba supaya hidup di atas 300 Hz di speaker HP), brush, jentikan jari, celesta. 112 BPM (lebih rapat dari Baru Tau
karena video 18 s). Foley per bahan: tetes air (pop naik + klik), serap (swish rendah lembut), langkah basah (clack +
swish 2–6 kHz), gelincir (whistle turun), keset jatuh (stamp + clack + kertas), cap karet (stamp 320–420 Hz + click),
balik keset (paper), dorong (scratch + clack). Setiap bagian punya aransemen sendiri. Hentakan di atas gambar ditulis
put(<cue> + 1/24, ..., cue=<id>). Satu hening di dalam jeda VO: 4,58–5,10 (sebelum "Kenalin…"), bunyi pertama sesudahnya
adalah hentakan keset jatuh. Motif 3 nada pembuka di celah 1,74–2,36, versi terselesaikan di celah 15,96–16,56.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools') if (Path(__file__).resolve().parents[2] / 'tools').is_dir() else '/data/apps/aff_studio/tools')
from slate_score import Recorder, hz

HERE = Path(__file__).resolve().parent
R = Recorder()
DUR = 18.72
FR = 1 / 24
HEN = [(4.58, 5.10)]
BEAT, T0 = 60 / 112, 0.05
CUE = {'hook_tetes': 13, 'hook_tetes_2': 35, 'serap': 24, 'kaki_basah': 85, 'licin': 96, 'keset_jatuh': 123, 'nama': 147,
       'motif': 167, 'tetes_1': 207, 'tetes_2': 215, 'kering': 245, 'balik': 271, 'dorong': 296, 'pental': 312, 'cap': 359,
       'segel': 376, 'motif_pop': 397, 'cek': 421, 'link': 429}
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
      'Dm7': ['D3', 'F3', 'A3', 'C4'], 'Bbmaj7': ['Bb2', 'D3', 'F3', 'A3'], 'G6': ['G3', 'B3', 'D4', 'E4'], 'Em7': ['E3', 'G3', 'B3', 'D4'],
      'Cmaj7': ['C3', 'E3', 'G3', 'B3'], 'D7': ['D3', 'F#3', 'A3', 'C4']}
ROOT = {'F6': 'F2', 'Gm7': 'G2', 'C7': 'C3', 'Am7': 'A2', 'Dm7': 'D2', 'Bbmaj7': 'Bb2', 'G6': 'G2', 'Em7': 'E2', 'Cmaj7': 'C3', 'D7': 'D2'}
up = lambda n, k=1: n[:-1] + str(int(n[-1]) + k)
beats = lambda a, z, b=BEAT: [T0 + k * b for k in range(0, int(DUR / b) + 4) if a <= T0 + k * b < z]
chord = lambda t, prog, start, bar=4: prog[int((t - start) / (bar * BEAT)) % len(prog)]
def bass(t, note, dur, vel, g=0.9):
    mus(t, R.pluck(hz(up(note)), dur, vel), g * 0.85, 0.05)
    mus(t, R.marimba(hz(up(note, 2)), vel * 0.55), g * 0.5, 0.1)
def vibes(t, ch, vel=0.5, g=0.5, d=1.2):
    for i, nt in enumerate(CH[ch]): mus(t + 0.012 * i, R.vib(hz(nt), d, vel), g, -0.3 + 0.2 * i)

# ---------------------------------------------------------------- musik per bagian
# HOOK 0–1,74: jentikan di 2 dan 4, vibrafon F6/Gm7, bass dua; motif 3 nada di celah 1,74–2,36
for tt in beats(0.05, 1.7):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['F6', 'Gm7'], 0.05, 2)
    if k in (0, 2): bass(tt, ROOT[ch] if k == 0 else up(CH[ch][2], -1), 0.45, 0.75)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.55, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch)
for i, (nt, d) in enumerate([('C5', 0.12), ('D5', 0.12), ('G5', 0.2)]):
    mus(1.8 + i * 0.14, R.flute(hz(nt), d, 1.0), 1.1, -0.1)
    mus(1.8 + i * 0.14, R.celesta(hz(nt) * 2, 0.6), 0.65, 0.15)

# MASALAH 2,36–4,5: kamar mandi — brush + ostinato marimba di A minor yang makin tegang, bass satu nada
for j, tt in enumerate(beats(2.38, 4.45, BEAT / 2)):
    ch = 'Am7' if tt < 3.5 else 'D7'
    if j % 2 == 0: bass(tt, ROOT[ch], 0.25, 0.6)
    mus(tt, R.brush(BEAT * 0.45, 0.4), 0.35, 0.2)
    if j % 2 == 1: mus(tt, R.marimba(hz(CH[ch][(j // 2) % 4]) * 2, 0.42), 0.45, -0.35)
mus(3.9, R.pad([hz('D3'), hz('F#3'), hz('C4')], 0.5, 0.45), 0.45, 0)       # sebelum gelincir; selesai sebelum hening

# PRODUK 5,17–8,0: setelah hening dan hentakan, band masuk lagi lebih terang (F → Bb), jentikan + ride
for tt in beats(5.4, 8.0):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['F6', 'Bbmaj7', 'Gm7', 'C7'], 5.4, 2)
    bass(tt, [ROOT[ch], up(CH[ch][2], -1), ROOT[ch], up(CH[ch][1], -1)][k], 0.4, 0.75)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.5, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch, 0.5, 0.5)
    mus(tt + BEAT / 2, R.ride(0.35), 0.28, 0.4)

# FITUR 1 8,38–10,7: air — woodblock ringan + arpeggio celesta di C mayor
for tt in beats(8.4, 10.65):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['Cmaj7', 'Am7', 'Dm7', 'G6'], 8.4, 2)
    if k in (0, 2): bass(tt, ROOT[ch] if k == 0 else up(CH[ch][2], -1), 0.4, 0.65)
    mus(tt, R.woodblock(1400 if k % 2 == 0 else 1000, 0.5), 0.35, 0.45 if k % 2 else -0.45)
    mus(tt + BEAT / 2, R.celesta(hz(CH[ch][(k + 1) % 4]) * 4, 0.45), 0.35, -0.2 + 0.1 * k)

# FITUR 2 11,3–13,5: dorong — bass petik delapan-an, brush, vibrafon di D minor
for j, tt in enumerate(beats(11.3, 13.5, BEAT / 2)):
    ch = chord(tt, ['Dm7', 'Gm7'], 11.3, 2)
    if j % 2 == 0: bass(tt, ROOT[ch] if j % 4 == 0 else up(CH[ch][2], -1), 0.25, 0.65)
    if j % 4 == 2: mus(tt, R.brush(BEAT, 0.45), 0.4, -0.2)
    if j % 8 == 0: vibes(tt, ch, 0.45, 0.45, 1.0)

# BUKTI 14,12–15,96: swing ringan di G, jentikan; band diam di sekitar cap (aturan mix)
for tt in beats(14.15, 15.9):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['G6', 'Em7'], 14.15, 2)
    bass(tt, [ROOT[ch], up(CH[ch][2], -1), ROOT[ch], up(CH[ch][1], -1)][k], 0.4, 0.7)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.5, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch, 0.48, 0.48)
# motif terselesaikan di celah 15,96–16,56
for i, (nt, d) in enumerate([('C5', 0.12), ('D5', 0.12), ('F5', 0.18)]):
    mus(16.0 + i * 0.15, R.flute(hz(nt), d, 1.0), 1.1, -0.1)
    mus(16.0 + i * 0.15, R.celesta(hz(nt) * 2, 0.6), 0.65, 0.15)

# CTA 16,56–18,6: akor setiap bagian kembali singkat, bass, berakhir sebelum film habis
for tt, c in [(16.6, 'F6'), (17.15, 'Bbmaj7'), (17.68, 'Gm7'), (18.1, 'C7')]:
    vibes(tt, c, 0.42, 0.45, 0.3 if tt >= 18.1 else 0.6)
    bass(tt, ROOT[c], 0.3, 0.55, 0.8)

# ---------------------------------------------------------------- hentakan di atas gambar (CUES + 1 frame) dan foley
fol(0.06, R.tick(0.7), 0.6, 0.4)                                                            # gayung miring
fol(0.2, R.pop(700, 1100, 0.06, 0.6), 0.55, 0.3)                                            # tetes lepas
hit('hook_tetes', [(R.pop(900, 1900, 0.08, 0.9), 1.0, 0.1), (R.click(3200, 0.8), 0.8, 0.1)])
fol(0.62, R.swish(0.5, 300, 1600, 0.45), 0.5, 0.1)                                          # serap
fol(1.3, R.celesta(hz('E6'), 0.7), 0.6, 0.1)                                              # tanpa hit di 'serap': bunyinya tertutup kata "nyerap" (QA r1–r2: onset +153 ms)
fol(1.15, R.pop(700, 1100, 0.06, 0.6), 0.55, 0.3)
hit('hook_tetes_2', [(R.pop(900, 2000, 0.08, 0.9), 1.0, -0.1), (R.click(3400, 0.8), 0.8, -0.1)])
fol(1.52, R.swish(0.5, 300, 1600, 0.45), 0.5, -0.1)
fol(2.42, R.swish(0.35, 500, 2500, 0.6), 0.5, -0.4)                                         # kaki masuk
hit('kaki_basah', [(R.clack(1.2), 1.15, -0.2), (R.click(3200, 0.9), 0.95, -0.2)])
fol(CUE['kaki_basah'] + FR + 0.12, R.swish(0.22, 2000, 6000, 0.7), 0.7, -0.2)            # percik sesudah benturan (QA r2: swish +112 ms)
hit('licin', [(R.whistle(1500, 500, 0.32, 0.8), 0.9, 0.1), (R.scratch(0.2, 0.7), 0.7, 0.1)])
hit('keset_jatuh', [(R.stamp(1.1, 300), 1.1, 0), (R.clack(1.0), 0.9, 0), (R.bell(0.9), 0.75, -0.1),
                    (R.stab([hz('F3'), hz('A3'), hz('C4'), hz('E4'), hz('G4')], 0.7, 0.9), 0.75, 0), (R.paper(0.3, 0.8), 0.7, 0)])
for i in range(5): fol(5.3 + i * 4 / 24, R.pop(800 + 120 * i, 1500 + 120 * i, 0.07, 0.6), 0.55, -0.4 + 0.2 * i)   # genangan terserap
hit('nama', [(R.stamp(0.9, 380), 1.0, 0), (R.click(2800, 0.8), 0.8, 0)])
hit('motif', [(R.scratch(0.35, 0.8), 0.85, -0.3)])
fol(7.22, R.pop(500, 1000, 0.1, 0.6), 0.55, -0.3)                                           # label "motif kucing"
fol(8.0, R.paper(0.33, 0.8), 0.75, 0)                                                       # wipe dari bawah
fol(8.36, R.tick(0.7), 0.6, 0.4)                                                            # gayung
hit('tetes_1', [(R.pop(900, 1900, 0.08, 0.9), 1.0, 0.1), (R.click(3200, 0.8), 0.8, 0.1)])
fol(8.72, R.swish(0.5, 300, 1600, 0.45), 0.5, 0.1)
hit('tetes_2', [(R.pop(900, 2000, 0.08, 0.9), 1.0, -0.1), (R.click(3400, 0.8), 0.8, -0.1)])
fol(9.05, R.swish(0.5, 300, 1600, 0.45), 0.5, -0.1)
fol(9.78, R.swish(0.3, 500, 3000, 0.6), 0.55, 0.4)                                          # tangan + cap masuk
hit('kering', [(R.stamp(0.9, 420), 1.0, 0.4), (R.click(3000, 0.9), 0.9, 0.4), (R.celesta(hz('D6'), 0.7), 0.7, 0.4)])
fol(10.84, R.paper(0.33, 0.8), 0.75, 0)                                                     # wipe dari kiri
fol(CUE['balik'] - FR, R.paper(0.3, 0.9), 0.9, 0)                                         # kertas mulai sebelum, klik di frame
hit('balik', [(R.click(2400, 0.9), 0.9, 0), (R.clack(0.7), 0.7, 0)])
fol(11.97, R.paper(0.3, 0.8), 0.8, 0)                                                       # balik lagi
fol(12.05, R.swish(0.3, 500, 2500, 0.6), 0.55, 0.5)                                         # tangan masuk
hit('dorong', [(R.clack(1.0), 1.0, 0.3), (R.scratch(0.22, 0.8), 0.8, 0.3)])
hit('pental', [(R.clack(0.8), 0.9, 0.4), (R.click(2600, 0.8), 0.8, 0.4)])
fol(CUE['pental'] + FR + 0.06, R.whistle(600, 1400, 0.18, 0.5), 0.5, 0.4)
fol(13.66, R.paper(0.33, 0.8), 0.75, 0)                                                     # wipe dari atas
fol(14.25, R.swish(0.3, 500, 3000, 0.6), 0.55, 0.3)                                         # cap datang
hit('cap', [(R.stamp(1.2, 320), 1.15, 0), (R.clack(1.0), 0.95, 0), (R.click(2600, 0.9), 0.85, 0), (R.bell(1.0), 0.8, 0.1),
            (R.stab([hz('G3'), hz('B3'), hz('D4'), hz('E4'), hz('A4')], 0.8, 0.9), 0.75, 0)])
fol(15.2, R.swish(0.3, 500, 3000, 0.6), 0.55, 0.3)                                          # cap diangkat
hit('segel', [(R.pop(500, 1300, 0.12, 0.8), 0.85, 0.4), (R.celesta(hz('G6'), 0.6), 0.6, 0.4)])
fol(16.1, R.iris(0.7), 0.7, 0)
hit('motif_pop', [(R.pop(600, 1300, 0.1, 0.8), 0.85, -0.4)])
fol(CUE['motif_pop'] + 5 / 24, R.pop(700, 1400, 0.1, 0.7), 0.75, 0.4)
fol(CUE['motif_pop'] + 9 / 24, R.pop(800, 1500, 0.1, 0.7), 0.75, 0.3)
hit('cek', [(R.clack(0.8), 0.9, 0), (R.click(3000, 0.8), 0.8, 0)])
hit('link', [(R.bell(0.8), 0.75, 0.3), (R.click(3200, 0.8), 0.8, 0.3)])

# ---------------------------------------------------------------- dinamika antar-bagian (QA r1: LRA 1,2 LU, target ≥ 2,5)
LEVEL = [(2.33, 4.55, 0.3), (11.17, 13.6, 0.38), (8.33, 11.1, 0.75), (5.12, 8.0, 1.7), (14.0, 16.4, 1.25), (16.5, 18.6, 1.7)]
for e in MUS:
    for a, z, k in LEVEL:
        if a <= e[0] < z: e[2] *= k

# ---------------------------------------------------------------- aturan mix (sama dengan Baru Tau #003)
HT = sorted({round(h[0], 4) for h in HIT if h[4]})
for e in MUS:
    if any(-0.12 <= e[0] - t <= 0.25 for t in HT): e[2] *= 0.5
CLEAR = [(t - 0.15, t + 0.1) for t in HT]
def crowded(e):
    return e[4] is None and not any(abs(e[0] - h) < 1e-6 for h in HT) and any(a <= e[0] < z for a, z in CLEAR)
MUS[:] = [e for e in MUS if not crowded(e)]
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
    bad = t >= DUR - 0.2
    for s0, s1 in HEN:
        if s0 - 0.1 <= t < s1 or (t < s0 and stop > s0 - 0.1):
            bad = True
    if bad and cue:
        raise SystemExit('hit %s at %.3f collides with a silence or the end' % (cue, t))
    (dropped if bad else kept).append((t, d, g, p, cue))
for t, d, g, p, cue in kept:
    R.put(t, d, g, p, cue=cue)
json.dump(R.score(DUR, HEN, room=0.006, lufs=-16), open(HERE / 'score.json', 'w'))
print('events', len(R.events), 'hits', len(R.hits), 'dropped', len(dropped), 'last', max(e[0] for e in R.events))
for s0, s1 in HEN:
    before = [e for e in R.events if s0 - 1.0 <= e[0] < s0]
    last = max((e[0] + end_of(e[1], e[2]), e[1]) for e in before) if before else None
    print('hening %.2f–%.2f: bunyi terakhir sebelum selesai %s; pertama sesudah %.4f' % (s0, s1, last, min(e[0] for e in R.events if e[0] >= s1)))
