import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
try:
    import numpy as np
    from PIL import Image
    import cutout
except ImportError:   # scipy/numpy hanya ada di .venv
    cutout = None


@unittest.skipIf(cutout is None, "scipy/numpy tidak ada (jalankan dengan .venv/bin/python)")
class Cutout(unittest.TestCase):
    def test_pulau_kecil_dibuang_dan_dipangkas(self):
        a = np.zeros((400, 400, 4), dtype=np.uint8)
        a[100:300, 100:300] = (200, 100, 50, 255)      # benda
        a[10:20, 360:390] = (0, 0, 0, 255)             # sisa teks kecil di pojok
        out = cutout.bersihkan(Image.fromarray(a), 0.02)
        self.assertEqual(out.size, (200 + 48, 200 + 48))
        self.assertEqual(np.array(out)[..., 3].max(), 255)

    def test_kemas_menulis_foto_js(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "cutout").mkdir()
            Image.new("RGBA", (300, 200), (10, 20, 30, 255)).save(Path(d) / "cutout" / "benda.png")
            ukuran, byte = cutout.kemas(d)
            js = (Path(d) / "aset" / "foto.js").read_text()
            self.assertIn("export const FOTO", js)
            self.assertIn("data:image/webp;base64,", js)
            self.assertEqual(ukuran["benda"], (300, 200))


if __name__ == "__main__":
    unittest.main()
