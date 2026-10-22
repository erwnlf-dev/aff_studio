#!/usr/bin/env python3
"""Impor paket data dari sesi Claude in Chrome ke folder data aff_studio (dipakai konsol web, tombol "Impor").

    python3 tools/impor_paket.py daftar [--data /data/apps/affiliate-data] [--cari /data/apps]   zip yang bisa diimpor (JSON)
    python3 tools/impor_paket.py impor <zip> [--data …] [--unduh-gambar]                         → <data>/<tanggal>/ (JSON)

Nama folder tujuan = tanggal di nama zip (affiliate_pipeline_data_2026-10-19.zip → 2026-10-19); paket yang sudah ada
tidak ditimpa (berkas lama dipertahankan, hanya yang belum ada yang ditambahkan). Daftar produk (products.json,
manifest_slim.json, shortlist.csv) yang sudah ada, mis. dari "Tempel link" untuk tanggal yang sama, DIGABUNG: produk zip
yang belum ada ditambahkan di belakang (rank setelah produk lama), produk yang sudah ada tidak diubah. Impor memegang
kunci paket yang sama dengan tempel link (paket.kunci_paket). Anggota zip di luar folder tujuan
ditolak. Kalau foto produk tidak ikut di zip, --unduh-gambar menjalankan fetch_images_zip.py milik paket itu (gambar
dari CDN Shopee, jeda 1,5–3,5 s per file) lalu membongkar hasilnya ke products/<id>/images/. Tanpa --unduh-gambar,
produk tanpa foto ditolak validator (tools/paket.py).
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paket  # noqa: E402

DATA = Path("/data/apps/affiliate-data")
CARI = [Path("/data/apps")]
POLA = re.compile(r"affiliate_pipeline_data_(\d{4}-\d{2}-\d{2})(?:[_-][\w-]+)?\.zip$")


def tanggal(zip_path):
    m = POLA.search(Path(zip_path).name)
    if not m:
        raise paket.PaketError("nama zip harus affiliate_pipeline_data_<YYYY-MM-DD>.zip: %s" % Path(zip_path).name)
    return m.group(1)


def daftar(data=DATA, cari=CARI):
    out = []
    for d in cari + [data]:
        for z in sorted(Path(d).glob("affiliate_pipeline_data_*.zip")):
            try:
                tgl = tanggal(z)
            except paket.PaketError:
                continue
            out.append({"zip": str(z), "tanggal": tgl, "ukuran_kb": round(z.stat().st_size / 1024),
                        "sudah_diimpor": (Path(data) / tgl / "products" / "products.json").exists()})
    return out


DAFTAR = ("products/products.json", "products/manifest_slim.json", "products/shortlist.csv")


def _daftar_json(teks, nama):
    try:
        d = json.loads(teks)
    except ValueError as e:
        raise paket.PaketError("%s tidak terbaca: %s" % (nama, e))
    if not isinstance(d, list) or not all(isinstance(x, dict) for x in d):
        raise paket.PaketError("%s harus daftar objek produk" % nama)
    return d


def _tulis_atomik(path, teks):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(teks, encoding="utf-8")
    os.replace(tmp, path)


def _rank(p):
    r = p.get("rank")
    return r if isinstance(r, int) and not isinstance(r, bool) else None


def _csv(teks, nama):
    try:
        r = csv.DictReader(io.StringIO(teks))
        return list(r.fieldnames or []), list(r)
    except csv.Error as e:
        raise paket.PaketError("%s tidak terbaca: %s" % (nama, e))


def gabung_daftar(tujuan, z):
    """products.json/manifest_slim.json/shortlist.csv yang sudah ada + produk zip yang belum ada. Rank produk zip
    digeser ke belakang produk lama (urutan zip dipertahankan). SEMUA berkas (paket dan zip) dibaca dan diperiksa
    dulu; baru setelah itu ditulis, masing-masing atomik (berkas rusak = tidak ada yang berubah). Mengembalikan jumlah
    produk yang ditambahkan."""
    prod = Path(tujuan) / "products"
    nama = set(z.namelist())
    lama = _daftar_json((prod / "products.json").read_text(encoding="utf-8"), "products.json paket")
    zip_ = _daftar_json(z.read("products/products.json").decode("utf-8"), "products.json zip")
    sj, sl = prod / "manifest_slim.json", prod / "shortlist.csv"
    slim = slim_zip = isi = baris_zip = None
    if "products/manifest_slim.json" in nama:
        slim_zip = _daftar_json(z.read("products/manifest_slim.json").decode("utf-8"), "manifest_slim.json zip")
        slim = _daftar_json(sj.read_text(encoding="utf-8"), "manifest_slim.json paket") if sj.exists() else []
    if "products/shortlist.csv" in nama:
        kolom_zip, baris_zip = _csv(z.read("products/shortlist.csv").decode("utf-8"), "shortlist.csv zip")
        kolom, isi = _csv(sl.read_text(encoding="utf-8"), "shortlist.csv paket") if sl.exists() else (kolom_zip, [])
        kolom = kolom or kolom_zip

    ada = {str(p.get("product_id")) for p in lama}
    geser = max([_rank(p) or 0 for p in lama] + [0])
    tambah = [p for p in sorted(zip_, key=lambda x: (_rank(x) is None, _rank(x) or 0))
              if str(p.get("product_id")) not in ada]
    rank = {}
    for n, p in enumerate(tambah, 1):
        p["rank"] = rank[str(p.get("product_id"))] = geser + n
    tulis = [(prod / "products.json", json.dumps(lama + tambah, ensure_ascii=False, indent=2) + "\n")]
    if slim_zip is not None:
        slim_zip = [dict(s, rank=rank[str(s.get("product_id"))]) if "rank" in s else s
                    for s in slim_zip if str(s.get("product_id")) in rank]
        slim = [s for s in slim if str(s.get("product_id")) not in rank]     # sisa impor yang terhenti: diganti
        tulis.append((sj, json.dumps(slim + slim_zip, ensure_ascii=False, indent=2) + "\n"))
    if baris_zip is not None:
        baris_zip = [dict(b, rank=rank[b["product_id"]]) if "rank" in b else b
                     for b in baris_zip if b.get("product_id") in rank]
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=kolom, extrasaction="ignore")
        w.writeheader()
        w.writerows([b for b in isi if b.get("product_id") not in rank] + baris_zip)
        tulis.append((sl, out.getvalue()))
    # products.json terakhir: kalau penulisan berhenti di tengah, impor ulang masih melihat produk zip sebagai
    # belum ada lalu menulis ulang daftar pendamping dari awal (manifest/shortlist difilter per product_id baru)
    for path, teks in tulis[1:] + tulis[:1]:
        _tulis_atomik(path, teks)
    return len(tambah)


def bongkar(zip_path, tujuan):
    """Bongkar aman: anggota di luar tujuan ditolak; berkas yang sudah ada tidak ditimpa, kecuali daftar produk
    (DAFTAR) yang digabung. Pemanggil memegang paket.kunci_paket(tujuan)."""
    tujuan = Path(tujuan).resolve()
    baru = 0
    with zipfile.ZipFile(zip_path) as z:
        for m in z.infolist():
            t = (tujuan / m.filename).resolve()
            if not str(t).startswith(str(tujuan) + "/") and t != tujuan:
                raise paket.PaketError("anggota zip di luar folder: %s" % m.filename)
        if "products/products.json" in z.namelist() and (tujuan / "products" / "products.json").exists():
            baru += gabung_daftar(tujuan, z)            # sebelum berkas lain, supaya galat bentuk tidak setengah jalan
            lewati = set(DAFTAR)
        else:
            lewati = set()
        for m in z.infolist():
            t = tujuan / m.filename
            if m.filename in lewati:
                continue
            if m.is_dir():
                t.mkdir(parents=True, exist_ok=True)
            elif not t.exists():
                t.parent.mkdir(parents=True, exist_ok=True)
                with z.open(m) as src, open(t, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                baru += 1
    return baru


def foto_kurang(tujuan):
    semua = json.loads((Path(tujuan) / "products" / "products.json").read_text(encoding="utf-8"))
    kurang = []
    for p in semua:
        for i in p.get("images") or []:
            if not (Path(tujuan) / "products" / str(p["product_id"]) / "images" / i.get("local", "")).exists():
                kurang.append(p["product_id"])
                break
    return kurang


def unduh_gambar(tujuan):
    """fetch_images_zip.py milik paket (dari sesi Chrome) → affiliate_assets_<tgl>.zip → products/<id>/images/."""
    tujuan = Path(tujuan)
    skrip = tujuan / "fetch_images_zip.py"
    if not skrip.exists():
        raise paket.PaketError("paket tidak membawa fetch_images_zip.py")
    sebelum = set(tujuan.glob("affiliate_assets_*.zip"))
    r = subprocess.run([sys.executable, "-I", str(skrip), "products/products.json"], cwd=tujuan, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise paket.PaketError("fetch_images_zip.py gagal: %s" % r.stderr[-300:])
    hasil = sorted(set(tujuan.glob("affiliate_assets_*.zip")) - sebelum) or sorted(tujuan.glob("affiliate_assets_*.zip"))
    if not hasil:
        raise paket.PaketError("fetch_images_zip.py tidak menghasilkan zip gambar")
    n = 0
    with zipfile.ZipFile(hasil[-1]) as z:
        for m in z.infolist():
            if not m.filename.endswith(".jpg"):
                continue
            t = (tujuan / "products" / m.filename).resolve()
            if not str(t).startswith(str((tujuan / "products").resolve()) + "/"):
                raise paket.PaketError("anggota zip gambar di luar folder: %s" % m.filename)
            if not t.exists():
                t.parent.mkdir(parents=True, exist_ok=True)
                t.write_bytes(z.read(m))
                n += 1
    return n


def impor(zip_path, data=DATA, unduh=False):
    tujuan = Path(data) / tanggal(zip_path)
    with paket.kunci_paket(tujuan):
        baru = bongkar(zip_path, tujuan)
    if not (tujuan / "products" / "products.json").exists():
        raise paket.PaketError("zip tidak berisi products/products.json")
    gambar = 0
    kurang = foto_kurang(tujuan)
    if kurang and unduh:
        gambar = unduh_gambar(tujuan)
        kurang = foto_kurang(tujuan)
    hasil = paket.muat(tujuan)
    return {"paket": str(tujuan), "berkas_baru": baru, "gambar_diunduh": gambar, "produk_tanpa_foto": kurang,
            "produk": len(hasil), "siap": sum(1 for _, d, _ in hasil if not d)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daftar")
    d.add_argument("--data", default=str(DATA))
    d.add_argument("--cari", action="append")
    i = sub.add_parser("impor")
    i.add_argument("zip")
    i.add_argument("--data", default=str(DATA))
    i.add_argument("--unduh-gambar", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "daftar":
            print(json.dumps(daftar(Path(a.data), [Path(c) for c in (a.cari or [str(x) for x in CARI])]), ensure_ascii=False))
        else:
            print(json.dumps(impor(a.zip, Path(a.data), a.unduh_gambar), ensure_ascii=False))
    except (paket.PaketError, OSError, zipfile.BadZipFile, subprocess.TimeoutExpired) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
