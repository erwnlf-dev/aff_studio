"""Alur baku: tools/sunyi.py, tools/produksi.py init/status/kata, kit affiliate, run_produksi.sh."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture  # noqa: E402
import produksi  # noqa: E402
import sunyi  # noqa: E402


class Sunyi(unittest.TestCase):
    def test_jendela_sunyi(self):
        sr = sunyi.SR
        x = np.concatenate([np.sin(np.arange(sr) * 0.3) * 0.5, np.zeros(int(0.6 * sr)), np.sin(np.arange(sr) * 0.3) * 0.5,
                            np.zeros(int(0.2 * sr)), np.sin(np.arange(sr // 2) * 0.3) * 0.5]).astype(np.float32)
        j = sunyi.jendela_sunyi(x)
        self.assertEqual(len(j), 1)                          # jeda 0,2 s di bawah ambang 0,3 s tidak dihitung
        self.assertAlmostEqual(j[0][0], 1.0, delta=0.03)
        self.assertAlmostEqual(j[0][1], 1.6, delta=0.03)

    def test_koreksi_onset(self):
        kata = [{"teks": "Kenalin…", "mulai": 4.56, "selesai": 5.78}, {"teks": "keset", "mulai": 5.82, "selesai": 6.36}]
        k = sunyi.koreksi(kata, [(4.52, 5.14), (5.72, 6.12)])
        self.assertEqual(k, [[5.14, 5.72, "Kenalin…"], [6.12, 6.36, "keset"]])


class Produksi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.paket = fixture.buat(Path(self.tmp.name) / "paket")

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_dan_status(self):
        folder = Path(self.tmp.name) / "kerja"
        self.assertEqual(produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_OK, "--folder", str(folder)]), 0)
        for f in ("produksi.json", "produk.json", "data_layar.json", "foto_sheet.jpg", "naskah.json", "brief.md", "film.js", "score.py"):
            self.assertTrue((folder / f).exists(), f)
        dl = json.loads((folder / "data_layar.json").read_text())
        self.assertEqual(dl["terjual"], "10RB+")
        self.assertEqual((dl["rating"], dl["ulasan"]), ("4,8", "9,5rb+"))
        self.assertIsNone(dl["harga"])                        # harga.mode = tanpa_angka
        naskah = json.loads((folder / "naskah.json").read_text())
        self.assertEqual([b["tipe"] for b in naskah["beats"]], ["hook", "masalah", "produk", "fitur", "fitur", "bukti", "cta"])
        self.assertNotIn("{{", (folder / "film.js").read_text() + (folder / "brief.md").read_text())
        # init kedua tidak menimpa pekerjaan kreator
        (folder / "film.js").write_text("// karya kreator")
        produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_OK, "--folder", str(folder)])
        self.assertEqual((folder / "film.js").read_text(), "// karya kreator")
        self.assertEqual(produksi.main([str(folder), "status"]), 0)

    def test_init_menolak_produk_ditolak(self):
        self.assertEqual(produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_RUSAK,
                                        "--folder", str(Path(self.tmp.name) / "x")]), 1)

    def test_render_tanpa_skor_ditolak(self):
        folder = Path(self.tmp.name) / "kerja"
        produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_OK, "--folder", str(folder)])
        self.assertEqual(produksi.main([str(folder), "render"]), 1)

    def test_bukan_folder_produksi(self):
        self.assertEqual(produksi.main([self.tmp.name, "naskah"]), 1)


class Kit(unittest.TestCase):
    KIT = AKAR / "kits" / "affiliate" / "aff.js"

    def test_tanpa_pola_nondeterministik(self):
        kode = re.sub(r"/\*.*?\*/|//[^\n]*", "", self.KIT.read_text(encoding="utf-8"), flags=re.S)
        for pola in (r"\bMath\.random\s*\(", r"\bDate\.now\s*\(", r"\bnew\s+Date\s*\(", r"\bperformance\.now\s*\(",
                     r"\bsetTimeout\s*\(", r"\bsetInterval\s*\(", r"\brequestAnimationFrame\s*\("):
            self.assertIsNone(re.search(pola, kode), pola)

    @unittest.skipUnless(shutil.which("node"), "node tidak ada")
    def test_sintaks(self):
        for f in (self.KIT, AKAR / "templates" / "produksi" / "film.js", AKAR / "examples" / "aff001-keset" / "film.js"):
            with tempfile.TemporaryDirectory() as d:
                m = Path(d) / "x.mjs"
                shutil.copy(f, m)
                r = subprocess.run(["node", "--check", str(m)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, "%s: %s" % (f, r.stderr))

    def test_tint_dibatasi(self):
        self.assertIn("Math.min(k, 0.15)", self.KIT.read_text(encoding="utf-8"))

    def test_contoh_memakai_kit_dan_konstanta_lokal(self):
        src = (AKAR / "examples" / "aff001-keset" / "film.js").read_text(encoding="utf-8")
        self.assertIn("from './engine/aff.js'", src)
        self.assertRegex(src, r"const W = 1080, H = 1920, FPS = 24;")
        self.assertNotRegex(src, r"import \{[^}]*\bFPS\b[^}]*\} from './engine/aff.js'")


class Skrip(unittest.TestCase):
    def test_run_produksi_sintaks(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(AKAR / "run_produksi.sh")]).returncode, 0)

    def test_izin_kreator(self):
        cfg = json.loads((AKAR / ".claude" / "kreator.json").read_text())
        deny = cfg["permissions"]["deny"]
        # path absolut (diisi run_produksi.sh): aturan "./" ikut berpindah kalau kreator `cd` (run kipas 20 Okt)
        self.assertIn("Read(/{{REPO}}/.env)", deny)
        self.assertIn("Edit(/{{REPO}}/**)", deny)
        self.assertFalse(any(d.startswith(("Read(./", "Edit(./")) for d in deny), deny)
        isi = (AKAR / "run_produksi.sh").read_text()
        for t in ("WebSearch", "WebFetch"):
            self.assertIn('"%s"' % t, isi.split("--disallowedTools", 1)[1].split("\n", 1)[0])


if __name__ == "__main__":
    unittest.main()
