#!/usr/bin/env python3
"""Pratinjau lokal film template tanpa Slate: contact sheet atau satu frame penuh, dirender Chromium headless.

    python3 tools/pratinjau.py <folder bahan> --keluar sheet.jpg                # 12 frame merata + awal setiap beat
    python3 tools/pratinjau.py <folder bahan> --t 0,2.5,7 --keluar sheet.jpg
    python3 tools/pratinjau.py <folder bahan> --t 0 --frame --keluar f0.jpg     # 1080×1920

Folder bahan = keluaran tools/siapkan_film.py (isi.json, foto.json). Untuk tahap naskah dan iterasi template;
render final dan QA tetap lewat Slate (render_film, qa_video), karena hanya Slate yang menjamin frame persis.
"""
import argparse
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from pathlib import Path

from PIL import Image

AKAR = Path(__file__).resolve().parent.parent
FONTS = Path(os.environ.get("SLATE_FONTS", "/data/apps/slate-studio/kits/fonts"))
CHROMIUM = os.environ.get("CHROMIUM", "chromium-browser")
# sama dengan slate-studio renderer.FONT_LOADS, supaya font pratinjau = font render
FONT_LOADS = ["72px Slab", "72px Oleo", "700 72px Oleo", "500 40px Jost", "600 40px Jost", "700 40px 'Barlow Condensed'",
              "800 40px 'Barlow Condensed'", "400 40px Inter", "600 40px Inter", "500 40px 'JetBrains Mono'", "500 40px Fredoka",
              "40px Lilita"]
LATAR = (0x1B, 0x1B, 0x1F)


class PratinjauError(Exception):
    pass


class _Diam(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def waktu_bawaan(isi, n=12):
    """n titik merata + 0,1 s setelah awal setiap beat, terurut, tanpa t = dur (frame itu tidak pernah dirender)."""
    dur = isi["dur"]
    t = {round(dur * k / n, 2) for k in range(n)} | {round(min(b["t0"] + 0.1, dur - 0.05), 2) for b in isi["beats"]}
    return sorted(x for x in t if 0 <= x < dur)


def _folder_tulis():
    """Chromium snap hanya boleh menulis di ~/snap/chromium/common."""
    exe = shutil.which(CHROMIUM) or CHROMIUM
    if "/snap/" in os.path.realpath(exe) or Path("/snap/bin/chromium").exists() and exe.startswith("/usr/bin/chromium-browser"):
        d = Path.home() / "snap" / "chromium" / "common"
        d.mkdir(parents=True, exist_ok=True)
        return d
    return Path(tempfile.gettempdir())


def render(bahan, waktu, keluar, template="kartu", skala=0.25, kol=None, label=True):
    bahan = Path(bahan)
    film = AKAR / "templates" / template / "film.js"
    if not film.exists():
        raise PratinjauError("template %s tidak ada" % template)
    if not FONTS.is_dir():
        raise PratinjauError("folder font Slate tidak ada: %s (set SLATE_FONTS)" % FONTS)
    kol = kol or min(len(waktu), 6)
    baris = -(-len(waktu) // kol)
    w, h = kol * round(1080 * skala), baris * (round(1920 * skala) + (30 if label else 0))
    with tempfile.TemporaryDirectory(prefix="pratinjau_") as ws:
        ws = Path(ws)
        shutil.copy(film, ws / "film.js")
        shutil.copy(AKAR / "templates" / "_pratinjau" / "index.html", ws / "index.html")
        for f in ("isi.json", "foto.json"):
            shutil.copy(bahan / f, ws / f)
        shutil.copytree(FONTS, ws / "fonts")
        handler = functools.partial(_Diam, directory=str(ws))
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            from urllib.parse import urlencode
            q = urlencode({"t": ",".join("%g" % t for t in waktu), "kol": kol, "skala": skala,
                           "label": "1" if label else "0", "fonts": json.dumps(FONT_LOADS)})
            png = _folder_tulis() / ("aff_pratinjau_%s.png" % uuid.uuid4().hex[:8])
            r = subprocess.run([CHROMIUM, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                                "--force-device-scale-factor=1", "--window-size=%d,%d" % (w, h),
                                "--virtual-time-budget=60000", "--enable-logging=stderr", "--v=0",
                                "--screenshot=%s" % png, "http://127.0.0.1:%d/index.html?%s" % (srv.server_address[1], q)],
                               capture_output=True, text=True, timeout=180)
        finally:
            srv.shutdown()
            srv.server_close()
        galat = [l for l in r.stderr.splitlines() if "Uncaught" in l or "SyntaxError" in l or "TypeError" in l]
        if galat:
            raise PratinjauError("film.js error: " + galat[0][-300:])
        if not png.exists():
            raise PratinjauError("Chromium tidak menulis screenshot (exit %d): %s" % (r.returncode, r.stderr[-300:]))
        try:
            im = Image.open(png).convert("RGB")
            im.load()
        finally:
            png.unlink(missing_ok=True)
    if im.getextrema() == tuple((c, c) for c in LATAR):
        raise PratinjauError("halaman kosong: film.js tidak menggambar (cek isi.json/foto.json)")
    Path(keluar).parent.mkdir(parents=True, exist_ok=True)
    im.save(keluar, quality=88)
    return keluar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bahan")
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--t", help="daftar detik, dipisah koma")
    ap.add_argument("--frame", action="store_true", help="satu frame penuh 1080×1920 (pakai --t dengan satu nilai)")
    ap.add_argument("--template", default="kartu")
    ap.add_argument("--kol", type=int)
    a = ap.parse_args(argv)
    isi = json.loads((Path(a.bahan) / "isi.json").read_text(encoding="utf-8"))
    waktu = [float(x) for x in a.t.split(",")] if a.t else waktu_bawaan(isi)
    try:
        if a.frame:
            if len(waktu) != 1:
                raise PratinjauError("--frame butuh tepat satu --t")
            render(a.bahan, waktu, a.keluar, a.template, skala=1, kol=1, label=False)
        else:
            render(a.bahan, waktu, a.keluar, a.template, kol=a.kol)
    except (PratinjauError, subprocess.TimeoutExpired) as e:
        print("gagal: %s" % e, file=sys.stderr)
        return 1
    print(a.keluar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
