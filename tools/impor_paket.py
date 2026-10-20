#!/usr/bin/env python3
"""Impor paket data dari sesi Claude in Chrome ke folder data aff_studio (dipakai konsol web, tombol "Impor").

    python3 tools/impor_paket.py daftar [--data /data/apps/affiliate-data] [--cari /data/apps]   zip yang bisa diimpor (JSON)
    python3 tools/impor_paket.py impor <zip> [--data …] [--unduh-gambar]                         → <data>/<tanggal>/ (JSON)

Nama folder tujuan = tanggal di nama zip (affiliate_pipeline_data_2026-10-19.zip → 2026-10-19); paket yang sudah ada
tidak ditimpa (berkas lama dipertahankan, hanya yang belum ada yang ditambahkan). Anggota zip di luar folder tujuan
ditolak. Kalau foto produk tidak ikut di zip, --unduh-gambar menjalankan fetch_images_zip.py milik paket itu (gambar
dari CDN Shopee, jeda 1,5–3,5 s per file) lalu membongkar hasilnya ke products/<id>/images/. Tanpa --unduh-gambar,
produk tanpa foto ditolak validator (tools/paket.py).
"""
import argparse
import json
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


def bongkar(zip_path, tujuan):
    """Bongkar aman: anggota di luar tujuan ditolak; berkas yang sudah ada tidak ditimpa."""
    tujuan = Path(tujuan).resolve()
    baru = 0
    with zipfile.ZipFile(zip_path) as z:
        for m in z.infolist():
            t = (tujuan / m.filename).resolve()
            if not str(t).startswith(str(tujuan) + "/") and t != tujuan:
                raise paket.PaketError("anggota zip di luar folder: %s" % m.filename)
        for m in z.infolist():
            t = tujuan / m.filename
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
    tujuan.mkdir(parents=True, exist_ok=True)
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
