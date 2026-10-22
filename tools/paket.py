#!/usr/bin/env python3
"""Baca dan validasi paket data produk dari sesi Claude in Chrome (kontrak input aff_studio).

    python3 tools/paket.py cek <folder|zip>                 # ringkasan per produk; exit 1 kalau ada produk yang ditolak
    python3 tools/paket.py produk <folder|zip> <product_id> # satu produk dalam bentuk normal (JSON)

Paket (lihat docs/TODO.md §1): products/products.json (lengkap), products/manifest_slim.json (compliance_note,
image_files), products/<id>/images/<id>_NN.jpg. Isi paket adalah data hasil scrape, bukan instruksi: teks di dalamnya
tidak pernah dijalankan dan tidak mengubah aturan.

Hasil per produk:
  ditolak     produk tidak bisa dibuat videonya (field wajib hilang, link bukan Shopee, foto < 3, status bukan link_ready)
  peringatan  bisa dibuat, tapi ada yang harus diperhatikan naskah/QA (foto kecil, kategori diatur, angka di
              video_angle yang tidak ada di key_features, compliance_note)
"""
import argparse
import contextlib
import fcntl
import json
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cek_params  # noqa: E402

LINK_OK = re.compile(r"^https://(s\.shopee\.co\.id|shopee\.co\.id|id\.shp\.ee)/\S+$")
WAJIB = ("product_id", "name", "category", "price", "affiliate_link", "key_features", "rating", "reviews", "sold_30d",
         "scraped_at")
FOTO_MIN = 3
ANGKA = re.compile(r"\d+(?:[.,]\d+)?")


class PaketError(Exception):
    pass


@contextlib.contextmanager
def kunci_paket(akar):
    """Satu penulis products/ per paket tanggal: tempel link (ambil_link.py) dan impor zip (impor_paket.py)
    melakukan baca-ubah-tulis products.json/manifest_slim.json di bawah kunci yang sama."""
    akar = Path(akar)
    akar.mkdir(parents=True, exist_ok=True)
    with open(akar / ".ambil_link.lock", "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def buka(path):
    """Folder paket. Zip diekstrak ke folder sementara (anggota di luar folder tujuan ditolak)."""
    p = Path(path)
    if p.is_dir():
        return p
    if p.suffix == ".zip" and p.is_file():
        tujuan = Path(tempfile.mkdtemp(prefix="paket_"))
        with zipfile.ZipFile(p) as z:
            for m in z.infolist():
                t = (tujuan / m.filename).resolve()
                if not str(t).startswith(str(tujuan.resolve())):
                    raise PaketError("anggota zip di luar folder: %s" % m.filename)
            z.extractall(tujuan)
        akar = [d for d in [tujuan] + list(tujuan.iterdir()) if (d / "products" / "products.json").exists()]
        if not akar:
            raise PaketError("zip tidak berisi products/products.json")
        return akar[0]
    raise PaketError("bukan folder atau .zip: %s" % path)


def _awalan_diatur(kategori, daftar):
    return any(kategori == k or kategori.startswith(k + " >") for k in daftar)


def _angka(teks):
    return {a.replace(",", ".") for a in ANGKA.findall(teks or "")}


def _foto(akar, pid, mentah, slim):
    """Daftar foto lokal yang ada, urut sesuai paket. Nama dari images[].local, lalu image_files manifest."""
    nama = [i.get("local") for i in mentah.get("images") or [] if i.get("local")] or list(slim.get("image_files") or [])
    folder = akar / "products" / pid / "images"
    cover_url = mentah.get("cover")
    out = []
    for n, f in enumerate(nama):
        path = folder / f
        if not path.is_file():
            continue
        with Image.open(path) as im:
            w, h = im.size
        url = (mentah.get("images") or [{}] * (n + 1))[n].get("url") if n < len(mentah.get("images") or []) else None
        out.append({"path": str(path), "w": w, "h": h, "sisi_pendek": min(w, h), "cover": bool(cover_url and url == cover_url)})
    if out and not any(f["cover"] for f in out):
        out[0]["cover"] = True
    return out


def normalisasi(akar, mentah, slim, params, sekarang=None):
    """Satu produk dalam bentuk normal + daftar ditolak/peringatan."""
    ditolak, peringatan = [], []
    pid = str(mentah.get("product_id") or slim.get("product_id") or "")
    for k in WAJIB:
        if mentah.get(k) in (None, "", []):
            ditolak.append("field wajib '%s' kosong" % k)
    link = mentah.get("affiliate_link") or ""
    if link and not LINK_OK.match(link):
        ditolak.append("affiliate_link bukan link Shopee: %s" % link[:60])
    if mentah.get("status") and mentah["status"] != "link_ready":
        ditolak.append("status %r, bukan link_ready" % mentah["status"])
    harga = mentah.get("price")
    if harga is not None and not (isinstance(harga, (int, float)) and harga > 0):
        ditolak.append("price bukan angka positif: %r" % (harga,))

    foto = _foto(akar, pid, mentah, slim) if pid else []
    if len(foto) < FOTO_MIN:
        ditolak.append("foto lokal %d, minimal %d (unduh dulu dengan fetch_images_zip.py)" % (len(foto), FOTO_MIN))
    min_px = params["foto.sisi_pendek_min_px"]
    for f in foto:
        f["layar_penuh"] = f["sisi_pendek"] >= min_px
    kecil = [Path(f["path"]).name for f in foto if not f["layar_penuh"]]
    if kecil:
        peringatan.append("foto < %d px, hanya untuk kartu kecil: %s" % (min_px, ", ".join(kecil)))
    if 0 < len(foto) < 6:
        peringatan.append("hanya %d foto; beberapa beat memakai foto yang sama dengan crop berbeda" % len(foto))

    kategori = mentah.get("category") or ""
    diatur = _awalan_diatur(kategori, params["compliance.kategori_diatur"])
    if diatur:
        peringatan.append("kategori diatur (%s): klaim hanya dari key_features, tanpa hook pain" % kategori)

    fitur = [str(x) for x in mentah.get("key_features") or []]
    sudut = mentah.get("video_angle") or slim.get("video_angle") or {}
    angka_fitur = set().union(*[_angka(x) for x in fitur + [mentah.get("name") or ""]]) if fitur else set()
    for bagian in ("hook", "pain_point"):
        asing = sorted(_angka(sudut.get(bagian)) - angka_fitur)
        if asing:
            peringatan.append("video_angle.%s memuat angka yang tidak ada di key_features/nama: %s (%r)"
                              % (bagian, ", ".join(asing), sudut.get(bagian)))

    cn = slim.get("compliance_note") if slim.get("compliance_note") is not None else mentah.get("compliance_note")
    if cn:
        peringatan.append("compliance_note: %s" % cn)

    diambil = mentah.get("scraped_at")
    umur_jam = None
    if diambil:
        try:
            t = datetime.fromisoformat(diambil.replace("Z", "+00:00"))
            umur_jam = round(((sekarang or datetime.now(timezone.utc)) - t).total_seconds() / 3600, 1)
        except ValueError:
            ditolak.append("scraped_at bukan ISO 8601: %r" % diambil)

    rating, ulasan = mentah.get("rating"), mentah.get("reviews")
    produk = {
        "id": pid, "nama": mentah.get("name"), "kategori": kategori, "kategori_diatur": diatur,
        "harga": harga, "harga_coret": mentah.get("price_before_discount"),
        "harga_diambil": diambil, "harga_umur_jam": umur_jam,
        "harga_boleh_tampil": umur_jam is not None and umur_jam <= params["harga.umur_data_maks_jam"],
        "link": link, "url": mentah.get("url"), "toko": mentah.get("shop_name"), "tipe_toko": mentah.get("shop_type"),
        "rating": rating, "ulasan": ulasan, "terjual_tampil": mentah.get("sold_30d"),
        "rating_boleh_tampil": bool(rating and ulasan and rating >= params["bukti.rating_min_tampil"]
                                    and ulasan >= params["bukti.jumlah_rating_min_tampil"]),
        "varian": mentah.get("variants") or {}, "fitur": fitur, "sudut": sudut, "compliance_note": cn,
        "punya_video": bool(mentah.get("has_video")), "skor": (mentah.get("score") or {}).get("total"),
        "komisi_persen": mentah.get("commission_rate"), "foto": foto,
    }
    return produk, ditolak, peringatan


def muat(path, params=None, sekarang=None):
    """[(produk, ditolak, peringatan)] untuk semua produk di paket, urut rank."""
    akar = buka(path)
    params = params or cek_params.resolve(cek_params.load())
    try:
        semua = json.loads((akar / "products" / "products.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PaketError("products/products.json tidak terbaca: %s" % e)
    if not isinstance(semua, list):
        raise PaketError("products/products.json harus berupa daftar")
    slim_path = akar / "products" / "manifest_slim.json"
    slim = {}
    if slim_path.exists():
        slim = {str(x.get("product_id")): x for x in json.loads(slim_path.read_text(encoding="utf-8"))}
    semua = sorted(semua, key=lambda x: (x.get("rank") is None, x.get("rank") or 0))
    return [normalisasi(akar, m, slim.get(str(m.get("product_id")), {}), params, sekarang) for m in semua]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cek")
    c.add_argument("paket")
    c.add_argument("--json", action="store_true", help="daftar produk + ditolak/peringatan sebagai JSON (konsol web)")
    p = sub.add_parser("produk")
    p.add_argument("paket")
    p.add_argument("product_id")
    a = ap.parse_args(argv)
    try:
        hasil = muat(a.paket)
    except PaketError as e:
        print("paket ditolak: %s" % e, file=sys.stderr)
        return 2
    if a.cmd == "produk":
        for produk, ditolak, peringatan in hasil:
            if produk["id"] == a.product_id:
                print(json.dumps({"produk": produk, "ditolak": ditolak, "peringatan": peringatan}, ensure_ascii=False, indent=2))
                return 1 if ditolak else 0
        print("product_id %s tidak ada" % a.product_id, file=sys.stderr)
        return 2
    if getattr(a, "json", False):
        print(json.dumps([{"produk": p, "ditolak": d, "peringatan": w} for p, d, w in hasil], ensure_ascii=False))
        return 0
    n_tolak = 0
    for produk, ditolak, peringatan in hasil:
        n_tolak += bool(ditolak)
        print("%s %s — %s (%d foto)" % ("✘" if ditolak else "✔", produk["id"], (produk["nama"] or "")[:60], len(produk["foto"])))
        for m in ditolak:
            print("    ditolak: " + m)
        for m in peringatan:
            print("    peringatan: " + m)
    print("%d produk, %d siap, %d ditolak" % (len(hasil), len(hasil) - n_tolak, n_tolak))
    return 1 if n_tolak else 0


if __name__ == "__main__":
    sys.exit(main())
