#!/usr/bin/env python3
"""Susun bahan film satu video: isi.json + foto.json untuk template, plus naskah.txt dan scenes.json untuk voiceover.

    python3 tools/siapkan_film.py --paket <folder> --naskah <naskah.json> --keluar <folder>
                                  [--vo vo.json] [--eksperimen EXP-xx --lengan B] [--set nama=nilai ...]

Tanpa --vo, timing kata diperkirakan dari parameter tempo dan jeda (untuk pratinjau tahap naskah, sebelum TTS).
Dengan --vo (vo.json dari Slate buat_voiceover), timing memakai angka voiceover: VO adalah jam (doc 12 K9).

Format naskah.json (keluaran generator naskah; contoh di tests/):
  {"product_id": "...", "hook_layar": "≤ 5 kata", "cta_layar": "...",
   "beats": [{"tipe": "hook", "vo": "teks terucap, *kata disorot*", "teks_kunci": "≤ 3–5 kata",
              "foto": 0, "fokus": [0.5, 0.5], "sumber": ["fitur:0", "rating", "ajakan"]}, ...]}
Urutan tipe beat harus sama dengan template.<nama>.urutan di registry (beat harga dibuang kalau harga.mode =
tanpa_angka atau data harga terlalu tua).
"""
import argparse
import base64
import colorsys
import io
import json
import re
import sys
from pathlib import Path

import yaml
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cek_params  # noqa: E402
import paket  # noqa: E402

AKHIR_KALIMAT = re.compile(r"[.?!…]$")
SUMBER_SAH = re.compile(r"^(fitur:\d+|nama|rating|ulasan|terjual|varian|harga|masalah|ajakan)$")
KOTAK_CAPTION = "#121216"
PUTIH = "#FFFFFF"


class NaskahError(Exception):
    pass


# ---------------------------------------------------------------- warna

def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in rgb)


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminans(h):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontras(a, b):
    la, lb = sorted((luminans(a), luminans(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def palet(cover_path):
    """Warna latar dari warna dominan foto cover yang tidak putih/abu: hue yang sama, gelap dan agak redup,
    supaya teks putih selalu ≥ 4,5:1 dan kartu foto terang menonjol."""
    with Image.open(cover_path) as im:
        kecil = im.convert("RGB").resize((96, 96))
    q = kecil.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    kandidat = []
    for jumlah, idx in sorted(q.getcolors(), reverse=True):
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if s > 0.18 and 0.12 < l < 0.9:
            kandidat.append((jumlah * s, h, s))
    h, s = (max(kandidat)[1:] if kandidat else (0.62, 0.25))
    latar = _hex(c * 255 for c in colorsys.hls_to_rgb(h, 0.17, min(s, 0.5)))
    lembut = _hex(c * 255 for c in colorsys.hls_to_rgb(h, 0.24, min(s, 0.45)))
    return {"latar": latar, "latar_lembut": lembut, "teks": PUTIH, "kotak_caption": KOTAK_CAPTION}


# ---------------------------------------------------------------- naskah dan timing

def kata_dari_vo(teks):
    """'Lip balm, tapi *ada warnanya*?' → [('Lip', False), ('balm,', False), ('tapi', False), ('ada', True), ...]"""
    out, sorot = [], False
    for token in teks.split():
        mulai = token.startswith("*")
        if mulai:
            sorot = True
        bersih = token.replace("*", "")
        if bersih:
            out.append((bersih, sorot or mulai))
        if token.rstrip(".,?!…").endswith("*"):
            sorot = False
    return out


def cek_naskah(naskah, produk, params):
    urutan = params["template.%s.urutan" % params["template.default"]]
    pakai_harga = params["harga.mode"] != "tanpa_angka" and produk["harga_boleh_tampil"]
    harap = [b for b in urutan if b != "harga" or pakai_harga]
    tipe = [b.get("tipe") for b in naskah.get("beats") or []]
    if tipe != harap:
        raise NaskahError("urutan beat %s, template %s mengharapkan %s" % (tipe, params["template.default"], harap))
    if naskah.get("product_id") != produk["id"]:
        raise NaskahError("product_id naskah %r ≠ produk %r" % (naskah.get("product_id"), produk["id"]))
    hook = (naskah.get("hook_layar") or "").split()
    if not 1 <= len(hook) <= params["hook.teks_layar_kata_maks"]:
        raise NaskahError("hook_layar %d kata, maks %d" % (len(hook), params["hook.teks_layar_kata_maks"]))
    if not (naskah.get("cta_layar") or "").strip():
        raise NaskahError("cta_layar kosong")
    n_foto = len(produk["foto"])
    for i, b in enumerate(naskah["beats"]):
        if not (b.get("vo") or "").strip():
            raise NaskahError("beat %d (%s): vo kosong" % (i, b["tipe"]))
        if not isinstance(b.get("foto"), int) or not 0 <= b["foto"] < n_foto:
            raise NaskahError("beat %d: foto %r di luar 0..%d" % (i, b.get("foto"), n_foto - 1))
        fk = b.get("fokus", [0.5, 0.5])
        if not (isinstance(fk, list) and len(fk) == 2 and all(0 <= x <= 1 for x in fk)):
            raise NaskahError("beat %d: fokus harus [x, y] di 0..1" % i)
        src = b.get("sumber") or []
        if not src or not all(SUMBER_SAH.match(s) for s in src):
            raise NaskahError("beat %d: sumber %r tidak sah (fitur:N, nama, rating, ulasan, terjual, varian, harga, masalah, ajakan)" % (i, src))
        for s in src:
            if s.startswith("fitur:") and int(s[6:]) >= len(produk["fitur"]):
                raise NaskahError("beat %d: %s tidak ada (produk punya %d fitur)" % (i, s, len(produk["fitur"])))
        kalimat = re.split(r"(?<=[.?!…])\s+", b["vo"].replace("*", ""))
        for k in kalimat:
            if len(k.split()) > params["vo.kata_maks_per_kalimat"]:
                raise NaskahError("beat %d: kalimat %d kata, maks %d: %r" % (i, len(k.split()), params["vo.kata_maks_per_kalimat"], k))
    if produk["kategori_diatur"] and params["hook.tipe"] == "pain":
        raise NaskahError("hook pain tidak boleh untuk kategori diatur (%s)" % produk["kategori"])


def perkiraan_timing(beats_kata, params):
    """Timing kata tanpa voiceover: tempo rata-rata dari registry, jeda kalimat dan jeda bagian."""
    dt = 1.0 / params["vo.tempo_kata_per_detik"]
    t, out = 0.05, []
    for i, kata in enumerate(beats_kata):
        if i:
            t += params["vo.jeda_bagian_detik"]
        for j, (w, _) in enumerate(kata):
            d = dt * (0.75 + 0.05 * min(len(w), 10))
            out.append((t, t + d))
            t += d
            if AKHIR_KALIMAT.search(w) and j < len(kata) - 1:
                t += params["vo.jeda_kalimat_detik"]
    return out, t


def timing_vo(beats_kata, vo):
    kata_vo = vo.get("kata") or []
    semua = [w for kata in beats_kata for w, _ in kata]
    if len(kata_vo) != len(semua):
        raise NaskahError("vo.json punya %d kata, naskah %d; buat bahan dari naskah yang sama dengan voiceover"
                          % (len(kata_vo), len(semua)))
    for a, b in zip(semua, kata_vo):
        if re.sub(r"\W", "", a.lower()) != re.sub(r"\W", "", b["teks"].lower()):
            raise NaskahError("kata naskah %r ≠ kata vo %r" % (a, b["teks"]))
    return [(k["mulai"], k["selesai"]) for k in kata_vo], float(vo["durasi"])


def kelompok_caption(kata, batas_beat, params):
    """Caption per frasa: ≤ kata_maks_per_layar kata, putus di akhir kalimat dan di batas beat."""
    maks = params["caption.kata_maks_per_layar"]
    grup, cur = [], []
    for i, k in enumerate(kata):
        cur.append(i)
        akhir = AKHIR_KALIMAT.search(k["teks"]) or k["teks"].endswith(",") and len(cur) >= 3
        # jangan sisakan 1–2 kata kalimat ke layar berikutnya ("…Next Level Butter" | "Balm."): perpanjang sampai
        # akhir kalimat selama total ≤ 7 kata (batas Baru Tau)
        sisa = next((j - i for j in range(i + 1, min(i + 3, len(kata))) if AKHIR_KALIMAT.search(kata[j]["teks"])
                     or (j + 1) in batas_beat), None)
        if len(cur) >= maks and sisa is not None and len(cur) + sisa <= 7 and not akhir:
            continue
        if len(cur) >= maks or akhir or (i + 1) in batas_beat or i == len(kata) - 1:
            grup.append(cur)
            cur = []
    out = []
    for n, g in enumerate(grup):
        t0 = kata[g[0]]["t0"]
        t_next = kata[grup[n + 1][0]]["t0"] if n + 1 < len(grup) else None
        t1 = kata[g[-1]]["t1"] + 0.25
        if t_next is not None and t_next - t1 < 0.35:
            t1 = t_next
        sorot = [i for i in g if kata[i]["sorot"]][: params["caption.kata_disorot_per_layar"]]
        out.append({"t0": round(t0, 3), "t1": round(t1, 3), "kata": g, "sorot": sorot})
    return out


# ---------------------------------------------------------------- bukti dan foto

def _angka_tampil(teks):
    """'10RB+' → 10000, '3,5RB+' → 3500, '1JT+' → 1000000."""
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*(RB|JT)?\+?\s*$", str(teks or ""), re.I)
    if not m:
        return None
    n = float(m.group(1).replace(",", "."))
    return int(n * {"RB": 1e3, "JT": 1e6}.get((m.group(2) or "").upper(), 1))


def _ribuan_bawah(n):
    """Pembulatan ke bawah, tidak pernah ke atas: 264454 → '264rb+', 9538 → '9,5rb+', 830 → '830'."""
    if n >= 1_000_000:
        v = int(n / 100_000) / 10
        return ("%g" % v).replace(".", ",") + "jt+"
    if n >= 10_000:
        return "%drb+" % (n // 1000)
    if n >= 1000:
        return ("%g" % (int(n / 100) / 10)).replace(".", ",") + "rb+"
    return str(n)


def bukti(produk, params):
    if params["bukti.format"] == "tanpa":
        return []
    chip = []
    if params["bukti.format"] in ("rating", "terjual_dan_rating") and produk["rating_boleh_tampil"]:
        chip.append("★ %s · %s ulasan" % (("%g" % produk["rating"]).replace(".", ","), _ribuan_bawah(produk["ulasan"])))
    n = _angka_tampil(produk["terjual_tampil"])
    if params["bukti.format"] in ("terjual", "terjual_dan_rating") and n is not None and n >= params["bukti.terjual_min_tampil"]:
        chip.append("%s terjual/bulan" % produk["terjual_tampil"].strip().replace("RB", "rb").replace("JT", "jt"))
    return chip


def kode_foto(paths, params):
    """Foto → data URI JPEG, total ≤ foto.embed_total_maks_kb (kualitas lalu ukuran diturunkan bertahap)."""
    batas = params["foto.embed_total_maks_kb"] * 1000
    sisi, q = params["foto.embed_sisi_panjang_px"], params["foto.embed_jpeg_kualitas"]
    while True:
        out, total = [], 0
        for p in paths:
            with Image.open(p) as im:
                im = im.convert("RGB")
                im.thumbnail((sisi, sisi), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
            src = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            total += len(src)
            out.append({"src": src, "w": im.size[0], "h": im.size[1]})
        if total <= batas:
            return out, {"kualitas": q, "sisi_px": sisi, "total_kb": round(total / 1000)}
        if q > 60:
            q -= 5
        elif sisi > 720:
            sisi = int(sisi * 0.9)
        else:
            raise NaskahError("foto tidak muat di %d KB walau 720 px kualitas 60; kurangi jumlah foto" % (batas // 1000))


# ---------------------------------------------------------------- susun

def susun(produk, naskah, snapshot, vo=None):
    params = snapshot["params"]
    cek_naskah(naskah, produk, params)
    beats_kata = [kata_dari_vo(b["vo"]) for b in naskah["beats"]]
    timing, akhir_vo = timing_vo(beats_kata, vo) if vo else perkiraan_timing(beats_kata, params)

    kata, batas, idx = [], set(), 0
    for bi, kk in enumerate(beats_kata):
        if bi:
            batas.add(idx)
        for w, s in kk:
            t0, t1 = timing[idx]
            kata.append({"teks": w, "t0": round(t0, 3), "t1": round(t1, 3), "sorot": s, "beat": bi})
            idx += 1

    beat_mulai = [0.0] + [kata[i]["t0"] for i in sorted(batas)]
    dur_isi = max(akhir_vo + 0.4, beat_mulai[-1] + params["cta.durasi_detik"])
    dur = round(dur_isi + params["durasi.ekor_loop_detik"], 3)

    cover = next(i for i, f in enumerate(produk["foto"]) if f["cover"])
    dipakai = sorted({b["foto"] for b in naskah["beats"]} | {cover})
    peta = {asli: n for n, asli in enumerate(dipakai)}
    foto, info_foto = kode_foto([produk["foto"][i]["path"] for i in dipakai], params)

    beats = []
    for i, b in enumerate(naskah["beats"]):
        t0 = beat_mulai[i]
        t1 = beat_mulai[i + 1] if i + 1 < len(beat_mulai) else dur
        beats.append({"tipe": b["tipe"], "t0": round(t0, 3), "t1": round(t1, 3), "foto": peta[b["foto"]],
                      "foto_penuh": produk["foto"][b["foto"]]["layar_penuh"], "fokus": b.get("fokus", [0.5, 0.5]),
                      "teks_kunci": naskah["hook_layar"] if i == 0 else (naskah["cta_layar"] if b["tipe"] == "cta" else b.get("teks_kunci", "")),
                      "bukti": bukti(produk, params) if b["tipe"] == "bukti" else [],
                      "harga": None})
        if b["tipe"] == "harga":
            beats[-1]["harga"] = {"teks": "Rp{:,}".format(int(produk["harga"])).replace(",", "."),
                                  "tanggal": produk["harga_diambil"][:10]}

    pal = palet(produk["foto"][cover]["path"])
    pasangan = [[pal["teks"], pal["latar"]], [PUTIH, KOTAK_CAPTION], [params["caption.warna_sorot"], KOTAK_CAPTION],
                [PUTIH, "#000000"]]
    gagal = [p for p in pasangan if kontras(*p) < params["teks.kontras_min"]]
    if gagal:
        raise NaskahError("kontras di bawah %s: %s" % (params["teks.kontras_min"], gagal))

    isi = {
        "versi": 1, "variant_id": snapshot["variant_id"], "eksperimen": snapshot["eksperimen"],
        "produk_id": produk["id"], "dur": dur, "timing": "vo" if vo else "perkiraan",
        "palet": pal, "kontras": pasangan, "disclosure": params["disclosure.teks"],
        "beats": beats, "kata": kata, "caption": kelompok_caption(kata, batas, params),
        "params": params,
    }
    naskah_txt = " ".join(b["vo"].replace("*", "") for b in naskah["beats"])
    scenes = [{"no": i + 1, "vo": b["vo"].replace("*", "")} for i, b in enumerate(naskah["beats"])]
    ringkas = {"dur": dur, "kata": len(kata), "karakter_vo": len(naskah_txt), "foto": info_foto,
               "variant_id": snapshot["variant_id"], "timing": isi["timing"]}
    return isi, {"foto": foto}, naskah_txt, scenes, ringkas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paket", required=True)
    ap.add_argument("--naskah", required=True)
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--vo")
    ap.add_argument("--eksperimen")
    ap.add_argument("--lengan")
    ap.add_argument("--set", action="append", default=[], metavar="nama=nilai")
    a = ap.parse_args(argv)
    try:
        naskah = json.loads(Path(a.naskah).read_text(encoding="utf-8"))
        reg = cek_params.load()
        ov = {}
        for s in a.set:
            k, v = s.split("=", 1)
            ov[k.strip()] = yaml.safe_load(v)
        snap = cek_params.snapshot(reg, ov, (), a.eksperimen, a.lengan)
        produk = next((p for p, ditolak, _ in paket.muat(a.paket, snap["params"])
                       if p["id"] == naskah.get("product_id") and not ditolak), None)
        if produk is None:
            raise NaskahError("produk %r tidak ada di paket atau ditolak validator" % naskah.get("product_id"))
        vo = json.loads(Path(a.vo).read_text(encoding="utf-8")) if a.vo else None
        isi, foto, txt, scenes, ringkas = susun(produk, naskah, snap, vo)
    except (NaskahError, paket.PaketError, ValueError, OSError) as e:
        print("ditolak: %s" % e, file=sys.stderr)
        return 2
    out = Path(a.keluar)
    out.mkdir(parents=True, exist_ok=True)
    (out / "isi.json").write_text(json.dumps(isi, ensure_ascii=False), encoding="utf-8")
    (out / "foto.json").write_text(json.dumps(foto), encoding="utf-8")
    (out / "naskah.txt").write_text(txt + "\n", encoding="utf-8")
    (out / "scenes.json").write_text(json.dumps(scenes, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(ringkas, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
