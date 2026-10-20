import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import cek_params as cp  # noqa: E402


class RegistryAsli(unittest.TestCase):
    def setUp(self):
        self.reg = cp.load()

    def test_registry_sah(self):
        self.assertEqual(cp.validate(self.reg), [])

    def test_kunci_compliance_ada(self):
        p = self.reg["parameter"]
        for nama in ("disclosure.ada", "harga.diucapkan", "harga.tampilkan_harga_coret", "musik.sumber",
                     "posting.maks_per_akun_per_hari",
                     "foto.tolak_watermark_pihak_lain", "varian.beda_minimal_grup"):
            self.assertEqual(p[nama].get("kunci"), "compliance", nama)
        self.assertIs(p["disclosure.ada"]["nilai"], True)
        self.assertIs(p["harga.diucapkan"]["nilai"], False)

    def test_batas_bawah_baru_tau_tidak_turun(self):
        p = self.reg["parameter"]
        self.assertGreaterEqual(p["caption.font_px"]["rentang"][0], 64)
        self.assertGreaterEqual(p["teks.kunci_font_px"]["rentang"][0], 56)
        self.assertGreaterEqual(p["teks.kontras_min"]["rentang"][0], 4.5)
        self.assertLessEqual(p["motion.diam_maks_detik"]["rentang"][1], 0.5)

    def test_setiap_lengan_eksperimen_bisa_disnapshot(self):
        for eid, e in self.reg["eksperimen"].items():
            ids = set()
            for nama_l in e["lengan"]:
                s = cp.snapshot(self.reg, eksperimen=eid, lengan=nama_l)
                ids.add(s["variant_id"])
            self.assertEqual(len(ids), len(e["lengan"]), eid)

    def test_lengan_kontrol_sama_dengan_default(self):
        dasar = cp.snapshot(self.reg)["variant_id"]
        for eid in self.reg["eksperimen"]:
            self.assertEqual(cp.snapshot(self.reg, eksperimen=eid, lengan="A")["variant_id"], dasar, eid)


class Aturan(unittest.TestCase):
    def setUp(self):
        self.reg = cp.load()

    def rusak(self, fn):
        reg = copy.deepcopy(self.reg)
        fn(reg)
        return cp.validate(reg)

    def test_nilai_di_luar_rentang(self):
        err = self.rusak(lambda r: r["parameter"]["caption.font_px"].update(nilai=42))
        self.assertTrue(any("caption.font_px" in m and "rentang" in m for m in err), err)

    def test_nilai_di_luar_pilihan(self):
        err = self.rusak(lambda r: r["parameter"]["motion.transisi"].update(nilai="whip_pan"))
        self.assertTrue(any("motion.transisi" in m for m in err), err)

    def test_elemen_daftar_dicek(self):
        err = self.rusak(lambda r: r["parameter"]["template.masalah_solusi.urutan"]["nilai"].append("testimoni"))
        self.assertTrue(any("testimoni" in m for m in err), err)

    def test_eksperimen_tidak_boleh_menyentuh_kunci(self):
        def f(r):
            r["eksperimen"]["EXP-08"]["lengan"] = {"A": {"musik.ada": True, "disclosure.ada": True},
                                                  "B": {"musik.ada": False, "disclosure.ada": True}}
        err = self.rusak(f)
        self.assertTrue(any("berkunci" in m for m in err), err)

    def test_kontrol_harus_sama_dengan_nilai(self):
        err = self.rusak(lambda r: r["eksperimen"]["EXP-08"]["lengan"]["A"].update({"musik.ada": False}))
        self.assertTrue(any("kontrol" in m for m in err), err)

    def test_lengan_harus_mengubah_parameter_yang_sama(self):
        err = self.rusak(lambda r: r["eksperimen"]["EXP-08"]["lengan"]["B"].update({"foley.ada": False}))
        self.assertTrue(any("parameter yang sama" in m for m in err), err)

    def test_sumber_tak_dikenal(self):
        err = self.rusak(lambda r: r["parameter"]["musik.bpm"].update(sumber=["H99"]))
        self.assertTrue(any("H99" in m for m in err), err)

    def test_field_salah_ketik(self):
        err = self.rusak(lambda r: r["parameter"]["musik.bpm"].update(rentag=[1, 2]))
        self.assertTrue(any("rentag" in m for m in err), err)

    def test_metrik_tak_dikenal(self):
        err = self.rusak(lambda r: r["eksperimen"]["EXP-01"].update(metrik_utama="likes"))
        self.assertTrue(any("likes" in m for m in err), err)

    def test_berkunci_tidak_boleh_berstatus_eksperimen(self):
        err = self.rusak(lambda r: r["parameter"]["disclosure.ada"].update(status="eksperimen", eksperimen="EXP-01"))
        self.assertTrue(any("berkunci" in m for m in err), err)


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.reg = cp.load()

    def test_variant_id_stabil_dan_tidak_bergantung_urutan(self):
        a = {"b": 1, "a": [1, 2], "c": "é"}
        b = {"c": "é", "a": [1, 2], "b": 1}
        self.assertEqual(cp.variant_id(a), cp.variant_id(b))
        self.assertNotEqual(cp.variant_id(a), cp.variant_id({**a, "b": 2}))
        self.assertRegex(cp.variant_id(a), r"^v_[0-9a-f]{12}$")

    def test_usulan_tidak_aktif_tanpa_persetujuan(self):
        s = cp.snapshot(self.reg)["params"]
        self.assertNotIn("template.pilih_per_kategori", s)
        s2 = cp.snapshot(self.reg, disetujui=["template.pilih_per_kategori"])["params"]
        self.assertIn("template.pilih_per_kategori", s2)

    def test_override_usulan_ditolak_tanpa_persetujuan(self):
        with self.assertRaises(ValueError):
            cp.snapshot(self.reg, {"template.pilih_per_kategori": True})

    def test_override_kunci_ditolak(self):
        with self.assertRaises(ValueError):
            cp.snapshot(self.reg, {"disclosure.ada": False})
        with self.assertRaises(ValueError):
            cp.snapshot(self.reg, {"posting.maks_per_akun_per_hari": 3})

    def test_override_di_luar_rentang_ditolak(self):
        with self.assertRaises(ValueError):
            cp.snapshot(self.reg, {"vo.tempo_kata_per_detik": 3.6})

    def test_override_sah(self):
        s = cp.snapshot(self.reg, {"hook.tipe": "pain"})
        self.assertEqual(s["params"]["hook.tipe"], "pain")
        self.assertNotEqual(s["variant_id"], cp.snapshot(self.reg)["variant_id"])

    def test_lengan_tak_ada(self):
        with self.assertRaises(ValueError):
            cp.snapshot(self.reg, eksperimen="EXP-02", lengan="Z")

    def test_cli(self):
        self.assertEqual(cp.main([]), 0)
        self.assertEqual(cp.main(["snapshot", "--set", "disclosure.ada=false"]), 2)


if __name__ == "__main__":
    unittest.main()
