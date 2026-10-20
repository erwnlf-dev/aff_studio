"""Aturan musik 20 Okt (catatan pemilik: "musik backsound hilang muncul"): audit_film memeriksa alas musik kontinu dan
level antarbagian yang rata; kerangka score.py memenuhinya."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / "tools"))
import audit_film  # noqa: E402

FILM = """const W = 1080, H = 1920, FPS = 24;
export const META = { dur: 20 };
export const CUES = [{ id: 'a', t: 2.0 }];
export default function film(ctx, t) {}
"""


def skor(gain_bagian, lubang=(), dur=20.0, hening=((5.0, 5.6),)):
    """Alas vibrafon per 0,5 s dengan gain per bagian 4 detik; `lubang` = rentang tanpa musik."""
    ev = []
    t = 0.05
    while t < dur - 0.3:
        if not any(a <= t < z for a, z in list(hening) + list(lubang)):
            ev.append([round(t, 3), "vib", [220.0, 0.5, 0.5], gain_bagian[int(t // 4) % len(gain_bagian)], 0.0])
        t += 0.5
    ev.append([2.0 + 1 / 24, "clack", [1.0], 1.0, 0.0])
    return {"durasi": dur, "hening": [list(h) for h in hening], "events": ev, "hits": [{"cue": "a", "t": 2.0 + 1 / 24}]}


class AuditMusik(unittest.TestCase):
    def audit(self, sc):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "film.js").write_text(FILM)
            (d / "vo.json").write_text(json.dumps({"kata": []}))
            (d / "score.json").write_text(json.dumps(sc))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                kode = audit_film.main([str(d)])
            return kode, [b for b in out.getvalue().splitlines() if "musik" in b]

    def test_alas_kontinu_dan_rata_lolos(self):
        kode, baris = self.audit(skor([0.5, 0.45, 0.55, 0.5, 0.6]))
        self.assertEqual(kode, 0, baris)
        self.assertTrue(all(b.startswith("lolos") for b in baris), baris)

    def test_musik_hilang_muncul_gagal(self):
        kode, baris = self.audit(skor([0.5], lubang=[(9.0, 10.5), (13.0, 14.0)]))
        self.assertEqual(kode, 1)
        self.assertTrue(any(b.startswith("GAGAL musik kontinu") for b in baris), baris)

    def test_level_bagian_naik_turun_gagal(self):
        kode, baris = self.audit(skor([0.05, 1.15, 0.1, 1.15, 0.05]))   # pola lama ×0,1–2,3
        self.assertEqual(kode, 1)
        self.assertTrue(any(b.startswith("GAGAL musik rata") for b in baris), baris)

    def test_hening_bukan_lubang(self):
        kode, baris = self.audit(skor([0.5], hening=((5.0, 5.8),)))
        self.assertEqual(kode, 0, baris)

    def test_tanpa_musik_gagal(self):
        sc = skor([0.5])
        sc["events"] = [e for e in sc["events"] if e[1] != "vib"]
        kode, baris = self.audit(sc)
        self.assertEqual(kode, 1)
        self.assertTrue(any("tanpa alas musik" in b for b in baris), baris)

    def test_batas_dari_registry(self):
        import cek_params
        p = cek_params.resolve(cek_params.load())
        b = audit_film.batas_musik()
        for k in audit_film.BATAS_MUSIK:
            self.assertEqual(b[k], float(p[k]), k)                  # audit memakai registry, bawaan hanya cadangan
            self.assertEqual(audit_film.BATAS_MUSIK[k], float(p[k]), k)


class KerangkaSkor(unittest.TestCase):
    def test_kerangka_memenuhi_aturan(self):
        """Kerangka score.py dengan durasi dan satu hening: alas saja sudah kontinu dan hening tetap sunyi."""
        src = (AKAR / "templates" / "produksi" / "score.py").read_text(encoding="utf-8")
        src = src.replace("{{NAMA}}", "Uji").replace("{{JOB}}", "j")
        src = src.replace("DUR = 0.0", "DUR = 20.0").replace("HEN = []", "HEN = [(5.0, 5.6)]")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "score.py").write_text(src)
            subprocess.run([sys.executable, "score.py"], cwd=d, check=True, capture_output=True)
            sc = json.loads((Path(d) / "score.json").read_text())
        lv = audit_film.level_musik(sc)
        db = sorted(x for _, x in lv)
        med = db[len(db) // 2]
        self.assertFalse([t for t, x in lv if x < med - 12])
        self.assertLessEqual(db[9 * len(db) // 10] - db[len(db) // 10], 12)
        self.assertFalse([e for e in sc["events"] if 5.0 <= e[0] < 5.6])


if __name__ == "__main__":
    unittest.main()
