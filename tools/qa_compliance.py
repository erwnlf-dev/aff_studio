#!/usr/bin/env python3
"""QA compliance dengan OCR (BASELINE 15, 18, 19; TODO §6 butir 6). Jalankan dengan .venv/bin/python (rapidocr).

    .venv/bin/python tools/qa_compliance.py foto <folder produksi>    teks tercetak di foto penjual → teks_foto.json
    .venv/bin/python tools/qa_compliance.py video <folder produksi>   frame final.mp4 → qa_compliance.json (exit 1 = gagal)

foto: setiap foto penjual dibaca; angka yang tidak ada di data produk (nama, key_features, data_layar) ditandai
      "bertentangan/tidak bersumber" supaya foto itu tidak dipilih untuk cutout atau crop-nya menghindari teks itu
      (contoh kipas: "16900r/min" vs data 23.000 RPM; "3000mAh" vs 6000mAh).
video: frame setiap 0,75 s dari final.mp4 dibaca, lalu:
  GAGAL   label disclosure ("Link afiliasi" / "afiliasi") tidak terbaca di sebuah frame (kunci disclosure.ada),
  GAGAL   kata terlarang di layar: "Rp" (kecuali data_layar.harga ada), "%", "diskon", "termurah", "promo", "gratis",
  PERIKSA angka di layar yang tidak ada di data produk / naskah: dijelaskan di cek_akhir.md atau dibuang dari film.
Batas OCR: teks kecil < ~28 px, teks miring jauh, dan teks dekoratif bisa terlewat; ini jaring pengaman, bukan pengganti
mata di critic loop.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ANGKA = re.compile(r"(\d+(?:[.,]\d+)*)\s*(rb|jt|k)?\+?", re.I)
TERLARANG = [(re.compile(r"\bRp\.?\s?\d", re.I), "Rp"), (re.compile(r"\d\s?%|%\s?\d"), "%"), (re.compile(r"diskon", re.I), "diskon"),
             (re.compile(r"termurah", re.I), "termurah"), (re.compile(r"\bpromo\b", re.I), "promo"),
             (re.compile(r"\bgratis\b", re.I), "gratis")]
DISCLOSURE = re.compile(r"afilia", re.I)
JARAK = 0.75


def angka(teks):
    """'23.000 RPM' → {23000}; '4,7' → {4.7}; '10RB+' → {10, 10000}; '26rb+' → {26, 26000}; '9,5rb+' → {9.5, 9500}."""
    out = set()
    for m in ANGKA.finditer(teks or ""):
        s, suf = m.group(1), (m.group(2) or "").lower()
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):            # pemisah ribuan Indonesia
            v = float(s.replace(".", ""))
        else:
            v = float(s.replace(",", "."))
        out.add(round(v, 3))
        if suf in ("rb", "k"):
            out.add(round(v * 1000, 3))
        elif suf == "jt":
            out.add(round(v * 1_000_000, 3))
    return out


def sumber_angka(folder):
    """Angka yang sah di layar: nama, key_features, data_layar, naskah (hook/teks kunci/cta/vo), varian, plus 0–10."""
    folder = Path(folder)
    p = json.loads((folder / "produk.json").read_text(encoding="utf-8"))["produk"]
    teks = [p.get("nama") or "", *p.get("fitur", []), json.dumps(json.loads((folder / "data_layar.json").read_text(encoding="utf-8")))]
    n = folder / "naskah.json"
    if n.exists():
        nk = json.loads(n.read_text(encoding="utf-8"))
        teks += [nk.get("hook_layar", ""), nk.get("cta_layar", "")] + [b.get(k, "") for b in nk.get("beats", []) for k in ("vo", "teks_kunci")]
    sah = set().union(*[angka(t) for t in teks]) | {float(i) for i in range(11)}
    for v, n_ in (p.get("varian") or {}).items():
        sah.add(float(len(n_)))
    return sah


def ocr(engine, path):
    hasil, _ = engine(str(path))
    return [(t, float(c)) for _, t, c in (hasil or []) if float(c) >= 0.6]


def cmd_foto(folder, engine):
    folder = Path(folder)
    p = json.loads((folder / "produk.json").read_text(encoding="utf-8"))["produk"]
    sah = sumber_angka(folder)
    out = []
    for i, f in enumerate(p["foto"]):
        teks = ocr(engine, f["path"])
        semua = " | ".join(t for t, _ in teks)
        asing = sorted(v for v in angka(semua) if v not in sah)
        out.append({"foto": i, "teks": [t for t, _ in teks], "angka_tidak_bersumber": asing})
        tanda = ("angka tidak ada di data: %s" % ", ".join("%g" % v for v in asing)) if asing else ("ada teks" if teks else "tanpa teks")
        print("foto %d: %s%s" % (i, tanda, (" — " + semua[:110]) if teks else ""))
    (folder / "teks_foto.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def cmd_video(folder, engine):
    folder = Path(folder)
    video = folder / "final.mp4"
    if not video.exists():
        print("final.mp4 belum ada")
        return 2
    dl = json.loads((folder / "data_layar.json").read_text(encoding="utf-8"))
    sah = sumber_angka(folder)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True, check=True).stdout)
    frames, gagal, periksa = [], [], {}
    with tempfile.TemporaryDirectory() as tmp:
        t = 0.1
        while t < dur - 0.05:
            f = Path(tmp) / ("%06.2f.png" % t)
            subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", str(video), "-frames:v", "1", str(f)], check=True)
            teks = ocr(engine, f)
            semua = " | ".join(x for x, _ in teks)
            ada_label = bool(DISCLOSURE.search(semua))
            larang = [nama for rx, nama in TERLARANG if rx.search(semua) and not (nama == "Rp" and dl.get("harga"))]
            asing = sorted(v for v in angka(semua) if v not in sah)
            frames.append({"t": round(t, 2), "disclosure": ada_label, "terlarang": larang, "angka_asing": asing, "teks": semua[:300]})
            if not ada_label:
                gagal.append("t=%.2f: label disclosure tidak terbaca" % t)
            for nama in larang:
                gagal.append("t=%.2f: kata terlarang '%s' di layar (%s)" % (t, nama, semua[:80]))
            for v in asing:
                periksa.setdefault("%g" % v, []).append(round(t, 2))
            t += JARAK
    lolos = not gagal
    hasil = {"lolos": lolos, "gagal": gagal, "periksa_angka": periksa, "frame": len(frames), "jarak_s": JARAK, "rinci": frames}
    (folder / "qa_compliance.json").write_text(json.dumps(hasil, ensure_ascii=False, indent=1), encoding="utf-8")
    print("QA compliance: %s (%d frame, tiap %.2f s)" % ("LOLOS" if lolos else "GAGAL", len(frames), JARAK))
    for g in gagal:
        print("GAGAL: " + g)
    for v, ts in periksa.items():
        print("PERIKSA angka %s di t=%s (tidak ada di data/naskah; jelaskan di cek_akhir.md atau buang)" % (v, ", ".join("%.2f" % x for x in ts[:6])))
    return 0 if lolos else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("foto", "video"):
        print(__doc__)
        return 2
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()
    return (cmd_foto if argv[0] == "foto" else cmd_video)(argv[1], engine)


if __name__ == "__main__":
    sys.exit(main())
