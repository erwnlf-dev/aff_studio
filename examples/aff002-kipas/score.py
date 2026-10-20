"""Mini Kipas Turbo Genggam LED 23000 RPM — partitur. Waktu dari kata_koreksi.json (vo.json job 2026-10-20-bd860a, 18,88 s;
META.dur 19,18 s). Pola: examples/aff001-keset/score.py.

Palet midcentury-toon (seperti Baru Tau): kombo cool-jazz — vibrafon, bass petik (digandakan oktaf + marimba supaya hidup
di atas 300 Hz di speaker HP), brush, jentikan jari, celesta, suling untuk motif. 112 BPM. Setiap bagian punya aransemen sendiri:
hook ringan-terang (F6/Gm7), masalah tipis dan tegang (A minor, brush + marimba + sambungan rel KRL), produk band penuh
(F–Bb–Gm–C + ride), fitur ① woodblock + arpeggio celesta (C), fitur ② bass delapan-an + vibrafon (D minor), bukti swing (G),
CTA akor tiap bagian kembali. Foley per bahan: tombol (click + tick), angin (swish 300–5000 Hz), keringat (pop), desakan
(clack + scratch), kipas keluar tas (swish → stamp), pita (paper), rotor (whistle naik), tisu (paper), cap karet (stamp + click),
keping warna (tick). Hentakan di atas gambar: put(<cue> + 1/24, ..., cue=<id>), dibuka bunyi ber-attack tajam. Swish/paper =
bunyi antisipasi 1–3 frame sebelum benturan. Satu hening di dalam jeda VO: 5,27–5,77 (sebelum "Nah…"), bunyi pertama sesudahnya
adalah hentakan kipas. Motif 3 nada pembuka di celah 2,53–3,05, versi terselesaikan di celah 16,43–16,95.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, '/data/apps/aff_studio/tools')
from slate_score import Recorder, hz

HERE = Path(__file__).resolve().parent
R = Recorder()
DUR = 19.18
FR = 1 / 24
HEN = [(5.27, 5.77)]
BEAT, T0 = 60 / 112, 0.05
CUE = {'nyala': 5, 'kencang': 39, 'desak': 74, 'gerah': 106, 'nah': 140, 'ini': 153, 'kipas': 174, 'motor': 219, 'rpm': 261,
       'enam': 287, 'layar': 329, 'cap': 369, 'segel': 386, 'warna': 412, 'cek': 431, 'link': 439}
CUE = {k: v / 24 for k, v in CUE.items()}
TEKAN5 = [f / 24 for f in (290, 300, 310, 320)]          # tekan 2–5 di fitur ② (tekan ke-6 = cue 'layar')

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
      'Cmaj7': ['C3', 'E3', 'G3', 'B3'], 'D7': ['D3', 'F#3', 'A3', 'C4'], 'E7': ['E3', 'G#3', 'B3', 'D4']}
ROOT = {'F6': 'F2', 'Gm7': 'G2', 'C7': 'C3', 'Am7': 'A2', 'Dm7': 'D2', 'Bbmaj7': 'Bb2', 'G6': 'G2', 'Em7': 'E2', 'Cmaj7': 'C3',
        'D7': 'D2', 'E7': 'E2'}
up = lambda n, k=1: n[:-1] + str(int(n[-1]) + k)
beats = lambda a, z, b=BEAT: [T0 + k * b for k in range(0, int(DUR / b) + 4) if a <= T0 + k * b < z]
chord = lambda t, prog, start, bar=4: prog[int((t - start) / (bar * BEAT)) % len(prog)]
def bass(t, note, dur, vel, g=0.9):
    mus(t, R.pluck(hz(up(note)), dur, vel), g * 0.85, 0.05)
    mus(t, R.marimba(hz(up(note, 2)), vel * 0.55), g * 0.5, 0.1)
def vibes(t, ch, vel=0.5, g=0.5, d=1.2):
    for i, nt in enumerate(CH[ch]): mus(t + 0.012 * i, R.vib(hz(nt), d, vel), g, -0.3 + 0.2 * i)

# ---------------------------------------------------------------- musik per bagian
# HOOK 0–2,45: jentikan di 2 dan 4, vibrafon F6/Gm7, bass dua; motif 3 nada di celah 2,53–3,05
for tt in beats(0.05, 2.45):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['F6', 'Gm7'], 0.05, 2)
    if k in (0, 2): bass(tt, ROOT[ch] if k == 0 else up(CH[ch][2], -1), 0.45, 0.75)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.55, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch)
for i, (nt, d) in enumerate([('C5', 0.12), ('D5', 0.12), ('G5', 0.2)]):
    mus(2.56 + i * 0.14, R.flute(hz(nt), d, 1.0), 1.1, -0.1)
    mus(2.56 + i * 0.14, R.celesta(hz(nt) * 2, 0.6), 0.65, 0.15)

# MASALAH 3,08–5,0: gerbong — brush + ostinato marimba A minor makin tegang, sambungan rel (tik-tak) tiap ketukan
for j, tt in enumerate(beats(3.1, 4.95, BEAT / 2)):
    ch = 'Am7' if tt < 4.1 else 'E7'
    if j % 2 == 0: bass(tt, ROOT[ch], 0.25, 0.6)
    mus(tt, R.brush(BEAT * 0.45, 0.4), 0.35, 0.2)
    if j % 2 == 1: mus(tt, R.marimba(hz(CH[ch][(j // 2) % 4]) * 2, 0.42), 0.45, -0.35)
    if j % 4 == 0: mus(tt + 0.02, R.woodblock(900, 0.55), 0.4, -0.5); mus(tt + 0.13, R.woodblock(760, 0.5), 0.35, -0.5)
mus(4.45, R.pad([hz('E3'), hz('G#3'), hz('D4')], 0.35, 0.45), 0.45, 0)     # selesai 5,10 (sebelum hening)

# PRODUK 5,9–8,5: setelah hening dan hentakan, band masuk lagi lebih terang (F → Bb), jentikan + ride
for tt in beats(5.95, 8.5):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['F6', 'Bbmaj7', 'Gm7', 'C7'], 5.95, 2)
    bass(tt, [ROOT[ch], up(CH[ch][2], -1), ROOT[ch], up(CH[ch][1], -1)][k], 0.4, 0.75)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.5, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch, 0.5, 0.5)
    mus(tt + BEAT / 2, R.ride(0.35), 0.28, 0.4)

# FITUR 1 9,12–11,35: motor — woodblock + arpeggio celesta di C mayor
for tt in beats(9.15, 11.35):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['Cmaj7', 'Am7', 'Dm7', 'G6'], 9.15, 2)
    if k in (0, 2): bass(tt, ROOT[ch] if k == 0 else up(CH[ch][2], -1), 0.4, 0.65)
    mus(tt, R.woodblock(1400 if k % 2 == 0 else 1000, 0.5), 0.35, 0.45 if k % 2 else -0.45)
    mus(tt + BEAT / 2, R.celesta(hz(CH[ch][(k + 1) % 4]) * 4, 0.45), 0.35, -0.2 + 0.1 * k)

# FITUR 2 11,96–14,1: level — bass petik delapan-an, brush, vibrafon di D minor
for j, tt in enumerate(beats(11.98, 14.1, BEAT / 2)):
    ch = chord(tt, ['Dm7', 'Gm7'], 11.98, 2)
    if j % 2 == 0: bass(tt, ROOT[ch] if j % 4 == 0 else up(CH[ch][2], -1), 0.25, 0.65)
    if j % 4 == 2: mus(tt, R.brush(BEAT, 0.45), 0.4, -0.2)
    if j % 8 == 0: vibes(tt, ch, 0.45, 0.45, 1.0)

# BUKTI 14,74–16,35: swing ringan di G, jentikan; band diam di sekitar cap (aturan mix)
for tt in beats(14.76, 16.3):
    k = round((tt - T0) / BEAT) % 4; ch = chord(tt, ['G6', 'Em7'], 14.76, 2)
    bass(tt, [ROOT[ch], up(CH[ch][2], -1), ROOT[ch], up(CH[ch][1], -1)][k], 0.4, 0.7)
    if k in (1, 3): mus(tt, R.snap(0.8), 0.5, 0.35 if k == 1 else -0.35)
    if k == 0: vibes(tt, ch, 0.48, 0.48)
# motif terselesaikan di celah 16,43–16,95
for i, (nt, d) in enumerate([('C5', 0.12), ('D5', 0.12), ('F5', 0.18)]):
    mus(16.45 + i * 0.15, R.flute(hz(nt), d, 1.0), 1.1, -0.1)
    mus(16.45 + i * 0.15, R.celesta(hz(nt) * 2, 0.6), 0.65, 0.15)

# CTA 16,98–18,9: akor setiap bagian kembali singkat, bass, berakhir sebelum film habis
for tt, c in [(17.0, 'F6'), (17.55, 'Bbmaj7'), (18.08, 'Gm7'), (18.55, 'C7')]:
    vibes(tt, c, 0.42, 0.45, 0.25 if tt >= 18.5 else 0.6)
    bass(tt, ROOT[c], 0.3, 0.55, 0.8)

# ---------------------------------------------------------------- hentakan di atas gambar (CUES + 1 frame) dan foley
# HOOK: tombol, angin, turbo, keringat
fol(0.04, R.swish(0.7, 300, 2000, 0.45), 0.5, 0.2)                                         # angin sudah jalan di frame 0
hit('nyala', [(R.clack(1.0), 1.15, 0.3), (R.click(3400, 1.0), 1.0, 0.3), (R.tick(0.8), 0.7, 0.3)])   # QA r1: +93 ms (tertutup "sekecil")
fol(0.32, R.swish(0.6, 400, 3000, 0.5), 0.55, 0.1)
fol(0.95, R.swish(0.6, 400, 3000, 0.5), 0.5, -0.1)
fol(CUE['kencang'] - 2 * FR, R.swish(0.12, 800, 4000, 0.6), 0.6, 0.2)                      # antisipasi turbo
hit('kencang', [(R.click(3400, 0.9), 0.9, 0.1), (R.swish(0.45, 600, 5000, 0.85), 0.9, -0.1), (R.celesta(hz('A6'), 0.6), 0.55, -0.2)])
for i in range(3): fol(CUE['kencang'] + FR + 0.08 + i * 0.07, R.pop(900 + 200 * i, 1800 + 200 * i, 0.06, 0.6), 0.5, -0.3 - 0.2 * i)   # keringat terlempar
fol(2.05, R.swish(0.4, 400, 3000, 0.45), 0.45, -0.2)
# MASALAH: desakan, keringat, kipasan tangan
fol(CUE['desak'] - 3 * FR, R.swish(0.15, 500, 2500, 0.55), 0.5, 0)                        # penumpang mundur → maju
hit('desak', [(R.clack(1.1), 1.1, -0.2), (R.scratch(0.22, 0.75), 0.75, 0.2)])
for tt in (3.55, 3.95, 4.3): fol(tt, R.paper(0.12, 0.45), 0.45, 0.3)                       # tangan mengipas
hit('gerah', [(R.pop(700, 1500, 0.08, 0.85), 0.9, 0.2), (R.click(2800, 0.7), 0.7, 0.2)])
fol(CUE['gerah'] + 0.42, R.pop(500, 900, 0.07, 0.6), 0.5, 0.2)                             # tetes mendarat
# PRODUK: kipas keluar dari tas (swish naik → hentakan setelah hening), tombol, pita
fol(CUE['nah'] - 2 * FR, R.swish(0.1, 900, 4000, 0.7), 0.7, 0)
hit('nah', [(R.stamp(1.1, 300), 1.1, 0), (R.clack(1.0), 0.9, 0), (R.bell(0.9), 0.75, -0.1),
            (R.stab([hz('F3'), hz('A3'), hz('C4'), hz('E4'), hz('G4')], 0.7, 0.9), 0.75, 0), (R.paper(0.3, 0.8), 0.7, 0)])
fol(5.95, R.scratch(0.18, 0.5), 0.5, 0.1)                                                  # tas tersentak
hit('ini', [(R.clack(1.0), 1.15, 0.1), (R.click(3400, 1.0), 1.0, 0.1), (R.tick(0.8), 0.7, 0.1)])      # QA r1: +110 ms
fol(CUE['ini'] + FR + 0.08, R.swish(0.8, 300, 3000, 0.55), 0.55, -0.3)                     # angin mulai
fol(7.0, R.paper(0.5, 0.4), 0.45, -0.5)                                                    # pita berkibar
hit('kipas', [(R.stamp(0.9, 380), 1.0, 0), (R.click(2800, 0.8), 0.8, 0)])
fol(7.9, R.swish(0.5, 300, 2500, 0.45), 0.45, -0.3)
fol(8.55, R.paper(0.33, 0.8), 0.75, 0)                                                     # wipe dari kiri
# FITUR 1: kaca pembesar, rotor (whistle naik), tisu, cap kecil di RPM
hit('motor', [(R.pop(600, 1300, 0.1, 0.8), 0.85, 0.4), (R.click(3000, 0.7), 0.7, 0.4)])
fol(CUE['motor'] + 0.12, R.whistle(260, 1300, 1.7, 0.45), 0.45, 0.4)                       # rotor makin cepat
fol(9.4, R.paper(0.5, 0.45), 0.45, -0.3)                                                   # tisu mulai terangkat
fol(9.92, R.pop(500, 1000, 0.1, 0.6), 0.55, -0.3)                                          # label "angin 20 m/s"
hit('rpm', [(R.clack(1.0), 1.3, 0), (R.click(3400, 1.0), 1.1, 0), (R.stamp(0.9, 420), 1.0, 0), (R.swish(0.4, 800, 5000, 0.7), 0.7, -0.3)])   # QA r2: +124 ms
fol(11.0, R.paper(0.35, 0.5), 0.45, -0.3)                                                  # tisu berkibar
fol(11.4, R.paper(0.33, 0.8), 0.75, 0)                                                     # wipe dari bawah
# FITUR 2: kaca pembesar layar, 5 tekan (klik makin tinggi), angka berganti
hit('enam', [(R.pop(600, 1300, 0.1, 0.8), 0.85, 0.4), (R.click(2600, 0.7), 0.7, 0.4)])
for i, tt in enumerate(TEKAN5):
    fol(tt + FR, R.click(2400 + 300 * i, 0.85), 0.8, -0.3)
    fol(tt + 3 * FR, R.tick(0.6), 0.5, 0.4)
hit('layar', [(R.clack(1.0), 1.3, -0.3), (R.click(3800, 1.0), 1.0, -0.3), (R.bell(0.7), 0.6, 0.4)])   # QA r1: +106 ms
fol(14.2, R.paper(0.33, 0.8), 0.75, 0)                                                     # wipe dari atas
# BUKTI: cap karet + segel
fol(14.6, R.swish(0.3, 500, 3000, 0.6), 0.55, 0.3)                                         # cap datang
fol(CUE['cap'] - 2 * FR, R.swish(0.1, 900, 3500, 0.6), 0.55, 0)
hit('cap', [(R.stamp(1.2, 320), 1.15, 0), (R.clack(1.0), 0.95, 0), (R.click(2600, 0.9), 0.85, 0), (R.bell(1.0), 0.8, 0.1),
            (R.stab([hz('G3'), hz('B3'), hz('D4'), hz('E4'), hz('A4')], 0.8, 0.9), 0.75, 0)])
fol(15.75, R.swish(0.3, 500, 3000, 0.6), 0.55, 0.3)                                        # cap diangkat
hit('segel', [(R.pop(500, 1300, 0.12, 0.8), 0.85, 0.4), (R.celesta(hz('G6'), 0.6), 0.6, 0.4)])
fol(16.4, R.iris(0.7), 0.7, 0)
# CTA: pelat, keping warna, varian, tunjuk
fol(16.86, R.pop(600, 1200, 0.1, 0.7), 0.7, 0)                                             # pelat CTA
hit('warna', [(R.tick(0.9), 0.9, 0.3), (R.paper(0.25, 0.6), 0.6, 0.3)])
for i in range(1, 10, 3): fol(CUE['warna'] + FR + i * 2 * FR, R.tick(0.7), 0.6, 0.3 + 0.05 * i)
fol(CUE['warna'] + 5 * FR, R.pop(700, 1400, 0.1, 0.7), 0.7, -0.4)                         # varian abu
fol(17.0, R.swish(0.35, 500, 2500, 0.5), 0.5, 0.5)                                         # tangan masuk
hit('cek', [(R.clack(0.8), 0.9, 0), (R.click(3000, 0.8), 0.8, 0)])
hit('link', [(R.clack(1.0), 1.3, 0.3), (R.click(3400, 1.0), 1.0, 0.3), (R.bell(0.8), 0.75, 0.3)])     # QA r1: +140 ms ("k" di akhir "link")

# ---------------------------------------------------------------- musik mengembang di celah VO (QA r1: LRA 1,8 LU)
for t0, c, g in [(8.6, 'C7', 1.6), (11.45, 'Dm7', 1.4), (14.27, 'G6', 1.6)]:     # celah 6,30–6,64 dipakai hentakan 'ini' (r3)
    vibes(t0, c, 0.6, g, 0.35)
    bass(t0, ROOT[c], 0.3, 0.8, 1.0)
    mus(t0, R.kick(0.7), 0.6, 0)

# USANG (aturan musik 20 Okt): LEVEL ×0,1–2,3 dan penghapusan musik 'crowded' di bawah membuat musik hilang-muncul
# (catatan pemilik). JANGAN ditiru: pakai blok ALAS, LEVEL 0,7–1,4, dan aturan mix di templates/produksi/score.py.
# ---------------------------------------------------------------- dinamika antar-bagian (target LRA ≥ 2,5 LU; r1 1,8 → lebih kontras)
LEVEL = [(3.0, 5.2, 0.1), (11.9, 14.15, 0.2), (9.1, 11.4, 0.45), (5.85, 8.55, 2.3), (14.7, 16.4, 1.5), (16.95, 19.0, 2.3)]
for e in MUS:
    for a, z, k in LEVEL:
        if a <= e[0] < z: e[2] *= k

# ---------------------------------------------------------------- aturan mix (sama dengan Baru Tau #003 / aff001)
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
for t, d, g, p, cue in dropped:
    print('  dibuang %.3f %s' % (t, d[0]))
for s0, s1 in HEN:
    before = [e for e in R.events if s0 - 1.0 <= e[0] < s0]
    last = max((e[0] + end_of(e[1], e[2]), e[1]) for e in before) if before else None
    print('hening %.2f–%.2f: bunyi terakhir sebelum selesai %s; pertama sesudah %.4f' % (s0, s1, last, min(e[0] for e in R.events if e[0] >= s1)))
