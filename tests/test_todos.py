"""Alat penutup TODO: impor paket, QA compliance (parser angka), biaya, status/keadaan, paket unggah."""
import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import biaya  # noqa: E402
import fixture  # noqa: E402
import impor_paket  # noqa: E402
import produksi  # noqa: E402
import qa_compliance  # noqa: E402

FETCH = r'''import json, sys, zipfile, time
d = json.load(open(sys.argv[1]))
with zipfile.ZipFile("affiliate_assets_%s.zip" % time.strftime("%Y-%m-%d"), "w") as z:
    for p in d:
        for n, i in enumerate(p["images"], 1):
            from PIL import Image; import io
            b = io.BytesIO(); Image.new("RGB", (1024, 1024), (n * 40, 90, 120)).save(b, "JPEG")
            z.writestr("%s/images/%s_%02d.jpg" % (p["product_id"], p["product_id"], n), b.getvalue())
'''


class Impor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        src = fixture.buat(t / "src", foto=False)
        (src / "fetch_images_zip.py").write_text(FETCH)
        self.zip = fixture.zip_dari(src, t / "affiliate_pipeline_data_2026-10-21.zip")
        self.data = t / "data"

    def tearDown(self):
        self.tmp.cleanup()

    def test_daftar(self):
        d = impor_paket.daftar(self.data, [Path(self.tmp.name)])
        self.assertEqual([(x["tanggal"], x["sudah_diimpor"]) for x in d], [("2026-10-21", False)])

    def test_impor_tanpa_dan_dengan_unduh_gambar(self):
        h = impor_paket.impor(self.zip, self.data)
        self.assertEqual(h["siap"], 0)
        self.assertEqual(len(h["produk_tanpa_foto"]), 3)
        h = impor_paket.impor(self.zip, self.data, unduh=True)
        self.assertEqual(h["produk_tanpa_foto"], [])
        self.assertEqual(h["siap"], 2)                       # produk ketiga ditolak karena link bukan Shopee
        self.assertTrue((self.data / "2026-10-21" / "products" / fixture.PRODUK_OK / "images" / ("%s_01.jpg" % fixture.PRODUK_OK)).exists())

    def test_nama_zip_dan_traversal_ditolak(self):
        with self.assertRaises(impor_paket.paket.PaketError):
            impor_paket.tanggal("paket.zip")
        jahat = Path(self.tmp.name) / "affiliate_pipeline_data_2026-10-22.zip"
        with zipfile.ZipFile(jahat, "w") as z:
            z.writestr("../../luar.txt", "x")
        with self.assertRaises(impor_paket.paket.PaketError):
            impor_paket.impor(jahat, self.data)
        self.assertFalse((self.data.parent / "luar.txt").exists())


class Angka(unittest.TestCase):
    def test_parser(self):
        a = qa_compliance.angka
        self.assertEqual(a("23.000 RPM"), {23000.0})
        self.assertEqual(a("★ 4,7"), {4.7})
        self.assertEqual(a("10RB+ terjual"), {10.0, 10000.0})
        self.assertEqual(a("9,5rb+ ulasan"), {9.5, 9500.0})
        self.assertEqual(a("16900r/min"), {16900.0})

    def test_terlarang(self):
        teks = "Diskon 50% | Rp35.000 | harga termurah"
        nama = [n for rx, n in qa_compliance.TERLARANG if rx.search(teks)]
        self.assertEqual(sorted(nama), ["%", "Rp", "diskon", "termurah"])
        self.assertTrue(qa_compliance.DISCLOSURE.search("Link afiliasi"))


class Produksi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.paket = fixture.buat(Path(self.tmp.name) / "paket")
        self.folder = Path(self.tmp.name) / "paket" / "produksi" / fixture.PRODUK_OK
        produksi.main(["init", "--paket", str(self.paket), "--produk", fixture.PRODUK_OK, "--folder", str(self.folder)])

    def tearDown(self):
        self.tmp.cleanup()

    def test_keadaan(self):
        self.assertEqual(produksi.keadaan(self.folder), "belum")
        (self.folder / "naskah.txt").write_text("x")
        self.assertEqual(produksi.keadaan(self.folder), "terhenti")
        (self.folder / "final.mp4").write_bytes(b"0")
        (self.folder / "cek_akhir.md").write_text("ok")
        self.assertEqual(produksi.keadaan(self.folder), "selesai")
        (self.folder / "review.json").write_text(json.dumps({"status": "disetujui"}))
        self.assertEqual(produksi.keadaan(self.folder), "disetujui")

    def test_paket_unggah(self):
        (self.folder / "final.mp4").write_bytes(b"MP4")
        (self.folder / "teks_post.txt").write_text("caption\n(link afiliasi)\n")
        (self.folder / "status.json").write_text(json.dumps({"job_id": "2026-10-20-abc123", "render": {"qa": {"lolos": True, "durasi": 19.0}}}))
        self.assertEqual(produksi.main([str(self.folder), "paket-unggah"]), 1)           # compliance belum ada
        (self.folder / "qa_compliance.json").write_text(json.dumps({"lolos": True}))
        self.assertEqual(produksi.main([str(self.folder), "paket-unggah"]), 0)
        self.assertEqual(produksi.main([str(self.folder), "paket-unggah"]), 0)           # tidak dobel di log
        vid = "%s-2026-10-20-abc123" % fixture.PRODUK_OK
        self.assertTrue((self.paket / "unggah" / vid / (vid + ".mp4")).exists())
        with open(self.paket / "uploads" / "upload_log.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["status"], rows[0]["platform"]), ("siap_unggah", "shopee_video"))

    def test_biaya(self):
        jl = Path(self.tmp.name) / "sesi.jsonl"
        jl.write_text("\n".join([json.dumps({"type": "system", "subtype": "init", "model": "claude-opus-5-5"}),
                                  json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 10.16, "num_turns": 142,
                                              "duration_ms": 2242000})]))
        (self.folder / "vo.json").write_text(json.dumps({"karakter_terpakai": 256, "durasi": 18.9, "job_id": "j"}))
        b = biaya.hitung(self.folder, jl)
        self.assertEqual((b["sesi"]["biaya_usd"], b["sesi"]["turn"], b["sesi"]["durasi_s"]), (10.16, 142, 2242))
        self.assertEqual(b["tts"]["karakter"], 256)
        b2 = biaya.hitung(self.folder)                                                     # catat ulang tanpa transkrip
        self.assertEqual(b2["sesi"]["biaya_usd"], 10.16)


if __name__ == "__main__":
    unittest.main()
