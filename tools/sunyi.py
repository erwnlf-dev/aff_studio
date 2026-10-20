#!/usr/bin/env python3
"""Ukur jendela sunyi di vo.mp3 dan koreksi onset kata → kata_koreksi.json.

    python3 tools/sunyi.py <folder produksi>            # unduh vo.mp3 (sekali), ukur, tulis kata_koreksi.json, cetak ringkasan

Alignment Slate menyerap jeda ruang napas ke durasi kata ("Kenalin…" 4,56–5,78 s; "keset" tercatat 5,82 s padahal suara
mulai 6,12 s). Hentakan gambar yang dipasang di onset alignment jadi meleset sampai 0,5 s. Alat ini:
  1. mengukur jendela sunyi: RMS 20 ms di bawah puncak − 40 dB selama ≥ 0,3 s (yang dipakai brief keset),
  2. memindahkan onset kata yang jatuh di dalam jendela sunyi ke akhir jendela itu, dan akhir kata yang melewati awal
     jendela sunyi ke awal jendela,
  3. menulis kata_koreksi.json {"kata": [[mulai, selesai, teks], ...], "sunyi": [[a, b], ...]}: dipakai film.js (KATA),
     tools/audit_film.py, dan score.py,
  4. mencetak calon hening (jendela ≥ 0,45 s) dan daftar kata berindeks untuk brief.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

SR, WIN = 16000, 0.02
AMBANG_DB, MIN_S, HENING_S = 40.0, 0.3, 0.45


def jendela_sunyi(x, sr=SR, ambang_db=AMBANG_DB, min_s=MIN_S):
    """Daftar (mulai, selesai) detik di mana RMS 20 ms < puncak − ambang_db selama ≥ min_s."""
    n = int(WIN * sr)
    if len(x) < n:
        return []
    blok = x[: len(x) // n * n].reshape(-1, n)
    db = 20 * np.log10(np.sqrt(np.mean(blok ** 2, axis=1)) + 1e-12)
    sunyi = db < db.max() - ambang_db
    out, s = [], None
    for i, b in enumerate(np.append(sunyi, False)):
        if b and s is None:
            s = i
        elif not b and s is not None:
            if (i - s) * WIN >= min_s:
                out.append((round(s * WIN, 2), round(i * WIN, 2)))
            s = None
    return out


def koreksi(kata, sunyi):
    """kata: [{teks, mulai, selesai}] dari vo.json → [[mulai, selesai, teks]] dengan onset di luar jendela sunyi."""
    out = []
    for w in kata:
        a, b = float(w["mulai"]), float(w["selesai"])
        for s0, s1 in sunyi:
            if s0 - 0.02 <= a < s1:
                a = s1
            if s0 < b <= s1 + 0.02 and b - s0 > 0.05 and a < s0:
                b = s0
        out.append([round(a, 3), round(max(b, a + 0.05), 3), w["teks"]])
    return out


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    folder = Path(argv[0])
    vo = json.loads((folder / "vo.json").read_text(encoding="utf-8"))
    mp3 = folder / "vo.mp3"
    if not mp3.exists():
        import slate
        slate.unduh(vo["link_job"], "vo.mp3", mp3)
    sunyi = jendela_sunyi(decode(mp3))
    kata = koreksi(vo.get("kata") or [], sunyi)
    (folder / "kata_koreksi.json").write_text(json.dumps({
        "kata": kata, "sunyi": sunyi,
        "catatan": "onset dikoreksi ke akhir jendela sunyi terukur (vo.mp3, puncak −%g dB, ≥ %g s); tools/sunyi.py" % (AMBANG_DB, MIN_S)},
        ensure_ascii=False, indent=0), encoding="utf-8")
    print("durasi VO %.2f s, %d kata" % (float(vo.get("durasi") or 0), len(kata)))
    print("jendela sunyi (≥ %.1f s): %s" % (MIN_S, ", ".join("%.2f–%.2f" % s for s in sunyi)))
    print("calon hening (≥ %.2f s, sisakan 0,03 s di tiap sisi): %s" % (
        HENING_S, ", ".join("%.2f–%.2f" % (a + 0.03, b - 0.03) for a, b in sunyi if b - a >= HENING_S) or "tidak ada"))
    geser = [(i, w["teks"], w["mulai"], k[0]) for i, (w, k) in enumerate(zip(vo.get("kata") or [], kata)) if abs(float(w["mulai"]) - k[0]) > 0.02]
    if geser:
        print("onset digeser: " + "; ".join("%d %s %.2f→%.2f" % g for g in geser))
    print("KATA (untuk film.js): " + json.dumps(kata, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
