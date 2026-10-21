import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AKAR / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cek_params  # noqa: E402
import fixture  # noqa: E402
import paket  # noqa: E402
import pratinjau  # noqa: E402
import siapkan_film as sf  # noqa: E402

SEKARANG = datetime(2026, 10, 19, 20, 0, tzinfo=timezone.utc)
FILM = AKAR / "templates" / "kartu" / "film.js"


class Dasar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.akar = fixture.buat(Path(cls.tmp.name) / "paket")
        cls.reg = cek_params.load()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def produk(self, pid=fixture.PRODUK_OK, params=None):
        params = params or cek_params.resolve(self.reg)
        return next(p for p, _, _ in paket.muat(self.akar, params, SEKARANG) if p["id"] == pid)

    def susun(self, naskah=None, ov=None, vo=None, pid=fixture.PRODUK_OK):
        snap = cek_params.snapshot(self.reg, ov or {})
        return sf.susun(self.produk(pid, snap["params"]), naskah or copy.deepcopy(fixture.NASKAH_OK), snap, vo)


class Susun(Dasar):
    def test_hasil_lengkap(self):
        isi, foto, txt, scenes, ringkas = self.susun()
        self.assertEqual([b["tipe"] for b in isi["beats"]], ["hook", "masalah", "produk", "fitur", "fitur", "bukti", "cta"])
        self.assertEqual(isi["timing"], "perkiraan")
        self.assertNotIn("*", txt)
        self.assertEqual(len(scenes), 7)
        self.assertEqual(isi["beats"][0]["teks_kunci"], "Keset ini nyerap air?")     # hook_layar
        self.assertEqual(isi["beats"][-1]["teks_kunci"], "Cek keranjang oranye")     # cta_layar
        self.assertEqual((isi["template"], isi["hook_tipe"], isi["cta_tempat"]), ("masalah_solusi", "demo", "keranjang oranye"))
        self.assertEqual(isi["disclosure"], "Link afiliasi")
        self.assertEqual(isi["variant_id"], ringkas["variant_id"])
        self.assertTrue(foto["foto"][0]["src"].startswith("data:image/jpeg;base64,"))

    def test_beat_berurutan_dan_menutup_durasi(self):
        isi = self.susun()[0]
        b = isi["beats"]
        self.assertEqual(b[0]["t0"], 0.0)
        self.assertEqual(b[-1]["t1"], isi["dur"])
        for x, y in zip(b, b[1:]):
            self.assertEqual(x["t1"], y["t0"])
        p = isi["params"]
        self.assertGreaterEqual(b[-1]["t1"] - b[-1]["t0"], p["cta.durasi_detik"])

    def test_caption_maks_7_kata_dan_teks_sama_dengan_vo(self):
        isi, _, txt, _, _ = self.susun()
        semua = []
        for g in isi["caption"]:
            self.assertLessEqual(len(g["kata"]), 7)
            self.assertLessEqual(len(g["sorot"]), isi["params"]["caption.kata_disorot_per_layar"])
            self.assertLess(g["t0"], g["t1"])
            semua += [isi["kata"][i]["teks"] for i in g["kata"]]
        self.assertEqual(" ".join(semua), txt)

    def test_sorot_dari_bintang(self):
        self.assertEqual(sf.kata_dari_vo("Lip balm, tapi *ada warnanya*?"),
                         [("Lip", False), ("balm,", False), ("tapi", False), ("ada", True), ("warnanya?", True)])

    def test_harga_dibuang_saat_tanpa_angka(self):
        isi = self.susun()[0]
        self.assertNotIn("harga", [b["tipe"] for b in isi["beats"]])

    def test_lengan_harga_butuh_beat_harga(self):
        with self.assertRaises(sf.NaskahError):
            self.susun(ov={"harga.mode": "angka_bertanggal"})
        n = copy.deepcopy(fixture.NASKAH_OK)
        n["beats"].insert(6, {"tipe": "harga", "vo": "Cek harganya di bawah.", "foto": 0, "sumber": ["harga"]})
        isi = self.susun(n, ov={"harga.mode": "angka_bertanggal"})[0]
        h = next(b for b in isi["beats"] if b["tipe"] == "harga")["harga"]
        self.assertEqual(h, {"teks": "Rp25.000", "tanggal": "2026-10-19"})

    def test_timing_vo_dipakai(self):
        _, _, txt, _, _ = self.susun()
        kata = [{"teks": w, "mulai": i * 0.4, "selesai": i * 0.4 + 0.3} for i, w in enumerate(txt.split())]
        isi = self.susun(vo={"durasi": kata[-1]["selesai"] + 0.5, "kata": kata})[0]
        self.assertEqual(isi["timing"], "vo")
        self.assertEqual(isi["kata"][5]["t0"], 2.0)

    def test_timing_vo_tidak_cocok_ditolak(self):
        with self.assertRaises(sf.NaskahError):
            self.susun(vo={"durasi": 5, "kata": [{"teks": "lain", "mulai": 0, "selesai": 0.3}]})


class Tolak(Dasar):
    def gagal(self, ubah, ov=None, pid=fixture.PRODUK_OK, pesan=""):
        n = copy.deepcopy(fixture.NASKAH_OK)
        ubah(n)
        with self.assertRaises(sf.NaskahError) as c:
            self.susun(n, ov=ov, pid=pid)
        self.assertIn(pesan, str(c.exception))

    def test_urutan_salah(self):
        self.gagal(lambda n: n["beats"].pop(1), pesan="urutan beat")

    def test_sumber_tidak_sah(self):
        self.gagal(lambda n: n["beats"][3].update(sumber=["video_angle"]), pesan="sumber")

    def test_fitur_di_luar_daftar(self):
        self.gagal(lambda n: n["beats"][3].update(sumber=["fitur:9"]), pesan="fitur:9")

    def test_kalimat_terlalu_panjang(self):
        self.gagal(lambda n: n["beats"][1].update(vo="satu dua tiga empat lima enam tujuh delapan sembilan sepuluh sebelas dua belas tiga."),
                   pesan="kalimat")

    def test_hook_layar_terlalu_panjang(self):
        self.gagal(lambda n: n.update(hook_layar="satu dua tiga empat lima enam"), pesan="hook_layar")

    # ---- aturan pasar Indonesia (docs/15)
    def test_cta_harus_ke_keranjang(self):
        def ubah(n):
            n["cta_layar"] = "Cek di link"
            n["beats"][-1]["vo"] = "Warnanya ada dua, *cek di link* ya."
        self.gagal(ubah, pesan="keranjang oranye")

    def test_cta_link_ditolak_walau_ada_keranjang(self):
        self.gagal(lambda n: n["beats"][-1].update(vo="Cek *keranjang oranye* atau link di bio."), pesan="link/bio")

    def test_cta_tiktok_keranjang_kuning(self):
        def ubah(n):
            n["cta_layar"] = "Cek keranjang kuning"
            n["beats"][-1]["vo"] = "Warnanya ada dua, cek *keranjang kuning* ya."
        n = copy.deepcopy(fixture.NASKAH_OK)
        ubah(n)
        self.assertEqual(self.susun(n, ov={"cta.tempat": "keranjang kuning"})[0]["cta_tempat"], "keranjang kuning")

    def test_kenalin_ditolak(self):
        self.gagal(lambda n: n["beats"][2].update(vo="Kenalin… keset contoh *serap air*."), pesan="Kenalin")

    def test_hook_maks_8_kata(self):
        self.gagal(lambda n: n["beats"][0].update(vo="Keset kamar mandi yang ini ternyata bisa *nyerap air*?"), pesan="hook 9 kata")

    def test_hook_tipe_wajib(self):
        self.gagal(lambda n: n.pop("hook_tipe"), pesan="hook_tipe")

    def test_hook_masalah_kategori_diatur(self):
        n = copy.deepcopy(fixture.NASKAH_OK)
        n["hook_tipe"] = "masalah"
        n["product_id"] = fixture.PRODUK_DIATUR
        for b in n["beats"]:
            b["foto"] = 0
        with self.assertRaises(sf.NaskahError) as c:
            self.susun(n, pid=fixture.PRODUK_DIATUR)
        self.assertIn("kategori diatur", str(c.exception))

    def test_variasi_template_dan_hook(self):
        saudara = [("111", ("masalah_solusi", "demo")), ("222", ("fitur_cepat", "hasil"))]
        snap = cek_params.snapshot(self.reg, {})
        with self.assertRaises(sf.NaskahError) as c:
            sf.susun(self.produk(), copy.deepcopy(fixture.NASKAH_OK), snap, None, saudara)
        self.assertIn("sama dengan 111", str(c.exception))
        n = copy.deepcopy(fixture.NASKAH_OK)
        n["hook_tipe"] = "nilai"                                    # pasangan baru: lolos
        self.assertEqual(sf.susun(self.produk(), n, snap, None, saudara)[0]["hook_tipe"], "nilai")
        lama = [("333", ("masalah_solusi", "angka"))] * 2 + [("111", ("masalah_solusi", "demo"))]
        sf.susun(self.produk(), copy.deepcopy(fixture.NASKAH_OK), snap, None, lama)   # di luar 2 video terakhir

    def test_template_fitur_cepat_dipilih_naskah(self):
        n = copy.deepcopy(fixture.NASKAH_OK)
        n["template"] = "fitur_cepat"
        with self.assertRaises(sf.NaskahError) as c:                # urutan masalah_solusi ≠ fitur_cepat
            self.susun(n)
        self.assertIn("template fitur_cepat", str(c.exception))
        n["template"] = "price_reveal"
        with self.assertRaises(sf.NaskahError) as c:
            self.susun(n)
        self.assertIn("tidak boleh", str(c.exception))

    def test_vo_lama_hanya_peringatan(self):
        """Run ulang dengan VO lama ("cek di link", tanpa hook_tipe) tidak macet: pelanggaran jadi peringatan."""
        n = copy.deepcopy(fixture.NASKAH_OK)
        n.pop("hook_tipe")
        n["cta_layar"] = "Cek di link"
        n["beats"][-1]["vo"] = "Warnanya ada dua, *cek di link* ya."
        teks = " ".join(b["vo"].replace("*", "") for b in n["beats"]).split()
        kata = [{"teks": w, "mulai": i * 0.4, "selesai": i * 0.4 + 0.3} for i, w in enumerate(teks)]
        per = []
        isi = sf.susun(self.produk(), n, cek_params.snapshot(self.reg, {}), {"durasi": kata[-1]["selesai"] + 0.5, "kata": kata}, (), per)[0]
        self.assertEqual(isi["timing"], "vo")
        self.assertTrue(any("keranjang oranye" in w for w in per) and any("hook_tipe" in w for w in per), per)

    def test_foto_di_luar_daftar(self):
        self.gagal(lambda n: n["beats"][0].update(foto=9), pesan="foto")

    def test_hook_pain_kategori_diatur(self):
        def ubah(n):
            n["product_id"] = fixture.PRODUK_DIATUR
            for b in n["beats"]:
                b["foto"] = min(b["foto"], 2)
        self.gagal(ubah, ov={"hook.tipe": "pain"}, pid=fixture.PRODUK_DIATUR, pesan="pain")


class Bantu(unittest.TestCase):
    def test_pembulatan_tidak_pernah_ke_atas(self):
        self.assertEqual(sf._ribuan_bawah(264454), "264rb+")
        self.assertEqual(sf._ribuan_bawah(9538), "9,5rb+")
        self.assertEqual(sf._ribuan_bawah(9999), "9,9rb+")
        self.assertEqual(sf._ribuan_bawah(830), "830")
        self.assertEqual(sf._ribuan_bawah(1_999_999), "1,9jt+")

    def test_angka_tampil(self):
        self.assertEqual(sf._angka_tampil("10RB+"), 10000)
        self.assertEqual(sf._angka_tampil("3,5RB+"), 3500)
        self.assertEqual(sf._angka_tampil("1JT+"), 1000000)
        self.assertIsNone(sf._angka_tampil("banyak"))

    def test_kontras(self):
        self.assertAlmostEqual(sf.kontras("#FFFFFF", "#000000"), 21.0, places=1)
        self.assertAlmostEqual(sf.kontras("#777777", "#777777"), 1.0)

    def test_palet_selalu_terbaca(self):
        with tempfile.TemporaryDirectory() as d:
            from PIL import Image
            for warna in [(255, 255, 255), (250, 210, 40), (20, 20, 20), (230, 40, 120)]:
                f = Path(d) / "c.jpg"
                Image.new("RGB", (200, 200), warna).save(f)
                pal = sf.palet(f)
                self.assertGreaterEqual(sf.kontras(pal["teks"], pal["latar"]), 4.5, warna)

    def test_kode_foto_turunkan_kualitas_sampai_muat(self):
        with tempfile.TemporaryDirectory() as d:
            from PIL import Image
            import random
            rnd = random.Random(1)
            f = Path(d) / "ramai.jpg"
            im = Image.new("RGB", (1024, 1024))
            im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)) for _ in range(1024 * 1024)])
            im.save(f, quality=95)
            params = {"foto.embed_total_maks_kb": 600, "foto.embed_sisi_panjang_px": 1024, "foto.embed_jpeg_kualitas": 80}
            out, info = sf.kode_foto([f], params)
            self.assertLessEqual(info["total_kb"], 600)
            self.assertTrue(info["kualitas"] < 80 or info["sisi_px"] < 1024, info)


class Template(Dasar):
    def test_tanpa_pola_nondeterministik(self):
        # pola yang sama dengan slate-studio renderer.NONDETERMINISTIC
        kode = re.sub(r"/\*.*?\*/|//[^\n]*", "", FILM.read_text(encoding="utf-8"), flags=re.S)
        for pola in (r"\bMath\.random\s*\(", r"\bDate\.now\s*\(", r"\bnew\s+Date\s*\(", r"\bperformance\.now\s*\(",
                     r"\bsetTimeout\s*\(", r"\bsetInterval\s*\(", r"\brequestAnimationFrame\s*\("):
            self.assertIsNone(re.search(pola, kode), pola)

    @unittest.skipUnless(shutil.which("node"), "node tidak ada")
    def test_sintaks_modul(self):
        with tempfile.TemporaryDirectory() as d:
            m = Path(d) / "film.mjs"
            shutil.copy(FILM, m)
            r = subprocess.run(["node", "--check", str(m)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_bahan_muat_batas_slate(self):
        isi, foto, _, _, _ = self.susun()
        total = len(json.dumps(isi, ensure_ascii=False).encode()) + len(json.dumps(foto).encode()) + FILM.stat().st_size
        self.assertLess(total, 2_000_000)     # renderer.prepare_workspace: maks 2 MB total

    @unittest.skipUnless(shutil.which(pratinjau.CHROMIUM) and pratinjau.FONTS.is_dir(), "chromium/font Slate tidak ada")
    def test_pratinjau_menggambar(self):
        isi, foto, _, _, _ = self.susun()
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "isi.json").write_text(json.dumps(isi), encoding="utf-8")
            (Path(d) / "foto.json").write_text(json.dumps(foto), encoding="utf-8")
            out = Path(d) / "f0.jpg"
            pratinjau.render(d, [0.0], out, skala=0.25, kol=1, label=False)
            from PIL import Image
            im = Image.open(out).convert("RGB")
            self.assertEqual(im.size, (270, 480))
            latar = sf._rgb(isi["palet"]["latar"])
            px = im.getpixel((5, 470))                       # pojok bawah = warna latar
            self.assertTrue(all(abs(a - b) <= 6 for a, b in zip(px, latar)), (px, latar))
            self.assertGreater(len(im.getcolors(maxcolors=1 << 16) or range(1 << 16)), 50)   # ada isi selain latar


if __name__ == "__main__":
    unittest.main()
