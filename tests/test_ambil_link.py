"""tools/ambil_link.py dengan lapisan CDP tiruan (tanpa jaringan, tanpa browser). Semua data produk karangan."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ambil_link  # noqa: E402
import fixture  # noqa: E402
import paket  # noqa: E402

SEKARANG = datetime(2026, 10, 22, 3, 0, tzinfo=timezone.utc)
URL = "https://shopee.co.id/Botol-Contoh-i.111.2000000001?sp_atk=x"
LINK = "https://s.shopee.co.id/ContohLink1"

DESKRIPSI = """Botol Minum Contoh 1 Liter

Keunggulan :
- Tahan panas dan dingin 12 jam
- Tutup anti bocor
✅ Bebas BPA
• Gratis ongkir se-Indonesia, order sekarang!

SPESIFIKASI
Ukuran: 8 x 25 cm
Bahan: Stainless steel 304
Warna: Hitam

Cara Pakai:
1. Cuci sebelum dipakai pertama kali
2. Jangan dimasukkan microwave

Pengiriman:
- Dikirim setiap hari kerja
"""


def item(**ubah):
    d = {
        "url_akhir": "https://shopee.co.id/product/111/2000000001",
        "ld": {"name": "Botol Minum Contoh", "price": "45000.00", "price_max": None, "seller": "Toko Contoh",
               "rating": "4.86", "rating_count": "1234"},
        "breadcrumb": ["Rumah & Taman", "Peralatan Dapur", "Botol Minum"],
        "item": {"item_id": "2000000001", "shop_id": "111",
                 "title": "[PROMO] Botol Minum Contoh 1 Liter Stainless Tahan Panas Dingin Anti Bocor Termos Kantor Sekolah",
                 "description": DESKRIPSI, "brand": "Contoh", "images": ["h1", "h2", "h3", "h4"], "has_video": False,
                 "categories": ["Rumah & Taman", "Peralatan Dapur", "Botol Minum"],
                 "tier_variations": [{"name": "Warna", "options": ["Hitam", "Putih"]}, {"name": "Model", "options": ["Std"]}],
                 "shop_location": "KOTA CONTOH", "is_official_shop": False, "is_preferred_plus_seller": True},
        "atribut": [{"name": "Stok", "value": "TERSEDIA"}, {"name": "Kapasitas", "value": "1L"}],
        "dom": {"harga": ["Rp45.000", "Rp60.000"], "terjual": "5RB+", "diskon": "-25%", "rating": "4.9",
                "penilaian": "1,2RB"},
    }
    for k, v in ubah.items():
        d[k].update(v) if isinstance(v, dict) else d.__setitem__(k, v)
    return d


class CdpPalsu:
    """Pengganti cdp_node: 'produk' menulis foto (PNG, agar konversi JPEG teruji), 'link' memberi link pendek."""

    def __init__(self, data=None, link=LINK, n_foto=4):
        self.data, self.link, self.n_foto, self.panggilan = data or item(), link, n_foto, []

    def __call__(self, perintah, *argumen):
        self.panggilan.append((perintah,) + argumen)
        if perintah == "produk":
            folder = Path(argumen[argumen.index("--gambar-ke") + 1])
            d = json.loads(json.dumps(self.data))
            d["foto"] = []
            for n in range(self.n_foto):
                Image.new("RGB", (1000, 1000), (40 * n, 90, 160)).save(folder / ("%02d.bin" % (n + 1)), "PNG")
                d["foto"].append({"url": "https://example.invalid/h%d" % (n + 1), "berkas": "%02d.bin" % (n + 1)})
            return d
        if perintah == "link":
            if self.link is None:
                raise ambil_link.AmbilError("CDP link: link tidak dibuat (failCode 1)")
            return {"link": self.link}
        raise AssertionError(perintah)


class Url(unittest.TestCase):
    def test_id_dari_url(self):
        self.assertEqual(ambil_link.id_dari_url(URL), ("111", "2000000001"))
        self.assertEqual(ambil_link.id_dari_url("https://shopee.co.id/product/5/6"), ("5", "6"))
        self.assertIsNone(ambil_link.id_dari_url("https://s.shopee.co.id/AbC"))

    def test_periksa_url(self):
        self.assertIsNone(ambil_link.periksa_url("https://s.shopee.co.id/AbC"))        # link pendek: id dibaca nanti
        for salah in ("https://contoh.invalid/x-i.1.2", "ftp://shopee.co.id/product/1/2", "https://shopee.co.id/flash_sale"):
            with self.assertRaises(ambil_link.AmbilError):
                ambil_link.periksa_url(salah)


class Teks(unittest.TestCase):
    def test_fitur_hanya_dari_teks_penjual(self):
        f = ambil_link.fitur_dari(DESKRIPSI, [{"name": "Kapasitas", "value": "1L"}], "Botol Minum Contoh 1 Liter")
        self.assertEqual(f[:3], ["Tahan panas dan dingin 12 jam", "Tutup anti bocor", "Bebas BPA"])
        self.assertIn("Ukuran: 8 x 25 cm", f)
        self.assertIn("Bahan: Stainless steel 304", f)
        self.assertLessEqual(len(f), 6)
        gabungan = " ".join(f).lower()
        for buang in ("ongkir", "microwave", "dikirim", "botol minum contoh 1 liter"):
            self.assertNotIn(buang, gabungan)

    def test_fitur_judul_berkurung_dan_isi_paket(self):
        d = "(Turbo 100 Putaran)\nPenjelasan panjang.\n\n(Layar Angka)\nPenjelasan.\n\nIsi Paket:\n- Kabel *1\n- Tali *1"
        f = ambil_link.fitur_dari(d)
        self.assertEqual(f[:2], ["Turbo 100 Putaran", "Layar Angka"])
        self.assertEqual(f[2:], ["Kabel *1", "Tali *1"])            # isi paket hanya pengisi

    def test_nama_dan_angka(self):
        self.assertEqual(ambil_link.nama_pendek("[PROMO] Botol Minum Contoh 1 Liter Stainless Tahan Panas Dingin Anti Bocor"),
                         "Botol Minum Contoh 1 Liter Stainless Tahan Panas Dingin Anti")
        self.assertEqual(ambil_link.nama_pendek("(HF) Keset Contoh Serap Air 40x60CM | Anti Slip Motif"),
                         "Keset Contoh Serap Air 40x60CM")
        self.assertEqual(ambil_link.angka_singkat("266,1RB"), 266100)
        self.assertEqual(ambil_link.angka_singkat("1,2JT"), 1200000)
        self.assertEqual(ambil_link.angka_rp("Rp26.900 - Rp34.900"), 26900)
        self.assertEqual(ambil_link.kategori_dari(["A", "B", "C"]), "A > C")

    def test_compliance(self):
        diatur = ["Perawatan & Kecantikan"]
        self.assertIn("Kategori diatur", ambil_link.catatan_compliance("Perawatan & Kecantikan > Lip", 10, diatur))
        self.assertIn("-87%", ambil_link.catatan_compliance("Elektronik > Kipas", 87, diatur))
        self.assertIsNone(ambil_link.catatan_compliance("Elektronik > Kipas", 20, diatur))


class Ambil(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def ambil(self, cdp, **kw):
        return ambil_link.ambil(URL, kw.pop("tanggal", "2099-01-01"), self.data, cdp=cdp, sekarang=SEKARANG, **kw)

    def test_paket_baru_lolos_validator(self):
        cdp = CdpPalsu()
        r = self.ambil(cdp)
        self.assertEqual((r["status"], r["product_id"], r["siap"], r["ditolak"]), ("ditambahkan", "2000000001", True, []))
        self.assertEqual(r["link"], LINK)
        self.assertEqual([c[0] for c in cdp.panggilan], ["produk", "link"])
        self.assertEqual(cdp.panggilan[0][1], "https://shopee.co.id/product/111/2000000001")   # URL kanonik, tanpa query
        hasil = paket.muat(self.data / "2099-01-01", sekarang=SEKARANG)
        p, ditolak, _ = hasil[0]
        self.assertEqual(ditolak, [])
        self.assertEqual(len(p["foto"]), 4)
        with Image.open(p["foto"][0]["path"]) as im:
            self.assertEqual(im.format, "JPEG")
        meta = json.loads((self.data / "2099-01-01/products/2000000001/meta.json").read_text())
        self.assertEqual((meta["price"], meta["price_before_discount"], meta["rating"], meta["reviews"]), (45000, 60000, 4.86, 1234))
        self.assertEqual(meta["category"], "Rumah & Taman > Botol Minum")
        self.assertEqual(meta["variants"], {"Warna": ["Hitam", "Putih"]})
        self.assertEqual((meta["shop_type"], meta["location"], meta["status"]), ("Star+", "Kota Contoh", "link_ready"))
        self.assertIsNone(meta["compliance_note"])
        self.assertEqual(meta["video_angle"]["hook"], meta["key_features"][0])
        self.assertTrue((self.data / "2099-01-01/products/shortlist.csv").exists())

    def test_tambah_ke_paket_lama_tanpa_mengubah_produk_lain(self):
        akar = fixture.buat(self.data / "2026-10-19")
        sebelum = json.loads((akar / "products/products.json").read_text())
        slim_sebelum = json.loads((akar / "products/manifest_slim.json").read_text())
        r = self.ambil(CdpPalsu(), tanggal="2026-10-19")
        self.assertEqual(r["status"], "ditambahkan")
        sesudah = json.loads((akar / "products/products.json").read_text())
        self.assertEqual(sesudah[:3], sebelum)
        self.assertEqual(sesudah[3]["rank"], 4)
        self.assertEqual(json.loads((akar / "products/manifest_slim.json").read_text())[:3], slim_sebelum)
        hasil = {p["id"]: d for p, d, _ in paket.muat(akar, sekarang=SEKARANG)}
        self.assertEqual(hasil["2000000001"], [])
        self.assertEqual(hasil[fixture.PRODUK_OK], [])

    def test_impor_zip_tanggal_sama_menggabung_produk(self):
        """Review R3 #7: tempel link dulu, lalu impor zip tanggal yang sama: produk zip ditambahkan (tidak dibuang),
        produk tempel link tetap, rank zip digeser ke belakang; impor ulang tidak menggandakan."""
        import impor_paket
        self.ambil(CdpPalsu(), tanggal="2026-10-19")
        sumber = fixture.buat(Path(self.tmp.name) / "zipsrc")
        (sumber / "products" / "shortlist.csv").write_text("rank,product_id,name\n1,%s,Keset\n" % fixture.PRODUK_OK)
        z = fixture.zip_dari(sumber, Path(self.tmp.name) / "affiliate_pipeline_data_2026-10-19.zip")
        r = impor_paket.impor(z, data=self.data)
        akar = self.data / "2026-10-19"
        semua = json.loads((akar / "products/products.json").read_text())
        self.assertEqual([str(p["product_id"]) for p in semua][0], "2000000001")
        self.assertEqual(len(semua), 4)
        self.assertEqual([p["rank"] for p in semua], [1, 2, 3, 4])
        slim = {str(x["product_id"]) for x in json.loads((akar / "products/manifest_slim.json").read_text())}
        self.assertEqual(len(slim), 4)
        self.assertIn(fixture.PRODUK_OK, (akar / "products/shortlist.csv").read_text())
        self.assertEqual(r["produk"], 4)
        impor_paket.impor(z, data=self.data)
        self.assertEqual(len(json.loads((akar / "products/products.json").read_text())), 4)

    def test_produk_sudah_ada_tidak_membuka_browser(self):
        self.ambil(CdpPalsu())
        cdp = CdpPalsu()
        r = self.ambil(cdp)
        self.assertEqual(r["status"], "sudah_ada")
        self.assertEqual(cdp.panggilan, [])

    def test_perbarui_mempertahankan_rank(self):
        akar = fixture.buat(self.data / "2026-10-19")
        self.ambil(CdpPalsu(), tanggal="2026-10-19")
        baru = item(ld={"price": "39000.00"})
        r = self.ambil(CdpPalsu(baru, n_foto=3), tanggal="2026-10-19", perbarui=True)
        self.assertEqual((r["status"], r["harga"], r["foto"]), ("diperbarui", 39000, 3))
        semua = json.loads((akar / "products/products.json").read_text())
        self.assertEqual(len(semua), 4)
        self.assertEqual(semua[3]["rank"], 4)
        self.assertEqual(len(list((akar / "products/2000000001/images").iterdir())), 3)

    def test_link_gagal_tidak_menulis_apa_pun(self):
        with self.assertRaises(ambil_link.AmbilError):
            self.ambil(CdpPalsu(link=None))
        self.assertFalse((self.data / "2099-01-01").exists())

    def test_link_bukan_shopee_ditolak(self):
        with self.assertRaises(ambil_link.AmbilError):
            self.ambil(CdpPalsu(link="https://contoh.invalid/x"))

    def test_link_manual_melewati_custom_link(self):
        cdp = CdpPalsu()
        r = self.ambil(cdp, link="https://s.shopee.co.id/Manual1")
        self.assertEqual([c[0] for c in cdp.panggilan], ["produk"])
        self.assertEqual(r["link"], "https://s.shopee.co.id/Manual1")

    def test_kategori_diatur_dan_diskon_besar(self):
        d = item(item={"categories": ["Perawatan & Kecantikan", "Bibir"]}, dom={"diskon": "-80%"})
        r = self.ambil(CdpPalsu(d))
        self.assertIn("Kategori diatur", r["compliance_note"])
        self.assertIn("-80%", r["compliance_note"])
        self.assertTrue(any("kategori diatur" in w for w in r["peringatan"]))

    def test_foto_kurang_ditolak_validator(self):
        r = self.ambil(CdpPalsu(n_foto=2))
        self.assertFalse(r["siap"])
        self.assertTrue(any("foto lokal 2" in m for m in r["ditolak"]))

    def test_link_pendek_dibaca_dari_halaman(self):
        cdp = CdpPalsu()
        r = ambil_link.ambil("https://s.shopee.co.id/AbC123", "2099-01-01", self.data, cdp=cdp, sekarang=SEKARANG)
        self.assertEqual(cdp.panggilan[0][1], "https://s.shopee.co.id/AbC123")
        self.assertEqual(cdp.panggilan[1], ("link", "https://shopee.co.id/product/111/2000000001"))
        self.assertEqual(r["product_id"], "2000000001")

    def test_cli_url_salah(self):
        out = io.StringIO()
        with redirect_stdout(out):
            kode = ambil_link.main(["https://contoh.invalid/x", "--data", str(self.data)])
        self.assertEqual(kode, 1)
        self.assertIn("bukan link produk Shopee", json.loads(out.getvalue())["error"])


if __name__ == "__main__":
    unittest.main()


class IdHalaman(unittest.TestCase):
    """Review 22 Okt #6: id dari halaman dipakai sebagai nama folder; divalidasi sebelum apa pun ditulis."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data"

    def tearDown(self):
        self.tmp.cleanup()

    def gagal(self, data, url, pesan):
        with self.assertRaises(ambil_link.AmbilError) as c:
            ambil_link.ambil(url, "2099-01-01", self.data, cdp=CdpPalsu(data))
        self.assertIn(pesan, str(c.exception))
        self.assertFalse((self.data / "2099-01-01").exists())                  # tidak ada yang ditulis
        self.assertFalse(any(Path(self.tmp.name).rglob("meta.json")))

    def test_item_id_berbahaya_lewat_link_pendek(self):
        d = item(item={"item_id": "../../../x"}, url_akhir="https://shopee.co.id/product/111/2000000001")
        self.gagal(d, "https://s.shopee.co.id/AbC123", "tidak valid")

    def test_id_halaman_beda_dengan_url(self):
        d = item(item={"item_id": "2000000009"}, url_akhir="https://shopee.co.id/product/111/2000000009")
        self.gagal(d, URL, "produk lain")

    def test_halaman_akhir_bukan_shopee(self):
        self.gagal(item(url_akhir="https://contoh.invalid/product/111/2000000001"), "https://s.shopee.co.id/AbC123", "bukan shopee")
        self.gagal(item(url_akhir="https://shopee.co.id/product/111/2000000777"), "https://s.shopee.co.id/AbC123", "tidak sama")
