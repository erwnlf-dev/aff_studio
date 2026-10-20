import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture  # noqa: E402
import paket  # noqa: E402

SEKARANG = datetime(2026, 10, 19, 20, 0, tzinfo=timezone.utc)


class Paket(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.akar = fixture.buat(Path(self.tmp.name) / "paket")
        self.hasil = {p["id"]: (p, d, w) for p, d, w in paket.muat(self.akar, sekarang=SEKARANG)}

    def tearDown(self):
        self.tmp.cleanup()

    def test_urut_rank_dan_jumlah(self):
        self.assertEqual(list(self.hasil), [fixture.PRODUK_OK, fixture.PRODUK_RUSAK, fixture.PRODUK_DIATUR])

    def test_produk_ok(self):
        p, ditolak, peringatan = self.hasil[fixture.PRODUK_OK]
        self.assertEqual(ditolak, [])
        self.assertEqual(len(p["foto"]), 4)
        self.assertTrue(p["foto"][0]["cover"])
        self.assertFalse(p["foto"][3]["layar_penuh"])          # 600 px < foto.sisi_pendek_min_px
        self.assertFalse(p["kategori_diatur"])
        self.assertTrue(p["rating_boleh_tampil"])
        self.assertTrue(p["harga_boleh_tampil"])                 # 4 jam < 24 jam
        self.assertEqual(p["harga_umur_jam"], 4.0)
        self.assertEqual(p["compliance_note"], "Jangan tonjolkan persen diskon.")

    def test_angka_hook_di_luar_fitur_diperingatkan(self):
        _, _, peringatan = self.hasil[fixture.PRODUK_OK]
        self.assertTrue(any("video_angle.hook" in m and "3" in m for m in peringatan), peringatan)

    def test_produk_rusak_ditolak(self):
        _, ditolak, _ = self.hasil[fixture.PRODUK_RUSAK]
        self.assertTrue(any("bukan link Shopee" in m for m in ditolak), ditolak)
        self.assertTrue(any("foto lokal 1" in m for m in ditolak), ditolak)

    def test_kategori_diatur(self):
        p, ditolak, peringatan = self.hasil[fixture.PRODUK_DIATUR]
        self.assertEqual(ditolak, [])
        self.assertTrue(p["kategori_diatur"])
        self.assertTrue(any("kategori diatur" in m for m in peringatan))

    def test_harga_tua_tidak_boleh_tampil(self):
        tua = datetime(2026, 10, 22, tzinfo=timezone.utc)
        p = next(p for p, _, _ in paket.muat(self.akar, sekarang=tua) if p["id"] == fixture.PRODUK_OK)
        self.assertFalse(p["harga_boleh_tampil"])

    def test_zip_tanpa_foto_ditolak_semua(self):
        kosong = fixture.buat(Path(self.tmp.name) / "kosong", foto=False)
        z = fixture.zip_dari(kosong, Path(self.tmp.name) / "kosong.zip")
        hasil = paket.muat(z, sekarang=SEKARANG)
        self.assertTrue(all(d for _, d, _ in hasil))

    def test_zip_dengan_foto_terbaca(self):
        z = fixture.zip_dari(self.akar, Path(self.tmp.name) / "paket.zip")
        hasil = {p["id"]: d for p, d, _ in paket.muat(z, sekarang=SEKARANG)}
        self.assertEqual(hasil[fixture.PRODUK_OK], [])

    def test_zip_traversal_ditolak(self):
        z = Path(self.tmp.name) / "jahat.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("../luar.txt", "x")
        with self.assertRaises(paket.PaketError):
            paket.buka(z)

    def test_bukan_paket(self):
        with self.assertRaises(paket.PaketError):
            paket.muat(Path(self.tmp.name) / "tidak_ada")

    def test_cli(self):
        self.assertEqual(paket.main(["cek", str(self.akar)]), 1)    # satu produk ditolak
        self.assertEqual(paket.main(["produk", str(self.akar), fixture.PRODUK_OK]), 0)
        self.assertEqual(paket.main(["produk", str(self.akar), "999"]), 2)


if __name__ == "__main__":
    unittest.main()
