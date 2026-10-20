"""
slate_score: write a score for Slate Studio without any audio dependencies.

    from slate_score import Recorder, hz
    R = Recorder(); put = R.put
    put(0.05, R.vib(hz('F3'), 2.2, 0.9), 1.0, -0.3)
    put(12.042, R.stamp(0.9, 220), 1.2, 0.0, cue='cap_menang')   # a hit: 1 frame after CUES 'cap_menang' in film.js
    json.dump(R.score(durasi=40.0, hening=[(24.05, 24.55)]), open('score.json', 'w'))

Hits put with cue='<id>' are listed in the score as "hits": [{cue, t}] (the server ignores the key);
tools/audit_film.py checks each one lands 1 frame after the matching cue in film.js.

Instruments (arguments in order):
  vib(f, dur, vel)  pluck(f, dur, vel)  celesta(f, vel)  marimba(f, vel)  flute(f, dur, vel)  musicbox(f, vel)
  stab([f...], dur, vel)  pad([f...], dur, vel)
  brush(dur, vel)  snap(vel)  woodblock(f, vel)  ride(vel)  kick(vel)  swell(dur, vel)
  stamp(vel, f)  click(f, vel)  clack(vel)  bell(vel)  swish(dur, lo, hi, vel)  iris(vel)  pop(f0, f1, dur, vel)
  whistle(f0, f1, dur, vel)  ratchet(n, span, vel)  tick(vel)  scratch(dur, vel)  switch_off(vel)  paper(dur, vel)
"""
INSTRUMENTS = ['bell', 'brush', 'celesta', 'clack', 'click', 'flute', 'iris', 'kick', 'marimba', 'musicbox', 'pad', 'paper',
               'pluck', 'pop', 'ratchet', 'ride', 'scratch', 'snap', 'stab', 'stamp', 'swell', 'swish', 'switch_off', 'tick',
               'vib', 'whistle', 'woodblock']


def hz(note):
    names = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7,
             'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    n, o = note[:-1], int(note[-1])
    return 440 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


class Recorder:
    def __init__(self):
        self.events = []
        self.hits = []

    def __getattr__(self, name):
        if name not in INSTRUMENTS:
            raise AttributeError(name)
        return lambda *a: (name, [float(x) if not isinstance(x, (list, tuple)) else [float(y) for y in x] for x in a])

    def put(self, t, desc, gain=1.0, pan=0.0, cue=None):
        self.events.append([round(float(t), 4), desc[0], desc[1], round(float(gain), 4), round(float(pan), 3)])
        if cue:
            self.hits.append({"cue": str(cue), "t": round(float(t), 4)})

    def score(self, durasi, hening=(), room=0.006, lufs=-16.0):
        out = {"durasi": durasi, "hening": [list(h) for h in hening], "room": room, "lufs": lufs, "events": self.events}
        if self.hits:
            out["hits"] = self.hits
        return out
