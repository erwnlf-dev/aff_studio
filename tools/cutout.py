#!/usr/bin/env python3
"""Cutout produk dari foto penjual (latar dan teks marketing dihapus), dikemas untuk film Slate.

    .venv/bin/python tools/cutout.py --paket <folder> --produk <id> --foto 5 --nama keset --keluar <folder produksi>
    .venv/bin/python tools/cutout.py ... --foto 6 --crop 0,0,0.5,0.5 --nama motif_pink    # satu kuadran dulu
    .venv/bin/python tools/cutout.py --kemas <folder produksi>                              # tulis ulang aset/foto.js

Hasil di <folder produksi>/cutout/<nama>.png (dipangkas ke tepi alpha + 24 px) dan aset/foto.js:
`export const FOTO = {nama: {src: "data:image/webp;base64,...", w, h}}`, WebP beralpha supaya muat di batas 2 MB
renderer Slate. Setiap cutout juga digambar di atas warna latar ke cutout/<nama>_cek.jpg untuk dicek mata (BIBLE
"Produk sebagai hero": tepi bersih, tanpa sisa teks/badge, produk tidak terpotong).

Model bawaan isnet-general-use (rembg, Apache-2.0); di server ARM 4 core ±10 detik per foto. Pulau alpha kecil yang
terpisah dari benda utama (sisa ikon/teks penjual) dibuang: hanya komponen yang ≥ --pulau_min dari yang terbesar
yang dipertahankan.
"""
import argparse
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

LATAR_CEK = (63, 167, 160)      # teal midcentury, kontras dengan kebanyakan produk


def potong(im, crop):
    if not crop:
        return im
    a = [float(x) for x in crop.split(",")]
    if all(0 <= x <= 1 for x in a):
        a = [a[0] * im.width, a[1] * im.height, a[2] * im.width, a[3] * im.height]
    return im.crop(tuple(int(round(x)) for x in a))


def bersihkan(rgba, pulau_min):
    """Buang pulau alpha kecil (sisa ikon/teks) dan pangkas ke benda."""
    arr = np.array(rgba)
    alpha = arr[..., 3]
    lab, n = ndimage.label(alpha > 128)
    if n > 1:
        ukuran = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
        simpan = {i + 1 for i, s in enumerate(ukuran) if s >= pulau_min * ukuran.max()}
        topeng = np.isin(lab, list(simpan))
        topeng = ndimage.binary_dilation(topeng, iterations=3)      # pertahankan tepi lembut di sekitar benda
        arr[..., 3] = np.where(topeng, alpha, 0)
    out = Image.fromarray(arr)
    bb = out.getbbox()
    if not bb:
        raise SystemExit("cutout kosong: model tidak menemukan benda")
    x0, y0, x1, y1 = bb
    pad = 24
    kanvas = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    kanvas.paste(out.crop(bb), (pad, pad))
    return kanvas


def kemas(produksi, kualitas=86, sisi=900):
    folder = Path(produksi) / "cutout"
    foto = {}
    for p in sorted(folder.glob("*.png")):
        im = Image.open(p).convert("RGBA")
        im.thumbnail((sisi, sisi), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=kualitas, method=6)
        foto[p.stem] = {"src": "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode(), "w": im.width, "h": im.height}
    aset = Path(produksi) / "aset"
    aset.mkdir(parents=True, exist_ok=True)
    js = "// dibuat tools/cutout.py --kemas; jangan diedit\nexport const FOTO = " + json.dumps(foto) + ";\n"
    (aset / "foto.js").write_text(js, encoding="utf-8")
    return {k: (v["w"], v["h"]) for k, v in foto.items()}, len(js.encode())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paket")
    ap.add_argument("--produk")
    ap.add_argument("--foto", type=int, help="indeks foto (0 = <id>_01.jpg)")
    ap.add_argument("--crop", help="x0,y0,x1,y1 (px, atau pecahan 0..1) sebelum cutout")
    ap.add_argument("--nama")
    ap.add_argument("--keluar", help="folder produksi")
    ap.add_argument("--model", default="isnet-general-use")
    ap.add_argument("--pulau_min", type=float, default=0.02)
    ap.add_argument("--kemas", metavar="FOLDER_PRODUKSI", help="hanya tulis ulang aset/foto.js dari cutout/*.png")
    a = ap.parse_args(argv)
    if a.kemas:
        ukuran, byte = kemas(a.kemas)
        print(json.dumps({"foto.js_byte": byte, "cutout": ukuran}))
        return 0
    if not all([a.paket, a.produk, a.foto is not None, a.nama, a.keluar]):
        ap.error("butuh --paket --produk --foto --nama --keluar (atau --kemas)")
    from rembg import new_session, remove
    src = Path(a.paket) / "products" / a.produk / "images" / ("%s_%02d.jpg" % (a.produk, a.foto + 1))
    im = potong(Image.open(src).convert("RGB"), a.crop)
    rgba = bersihkan(remove(im, session=new_session(a.model)), a.pulau_min)
    folder = Path(a.keluar) / "cutout"
    folder.mkdir(parents=True, exist_ok=True)
    rgba.save(folder / (a.nama + ".png"))
    cek = Image.new("RGBA", rgba.size, LATAR_CEK + (255,))
    cek.alpha_composite(rgba)
    cek.convert("RGB").save(folder / (a.nama + "_cek.jpg"), quality=88)
    ukuran, byte = kemas(a.keluar)
    print(json.dumps({"cutout": str(folder / (a.nama + ".png")), "ukuran": rgba.size, "foto.js_byte": byte}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
