"""teks_platform.json (doc 16): satu video, teks per platform, dicek sebelum selesai."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import fixture  # noqa: E402
import produksi  # noqa: E402
import teks_platform  # noqa: E402

BAIK = {
    "shopee_video": {"caption": "keset yang airnya langsung kering, alasnya nggak geser. cek keranjang oranye ya"},
    "tiktok": {"caption": "keset kamar mandi serap air, lantai tetap kering.\nalasnya anti-slip. cek keranjang kuning ya\n#kesetkamarmandi #rumahminimalis #racuntiktok"},
    "threads": {"teks": "keluar kamar mandi lantainya licin terus?\nkeset ini nyerap airnya cepat, alasnya juga nggak geser.\nkamu pakai keset apa?\n🔊 Narasi: suara AI",
                "topik": "Rumah Tangga", "balasan": "link-nya: {LINK} (link afiliasi, aku dapat komisi kalau kamu beli)"},
}


class TeksPlatform(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.paket = fixture.buat(Path(self.tmp.name) / "paket")
        self.folder = Path(self.tmp.name) / "paket" / "produksi" / fixture.PRODUK_OK
        produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_OK, "--folder", str(self.folder)])

    def tearDown(self):
        self.tmp.cleanup()

    def tulis(self, d):
        (self.folder / "teks_platform.json").write_text(json.dumps(d, ensure_ascii=False))

    def salah(self, d):
        self.tulis(d)
        return teks_platform.cek(self.folder)[1]

    def test_lolos_dan_teks_post(self):
        self.tulis(BAIK)
        self.assertEqual(teks_platform.main([str(self.folder)]), 0)
        self.assertTrue((self.folder / "teks_post.txt").read_text().startswith("keset yang airnya"))

    def test_platform_wajib_mengikuti_tujuan(self):
        d = {k: v for k, v in BAIK.items() if k != "tiktok"}
        self.assertTrue(any("tiktok: tidak ada" in s for s in self.salah(d)))          # semua = ketiganya
        m = json.loads((self.folder / "produksi.json").read_text())
        m["platform"] = "threads"
        (self.folder / "produksi.json").write_text(json.dumps(m))
        self.assertEqual(self.salah({"threads": BAIK["threads"]}), [])

    def test_shopee_150_dan_tanpa_link(self):
        d = json.loads(json.dumps(BAIK))
        d["shopee_video"]["caption"] = "x" * 151
        self.assertTrue(any("151 karakter" in s for s in self.salah(d)))
        d["shopee_video"]["caption"] = "cek link di bio ya"
        self.assertTrue(any("tanpa link/bio" in s for s in self.salah(d)))

    def test_tiktok_hashtag_dan_larangan(self):
        d = json.loads(json.dumps(BAIK))
        d["tiktok"]["caption"] = "keset kamar mandi serap air. beli di shopee ya #a #b #c"
        self.assertTrue(any("'shopee' dilarang" in s for s in self.salah(d)))
        d["tiktok"]["caption"] = "keset kamar mandi serap air #fyp #viral"
        s = self.salah(d)
        self.assertTrue(any("2 hashtag" in x for x in s) and any("#fyp" in x for x in s))

    def test_threads_link_label_topik_balasan(self):
        d = json.loads(json.dumps(BAIK))
        d["threads"]["teks"] = "keset bagus https://s.shopee.co.id/x"
        d["threads"]["topik"] = "Rumah & Tangga"
        d["threads"]["balasan"] = "beli ya"
        s = " | ".join(self.salah(d))
        for kata in ("balasan pertama, bukan di badan", "suara AI", "threads.topik", "{LINK}"):
            self.assertIn(kata, s)
        d = json.loads(json.dumps(BAIK))
        d["threads"]["teks"] = "🔥" * 120 + "\n🔊 Narasi: suara AI"                         # 480 + byte
        self.assertTrue(any("byte UTF-8" in x for x in self.salah(d)))

    def test_klaim_dan_kata_terlarang(self):
        d = json.loads(json.dumps(BAIK))
        d["shopee_video"]["caption"] = "keset diskon, tahan 99 tahun. cek keranjang oranye"
        s = " | ".join(self.salah(d))
        self.assertIn("diskon", s)
        self.assertIn("angka 99", s)


if __name__ == "__main__":
    unittest.main()
