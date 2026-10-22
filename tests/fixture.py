"""Paket data tiruan (disamarkan) untuk tes: struktur sama dengan paket sesi Chrome, isi karangan, foto dibuat PIL."""
import json
import zipfile
from pathlib import Path

from PIL import Image

PRODUK_OK = "1000000001"
PRODUK_RUSAK = "1000000002"
PRODUK_DIATUR = "1000000003"


def _meta(pid, rank, nama, kategori, n_foto, link="https://s.shopee.co.id/ABCdef123", hook="Lantai basah jadi kering?"):
    return {
        "rank": rank, "product_id": pid, "shop_id": "1", "name": nama, "category": kategori,
        "price": 25000, "price_before_discount": 90000, "commission_rate": 10.0, "sold_30d": "10RB+",
        "rating": 4.8, "reviews": 9538, "shop_name": "Toko Contoh", "shop_type": "Mall", "has_video": False,
        "variants": {"Warna": ["Abu", "Biru"]},
        "key_features": ["Daya serap air tinggi", "Cepat kering", "Alas anti-slip", "Ukuran 40x60cm"],
        "video_angle": {"hook": hook, "pain_point": "Lantai licin", "usp": [], "cta": "Cek di link"},
        "score": {"total": 80.0}, "cover": "https://example.invalid/%s_1" % pid,
        "images": [{"url": "https://example.invalid/%s_%d" % (pid, n + 1), "local": "%s_%02d.jpg" % (pid, n + 1)}
                   for n in range(n_foto)],
        "url": "https://shopee.co.id/product/1/%s" % pid, "affiliate_link": link,
        "scraped_at": "2026-10-19T16:00:00Z", "status": "link_ready",
    }


def buat(akar, foto=True, ukuran=1024):
    akar = Path(akar)
    produk = [
        _meta(PRODUK_OK, 1, "Keset Contoh Serap Air", "Perlengkapan Rumah", 4, hook="Air hilang dalam 3 detik?"),
        _meta(PRODUK_RUSAK, 2, "Produk Rusak", "Perlengkapan Rumah", 1, link="https://contoh.invalid/x"),
        _meta(PRODUK_DIATUR, 3, "Lip Balm Contoh", "Perawatan & Kecantikan > Treatment Bibir", 3),
    ]
    (akar / "products").mkdir(parents=True)
    (akar / "products" / "products.json").write_text(json.dumps(produk), encoding="utf-8")
    slim = [{"product_id": p["product_id"], "compliance_note": None,
             "image_files": [i["local"] for i in p["images"]]} for p in produk]
    slim[0]["compliance_note"] = "Jangan tonjolkan persen diskon."
    (akar / "products" / "manifest_slim.json").write_text(json.dumps(slim), encoding="utf-8")
    warna = [(200, 60, 40), (40, 120, 200), (230, 230, 230), (60, 160, 90)]
    for p in produk:
        d = akar / "products" / p["product_id"] / "images"
        d.mkdir(parents=True)
        if not foto:
            continue
        for n, i in enumerate(p["images"]):
            sisi = 600 if (p["product_id"] == PRODUK_OK and n == 3) else ukuran
            Image.new("RGB", (sisi, sisi), warna[n % len(warna)]).save(d / i["local"], quality=90)
    return akar


def zip_dari(folder, tujuan):
    folder = Path(folder)
    with zipfile.ZipFile(tujuan, "w") as z:
        for f in folder.rglob("*"):
            z.write(f, f.relative_to(folder))
    return tujuan


NASKAH_OK = {
    "product_id": PRODUK_OK, "hook_layar": "Keset ini nyerap air?", "cta_layar": "Cek di bawah", "hook_tipe": "demo",
    "beats": [
        {"tipe": "hook", "vo": "Keset ini *nyerap air*?", "foto": 0, "fokus": [0.5, 0.5], "sumber": ["fitur:0"]},
        {"tipe": "masalah", "vo": "Keluar kamar mandi, lantainya *licin*?", "teks_kunci": "Lantai licin?", "foto": 1,
         "fokus": [0.3, 0.3], "sumber": ["masalah"]},
        {"tipe": "produk", "vo": "Ini keset contoh *serap air*.", "teks_kunci": "Keset serap air", "foto": 0,
         "sumber": ["nama"]},
        {"tipe": "fitur", "vo": "Daya serapnya tinggi, dan *cepat kering*.", "teks_kunci": "Cepat kering", "foto": 2,
         "sumber": ["fitur:0", "fitur:1"]},
        {"tipe": "fitur", "vo": "Alasnya *anti-slip*, nggak gampang geser.", "teks_kunci": "Anti-slip", "foto": 3,
         "sumber": ["fitur:2"]},
        {"tipe": "bukti", "vo": "Sebulan terjual *sepuluh ribu lebih*.", "foto": 1, "sumber": ["terjual", "rating"]},
        {"tipe": "cta", "vo": "Warnanya ada dua, cek *di bawah* ya.", "foto": 0, "sumber": ["varian", "ajakan"]},
    ],
}
