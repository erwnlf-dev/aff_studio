#!/usr/bin/env python3
"""Panggil Slate Studio untuk satu folder video (keluaran tools/siapkan_film.py).

    python3 tools/slate.py kuota                               sisa karakter ElevenLabs dan batas harian server
    python3 tools/slate.py vo <folder> [--voice ID]            buat_voiceover dari naskah.txt + scenes.json → vo.json
    python3 tools/slate.py render <folder> [--template kartu]  render_film: film.js template + isi.json + foto.json
    python3 tools/slate.py tunggu <folder> [--maks detik]      tunggu render selesai, unduh final.mp4 + status.json
    python3 tools/slate.py qa <folder>                         qa_video untuk job folder ini → qa.json
    python3 tools/slate.py pratinjau <folder> --t 0,2.5 [--keluar f.jpg]   stills dari renderer Slate (tanpa job)

Urutan satu video: siapkan_film (tanpa --vo) → setuju naskah → vo → siapkan_film --vo vo.json → render → tunggu → qa.

Alamat server (SLATE_MCP_URL, berisi secret) dibaca dari file env, berurutan: $AFF_SLATE_ENV, aff_studio/.env,
/data/apps/baru-tau-autopilot/.env. Alamat itu tidak pernah dicetak dan disensor dari semua pesan. Tool posting dan
Telegram selalu ditolak: posting tetap keputusan pemilik (TODO §1). vo menolak kalau vo.json sudah ada, supaya
kredit ElevenLabs tidak terpakai dua kali untuk naskah yang sama.
"""
import argparse
import base64
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
ENV_CALON = [os.environ.get("AFF_SLATE_ENV"), AKAR / ".env", "/data/apps/baru-tau-autopilot/.env"]
IZIN = {"cek_kuota", "buat_voiceover", "render_film", "status_job", "qa_video", "pratinjau_film"}
RENDER_JALAN = ("antre", "menyiapkan", "merender_frame", "musik", "menggabung_vo")
MAKS_FILM = 2_000_000      # slate-studio renderer.prepare_workspace: total semua file film


class SlateError(Exception):
    pass


# ---------------------------------------------------------------- klien MCP

def _baca_env(path):
    env = {}
    for line in Path(path).read_text(errors="replace").splitlines():
        m = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
        if m:
            v = m.group(2).rstrip("\r").split(" #")[0]
            q = re.fullmatch(r"\"(.*)\"|'(.*)'", v)
            env[m.group(1)] = (q.group(1) if q.group(1) is not None else q.group(2)) if q else v
    return env


def url_server():
    for p in ENV_CALON:
        if p and Path(p).is_file():
            url = _baca_env(p).get("SLATE_MCP_URL", "")
            if url:
                return url
    raise SlateError("SLATE_MCP_URL tidak ditemukan ($AFF_SLATE_ENV, aff_studio/.env, atau .env autopilot)")


def sensor(teks):
    s = str(teks)
    try:
        url = url_server()
    except SlateError:
        return s
    u = urllib.parse.urlsplit(url)
    for rahasia in {url, url.rstrip("/"), u.path, u.path.rstrip("/").rsplit("/", 1)[-1]}:
        if len(rahasia) >= 8:
            s = s.replace(rahasia, "<SLATE_MCP_URL>")
    return s


def panggil(tool, args, timeout=900):
    if tool not in IZIN:
        raise SlateError("tool %r tidak diizinkan lewat helper ini" % tool)
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": args}}).encode()
    req = urllib.request.Request(url_server(), data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise SlateError(sensor("HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))) from None
    except Exception as e:  # noqa: BLE001
        raise SlateError(sensor("server tidak bisa dihubungi: %s" % e)) from None
    if raw.lstrip().startswith(("event:", "data:")):
        raw = [ln[5:].strip() for ln in raw.splitlines() if ln.startswith("data:")][-1]
    res = json.loads(raw)
    if res.get("error"):
        raise SlateError(sensor(json.dumps(res["error"], ensure_ascii=False)[:400]))
    return (res.get("result") or {}).get("content") or []


def panggil_json(tool, args, timeout=900):
    content = panggil(tool, args, timeout)
    t = "".join(c.get("text", "") for c in content if c.get("type") == "text")
    try:
        d = json.loads(t)
    except ValueError:
        return {"error": sensor(t[:300]) or "jawaban kosong"}
    return d if isinstance(d, dict) else {"error": "jawaban bukan objek JSON"}


def link_lokal(link, nama=None):
    """Link job publik (PUBLIC_BASE_URL + ?k= token job) diarahkan ke server lokal dari SLATE_MCP_URL."""
    u, base = urllib.parse.urlsplit(link), urllib.parse.urlsplit(url_server())
    path = u.path
    if nama:
        path = re.sub(r"^(/j/[^/]+)(/f/[^/]+)?$", lambda m: m.group(1) + "/f/" + nama, path)
    return urllib.parse.urlunsplit((base.scheme, base.netloc, path, u.query, ""))


def unduh(link, nama, tujuan=None, timeout=600):
    req = urllib.request.Request(link_lokal(link, nama))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if tujuan is None:
                return r.read()
            tmp = Path(str(tujuan) + ".tmp")
            with open(tmp, "wb") as f:
                shutil.copyfileobj(r, f, 1024 * 1024)
            tmp.replace(tujuan)
            return None
    except urllib.error.HTTPError as e:
        raise SlateError("unduh %s gagal: HTTP %s" % (nama, e.code)) from None
    except Exception as e:  # noqa: BLE001
        raise SlateError(sensor("unduh %s gagal: %s" % (nama, e))) from None


def tanpa_link(d):
    """Salinan jawaban tanpa link job (berisi token ?k=) untuk dicetak."""
    if isinstance(d, dict):
        return {k: ("<link>" if isinstance(v, str) and "?k=" in v else tanpa_link(v)) for k, v in d.items()}
    if isinstance(d, list):
        return [tanpa_link(x) for x in d]
    return d


# ---------------------------------------------------------------- perintah

def _isi(folder):
    p = Path(folder) / "isi.json"
    if not p.is_file():
        raise SlateError("%s tidak ada; jalankan tools/siapkan_film.py dulu" % p)
    return json.loads(p.read_text(encoding="utf-8"))


def _vo(folder):
    p = Path(folder) / "vo.json"
    if not p.is_file():
        raise SlateError("%s tidak ada; jalankan 'slate.py vo' dulu" % p)
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_kuota(a):
    return panggil_json("cek_kuota", {}, timeout=120)


def cmd_vo(a):
    folder = Path(a.folder)
    tujuan = folder / "vo.json"
    if tujuan.exists():
        raise SlateError("%s sudah ada: voiceover untuk naskah ini sudah dibuat (kredit tidak dipakai dua kali)" % tujuan)
    isi = _isi(folder)
    p = isi["params"]
    naskah = (folder / "naskah.txt").read_text(encoding="utf-8").strip()
    scenes = json.loads((folder / "scenes.json").read_text(encoding="utf-8"))
    args = {"judul": "Affiliate %s %s" % (isi["produk_id"], isi["variant_id"]), "naskah": naskah, "scenes": scenes,
            "model": {"eleven_v3": "v3", "eleven_multilingual_v2": "v2"}[p["vo.model"]],
            "speed": p["vo.v2.speed"], "subtitle": False, "musik": "pelan" if p["musik.ada"] else "mati",
            "ruang_napas": True, "jeda_kalimat": p["vo.jeda_kalimat_detik"], "jeda_bagian": p["vo.jeda_bagian_detik"]}
    if a.voice:
        args["voice_id"] = a.voice
    d = panggil_json("buat_voiceover", args)
    if d.get("error"):
        return d
    if d.get("link_job"):
        try:
            d["kata"] = json.loads(unduh(d["link_job"], "timing.json", timeout=60)).get("kata")
        except (SlateError, ValueError) as e:
            d["kata_error"] = str(e)
    tujuan.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"vo": str(tujuan), "job_id": d.get("job_id"), "durasi": d.get("durasi"),
            "karakter_terpakai": d.get("karakter_terpakai"), "kata": len(d.get("kata") or []),
            "sisa_kuota_harian_server": d.get("sisa_kuota_harian_server")}


def _bahan_film(folder, a):
    """(film_js, file_tambahan) untuk template atau film yang disutradarai (--film, ADR-P06). Folder aset/ selalu ikut
    sebagai aset/<nama>; isi.json/foto.json hanya untuk template."""
    folder = Path(folder)
    if a.film:
        film = Path(a.film).read_text(encoding="utf-8")
        tambahan = {}
    else:
        film = (AKAR / "templates" / a.template / "film.js").read_text(encoding="utf-8")
        tambahan = {f: (folder / f).read_text(encoding="utf-8") for f in ("isi.json", "foto.json")}
    if a.film:                                           # kit affiliate aff_studio dikirim sebagai engine/<nama>
        for f in sorted((AKAR / "kits" / "affiliate").glob("*.js")):
            tambahan["engine/" + f.name] = f.read_text(encoding="utf-8")
    if (folder / "aset").is_dir():
        for f in sorted((folder / "aset").iterdir()):
            if f.suffix in (".js", ".json", ".css", ".svg", ".txt"):
                tambahan["aset/" + f.name] = f.read_text(encoding="utf-8")
    total = sum(len(x.encode("utf-8")) for x in [film, *tambahan.values()])
    if total > MAKS_FILM:
        raise SlateError("file film %d byte, batas renderer Slate %d" % (total, MAKS_FILM))
    return film, tambahan


def cmd_render(a):
    folder = Path(a.folder)
    isi, vo = _isi(folder), _vo(folder)
    if not a.film and isi.get("timing") != "vo":
        raise SlateError("isi.json masih memakai timing perkiraan; jalankan siapkan_film.py --vo %s/vo.json dulu" % folder)
    film, tambahan = _bahan_film(folder, a)
    p = isi["params"]
    partitur = Path(a.partitur) if a.partitur else folder / "score.json"
    args = {"job_id": vo["job_id"], "film_js": film, "kit": a.kit or "none", "file_tambahan": tambahan,
            "fps": a.fps or p["motion.fps"], "durasi": a.durasi or isi["dur"],
            "musik": a.musik or ("pelan" if p["musik.ada"] else "mati"), "subtitle": False,
            "telegram": False, "qa_wajib": True}
    if a.film and partitur.is_file():
        args["partitur_json"] = partitur.read_text(encoding="utf-8")
    d = panggil_json("render_film", args)
    (folder / "render.json").write_text(json.dumps(tanpa_link(d), ensure_ascii=False, indent=2), encoding="utf-8")
    return tanpa_link(d)


def cmd_tunggu(a):
    folder = Path(a.folder)
    job = _vo(folder)["job_id"]
    batas = time.time() + max(0, min(a.maks, 1800))
    while True:
        st = panggil_json("status_job", {"job_id": job}, timeout=60)
        r = st.get("render") or {}
        if st.get("error") or r.get("state") not in RENDER_JALAN or time.time() >= batas:
            break
        time.sleep(15)
    (folder / "status.json").write_text(json.dumps(tanpa_link(st), ensure_ascii=False, indent=2), encoding="utf-8")
    link = next((v for v in st.values() if isinstance(v, str) and "/j/" in v and "?k=" in v), None)
    if link and (st.get("state") == "selesai" or (st.get("render") or {}).get("state") == "selesai"):
        unduh(link, "final.mp4", folder / "final.mp4")
        st["final_lokal"] = str(folder / "final.mp4")
    return tanpa_link(st)


def cmd_qa(a):
    folder = Path(a.folder)
    d = panggil_json("qa_video", {"job_id": _vo(folder)["job_id"]}, timeout=600)
    (folder / "qa.json").write_text(json.dumps(tanpa_link(d), ensure_ascii=False, indent=2), encoding="utf-8")
    return tanpa_link(d)


def cmd_pratinjau(a):
    folder = Path(a.folder)
    film, tambahan = _bahan_film(folder, a)
    content = panggil("pratinjau_film", {"film_js": film, "waktu": [float(x) for x in a.t.split(",")],
                                         "kit": a.kit or "none", "file_tambahan": tambahan}, timeout=600)
    for c in content:
        if c.get("type") == "image":
            keluar = Path(a.keluar or folder / "pratinjau_slate.jpg")
            keluar.write_bytes(base64.b64decode(c.get("data", "")))
            return {"gambar": str(keluar)}
    t = "".join(c.get("text", "") for c in content if c.get("type") == "text")
    return {"error": sensor(t[:400]) or "tidak ada gambar"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("kuota")
    s = sub.add_parser("vo")
    s.add_argument("folder")
    s.add_argument("--voice")
    s = sub.add_parser("render")
    s.add_argument("folder")
    s.add_argument("--template", default="kartu")
    s.add_argument("--film", help="film.js sendiri (video yang disutradarai); aset/ dan score.json folder ikut")
    s.add_argument("--kit", help="kit Slate, mis. midcentury")
    s.add_argument("--partitur", help="score.json (bawaan <folder>/score.json, hanya dengan --film)")
    s.add_argument("--durasi", type=float, help="META.dur film (bawaan isi.json dur)")
    s.add_argument("--fps", type=int)
    s.add_argument("--musik", choices=["pelan", "sedang", "mati"])
    s = sub.add_parser("tunggu")
    s.add_argument("folder")
    s.add_argument("--maks", type=int, default=540)
    s = sub.add_parser("qa")
    s.add_argument("folder")
    s = sub.add_parser("pratinjau")
    s.add_argument("folder")
    s.add_argument("--t", required=True)
    s.add_argument("--keluar")
    s.add_argument("--template", default="kartu")
    s.add_argument("--film")
    s.add_argument("--kit")
    a = ap.parse_args(argv)
    try:
        hasil = {"kuota": cmd_kuota, "vo": cmd_vo, "render": cmd_render, "tunggu": cmd_tunggu, "qa": cmd_qa,
                 "pratinjau": cmd_pratinjau}[a.cmd](a)
    except (SlateError, OSError, KeyError, ValueError) as e:
        print(json.dumps({"error": sensor(str(e))}, ensure_ascii=False))
        return 1
    print(json.dumps(hasil, ensure_ascii=False, indent=1))
    return 1 if isinstance(hasil, dict) and hasil.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
