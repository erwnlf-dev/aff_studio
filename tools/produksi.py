#!/usr/bin/env python3
"""Satu pintu produksi video affiliate yang disutradarai (ADR-P06). Langkah dan aturannya: CLAUDE.md.

    python3 tools/produksi.py init --paket <folder paket> --produk <id>   folder kerja + kerangka + foto_sheet.jpg
    python3 tools/produksi.py <folder> cutout --foto N --nama X [--crop x0,y0,x1,y1] [--model u2net]
    python3 tools/produksi.py <folder> naskah                    validasi naskah.json → naskah.txt, scenes.json, isi.json
    python3 tools/produksi.py <folder> vo --voice <id>           buat_voiceover (sekali) + tools/sunyi.py
    python3 tools/produksi.py <folder> kata                      KATA untuk film.js + calon hening (dari kata_koreksi.json)
    python3 tools/produksi.py <folder> audit                     tools/audit_film.py
    python3 tools/produksi.py <folder> pratinjau --t 0,1.5,... --keluar pratinjau_r1.jpg [--slate]
    python3 tools/produksi.py <folder> skor                      jalankan score.py → score.json, lalu audit
    python3 tools/produksi.py <folder> render                    render_film (META.dur dari film.js), tunggu, unduh final.mp4
    python3 tools/produksi.py <folder> qa                        ringkasan QA render terakhir (status.json)
    python3 tools/produksi.py <folder> compliance                OCR final.mp4: disclosure tiap frame, tanpa Rp/%/diskon
    python3 tools/produksi.py <folder> paket-unggah [--platform]  (setelah disetujui pemilik) → <paket>/unggah/<video_id>/
    python3 tools/produksi.py <folder> sheet                     final_sheet.jpg: 20 frame dari final.mp4 (cek tanpa suara)
    python3 tools/produksi.py <folder> status                    langkah yang sudah/belum

Folder kerja bawaan: <paket>/produksi/<id>/ (di luar repo: repo publik). Gaya bawaan midcentury + kit affiliate.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
TOOLS = AKAR / "tools"
sys.path.insert(0, str(TOOLS))
import cek_params  # noqa: E402
import paket  # noqa: E402
import siapkan_film  # noqa: E402

VENV_PY = AKAR / ".venv" / "bin" / "python"
KIT = "midcentury"


class ProduksiError(Exception):
    pass


def jalan(args, **kw):
    """Jalankan alat lain, teruskan keluarannya; gagal → ProduksiError."""
    r = subprocess.run([str(a) for a in args], cwd=AKAR, text=True, **kw)
    if r.returncode != 0:
        raise ProduksiError("%s keluar dengan kode %d" % (Path(str(args[1])).name, r.returncode))
    return r


def meta(folder):
    p = Path(folder) / "produksi.json"
    if not p.exists():
        raise ProduksiError("%s bukan folder produksi (jalankan init dulu)" % folder)
    return json.loads(p.read_text(encoding="utf-8"))


def data_layar(produk, params):
    """Teks bukti persis seperti yang boleh tampil (BASELINE 19): tanpa pembulatan ke atas, tanpa harga coret."""
    d = {}
    n = siapkan_film._angka_tampil(produk["terjual_tampil"])
    if n is not None and n >= params["bukti.terjual_min_tampil"]:
        d["terjual"] = produk["terjual_tampil"].strip()
    if produk["rating_boleh_tampil"]:
        d["rating"] = ("%g" % produk["rating"]).replace(".", ",")
        d["ulasan"] = siapkan_film._ribuan_bawah(produk["ulasan"])
    d["varian"] = {k: len(v) for k, v in (produk["varian"] or {}).items()}
    d["harga"] = None if params["harga.mode"] == "tanpa_angka" or not produk["harga_boleh_tampil"] else \
        "Rp{:,}".format(int(produk["harga"])).replace(",", ".")
    return d


def foto_sheet(produk, tujuan):
    from PIL import Image, ImageDraw
    fs = produk["foto"]
    W, kol = 300, 5
    sheet = Image.new("RGB", (kol * W, ((len(fs) + kol - 1) // kol) * (W + 26)), "white")
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(fs):
        with Image.open(f["path"]) as im:
            im = im.convert("RGB")
            im.thumbnail((W - 6, W - 6))
        x, y = (i % kol) * W, (i // kol) * (W + 26)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 6, y + W + 6), "foto %d  %dpx%s%s" % (i, f["sisi_pendek"], " cover" if f["cover"] else "",
                                                       "" if f["layar_penuh"] else " (kecil)"), fill="black")
    sheet.save(tujuan, quality=88)


# Hasil satu run. Run ulang di folder yang sama memindahkannya ke _sebelum/<ts>/ (hanya di sini, dipanggil
# run_produksi.sh di bawah kunci produksi; konsol web tidak mengarsipkan): GAGAL.md lama tidak boleh menutupi video baru,
# dan final.mp4/qa_compliance.json lama tidak boleh terbaca sebagai hasil run baru. VO, naskah, film, partitur tetap.
HASIL_RUN = ("final.mp4", "final_sheet.jpg", "cek_akhir.md", "qa_compliance.json", "teks_post.txt", "status.json",
             "biaya.json", "GAGAL.md")


def arsipkan_hasil(folder):
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    folder = Path(folder)
    if (folder / "review.json").exists():
        (folder / "review.json").rename(folder / ("review_%s.json" % ts))
    lama = [n for n in HASIL_RUN if (folder / n).exists()]
    if not lama:
        return None
    tujuan = folder / "_sebelum" / ts
    tujuan.mkdir(parents=True, exist_ok=True)
    for n in lama:
        (folder / n).rename(tujuan / n)
    return tujuan


def kunci_dipegang():
    """True kalau ada yang memegang flock logs/.produksi.lock (dari /proc/locks, tanpa ikut mengunci)."""
    import os
    f = AKAR / "logs" / ".produksi.lock"
    try:
        st = f.stat()
        baris = Path("/proc/locks").read_text().splitlines()
    except OSError:
        return False
    for b in baris:
        bagian = b.split()
        if "->" in bagian or len(bagian) < 6 or bagian[1] != "FLOCK":
            continue
        try:
            maj, mnr, ino = bagian[5].split(":")
            if (int(ino), int(maj, 16), int(mnr, 16)) == (st.st_ino, os.major(st.st_dev), os.minor(st.st_dev)):
                return True
        except ValueError:
            continue
    return False


def cmd_init(a):
    params = cek_params.resolve(cek_params.load())
    hasil = {p["id"]: (p, d, w) for p, d, w in paket.muat(a.paket, params)}
    if a.produk not in hasil:
        raise ProduksiError("produk %s tidak ada di paket" % a.produk)
    produk, ditolak, peringatan = hasil[a.produk]
    if ditolak:
        raise ProduksiError("produk ditolak validator paket: " + "; ".join(ditolak))
    folder = Path(a.folder) if a.folder else Path(a.paket) / "produksi" / a.produk
    if getattr(a, "baru", False) and folder.exists():
        import datetime
        tujuan = folder.parent / "_arsip" / ("%s-%s" % (folder.name, datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
        tujuan.parent.mkdir(parents=True, exist_ok=True)
        folder.rename(tujuan)
        print("folder lama diarsipkan utuh (naskah baru): %s" % tujuan)
    folder.mkdir(parents=True, exist_ok=True)
    arsip = arsipkan_hasil(folder)
    if arsip:
        print("hasil run sebelumnya diarsipkan: %s" % arsip)
    snap = cek_params.snapshot(cek_params.load())
    dl = data_layar(produk, params)
    (folder / "produk.json").write_text(json.dumps({"produk": produk, "peringatan": peringatan}, ensure_ascii=False, indent=1), encoding="utf-8")
    (folder / "data_layar.json").write_text(json.dumps(dl, ensure_ascii=False, indent=1), encoding="utf-8")
    foto_sheet(produk, folder / "foto_sheet.jpg")
    urutan = [b for b in params["template.%s.urutan" % params["template.default"]] if b != "harga" or dl["harga"]]
    isi = {"NAMA": produk["nama"], "ID": produk["id"], "GAYA": "midcentury-toon", "JOB": "<job vo>",
           "VARIANT": snap["variant_id"], "DATA_LAYAR": json.dumps(dl, ensure_ascii=False), "CN": produk["compliance_note"] or "—"}
    for nama in ("film.js", "score.py", "brief.md"):
        tujuan = folder / nama
        if not tujuan.exists():
            teks = (AKAR / "templates" / "produksi" / nama).read_text(encoding="utf-8")
            for k, v in isi.items():
                teks = teks.replace("{{%s}}" % k, str(v))
            tujuan.write_text(teks, encoding="utf-8")
    if not (folder / "naskah.json").exists():
        cover = next(i for i, f in enumerate(produk["foto"]) if f["cover"])
        naskah = {"product_id": produk["id"], "hook_layar": "", "cta_layar": "",
                  "beats": [{"tipe": b, "vo": "", "teks_kunci": "", "foto": cover, "sumber": []} for b in urutan]}
        (folder / "naskah.json").write_text(json.dumps(naskah, ensure_ascii=False, indent=1), encoding="utf-8")
    (folder / "produksi.json").write_text(json.dumps({"paket": str(Path(a.paket).resolve()), "produk": produk["id"],
                                                      "variant_id": snap["variant_id"], "kit": KIT}, indent=1), encoding="utf-8")
    print("folder: %s" % folder)
    print("produk: %s — %s" % (produk["id"], produk["nama"]))
    print("fitur (sumber fitur:N):")
    for i, f in enumerate(produk["fitur"]):
        print("  fitur:%d  %s" % (i, f))
    print("data_layar: %s" % json.dumps(dl, ensure_ascii=False))
    print("urutan beat: %s" % urutan)
    for w in peringatan:
        print("peringatan: " + w)
    if VENV_PY.exists() and not (folder / "teks_foto.json").exists():
        print("teks tercetak di foto penjual (tools/qa_compliance.py foto → teks_foto.json):")
        subprocess.run([str(VENV_PY), str(TOOLS / "qa_compliance.py"), "foto", str(folder)], cwd=AKAR)
    print("berikutnya: buka foto_sheet.jpg, pilih foto bersih → cutout; tulis naskah.json → naskah")
    return 0


def cmd_cutout(a):
    m = meta(a.folder)
    if not VENV_PY.exists():
        raise ProduksiError("venv rembg belum ada: python3 -m venv --system-site-packages .venv && .venv/bin/pip install 'rembg[cpu]'")
    args = [VENV_PY, TOOLS / "cutout.py", "--paket", m["paket"], "--produk", m["produk"], "--foto", a.foto, "--nama", a.nama, "--keluar", a.folder]
    if a.crop:
        args += ["--crop", a.crop]
    if a.model:
        args += ["--model", a.model]
    jalan(args)
    from PIL import Image
    cek = sorted(Path(a.folder, "cutout").glob("*_cek.jpg"))
    W = 300
    sheet = Image.new("RGB", (3 * W, ((len(cek) + 2) // 3) * W), "white")
    for i, f in enumerate(cek):
        with Image.open(f) as im:
            im.thumbnail((W - 6, W - 6))
            sheet.paste(im, ((i % 3) * W, (i // 3) * W))
    sheet.save(Path(a.folder) / "cutout_sheet.jpg", quality=88)
    print("cek mata: %s/cutout_sheet.jpg" % a.folder)
    return 0


def cmd_naskah(a):
    m = meta(a.folder)
    args = [sys.executable, TOOLS / "siapkan_film.py", "--paket", m["paket"], "--naskah", Path(a.folder) / "naskah.json", "--keluar", a.folder]
    if (Path(a.folder) / "vo.json").exists():
        args += ["--vo", Path(a.folder) / "vo.json"]
    jalan(args)
    return 0


def cmd_vo(a):
    folder = Path(a.folder)
    if not (folder / "naskah.txt").exists():
        raise ProduksiError("naskah.txt belum ada: jalankan 'naskah' dulu")
    if not (folder / "vo.json").exists():
        if not a.voice:
            raise ProduksiError("--voice wajib (server Slate tanpa suara bawaan)")
        jalan([sys.executable, TOOLS / "slate.py", "vo", folder, "--voice", a.voice])
    jalan([sys.executable, TOOLS / "sunyi.py", folder])
    return 0


def cmd_kata(a):
    k = json.loads((Path(a.folder) / "kata_koreksi.json").read_text(encoding="utf-8"))
    print("const KATA = %s;" % json.dumps(k["kata"], ensure_ascii=False))
    for i, (t0, t1, w) in enumerate(k["kata"]):
        print("  %2d  %-14s %6.3f  frame %d" % (i, w, t0, round(t0 * 24)))
    print("jendela sunyi: %s" % ", ".join("%.2f–%.2f" % tuple(s) for s in k["sunyi"]))
    return 0


def cmd_audit(a):
    jalan([sys.executable, TOOLS / "audit_film.py", a.folder])
    return 0


def cmd_pratinjau(a):
    folder = Path(a.folder)
    keluar = Path(a.keluar) if Path(a.keluar).is_absolute() else folder / a.keluar
    if a.slate:
        jalan([sys.executable, TOOLS / "slate.py", "pratinjau", folder, "--film", folder / "film.js", "--kit", KIT, "--t", a.t, "--keluar", keluar])
    else:
        args = [sys.executable, TOOLS / "pratinjau.py", folder, "--film", folder / "film.js", "--kit", KIT, "--t", a.t, "--keluar", keluar]
        if a.kol:
            args += ["--kol", a.kol]
        jalan(args)
    return 0


def cmd_skor(a):
    jalan([sys.executable, Path(a.folder) / "score.py"])
    jalan([sys.executable, TOOLS / "audit_film.py", a.folder])
    return 0


def meta_film(folder):
    import audit_film
    src = (Path(folder) / "film.js").read_text(encoding="utf-8")
    data, err = audit_film.via_node(src)
    if data is None:
        data = audit_film.via_regex(src)
    dur = ((data or {}).get("META") or {}).get("dur")
    if not dur:
        raise ProduksiError("META.dur film.js tidak terbaca (%s)" % err)
    return float(dur)


def cmd_render(a):
    folder = Path(a.folder)
    if not (folder / "score.json").exists():
        raise ProduksiError("score.json belum ada (BASELINE 11: video tanpa musik/foley dilarang)")
    jalan([sys.executable, TOOLS / "audit_film.py", folder])
    dur = meta_film(folder)
    for f in sorted(folder.glob("final.mp4")):
        n = len(list(folder.glob("final_r*.mp4"))) + 1
        f.rename(folder / ("final_r%d.mp4" % n))
    jalan([sys.executable, TOOLS / "slate.py", "render", folder, "--film", folder / "film.js", "--kit", KIT,
           "--durasi", dur, "--fps", 24, "--musik", "sedang"])
    r = jalan([sys.executable, TOOLS / "slate.py", "tunggu", folder, "--maks", 900], capture_output=True)
    st = json.loads(r.stdout)
    ren = st.get("render") or {}
    q = ren.get("qa") or {}
    print("render: %s | QA lolos: %s" % (ren.get("state"), q.get("lolos")))
    if ren.get("error"):                        # mis. state data_gagal (cek data Slate sebelum render)
        print("ERROR: %s" % ren["error"])
    for m in ren.get("masalah") or []:
        print("MASALAH (cek data): %s" % m)
    for m in q.get("masalah") or []:
        print("MASALAH: " + m)
    for m in q.get("peringatan") or []:
        print("peringatan: " + m)
    print("lufs %s, lra %s, beku %s, loop %s, hening %s" % (q.get("lufs"), q.get("lra"), q.get("beku"), q.get("loop_selisih"), q.get("hening")))
    if st.get("final_lokal"):
        print("final: " + st["final_lokal"])
    return 0 if q.get("lolos") else 1


def cmd_qa(a):
    """Ringkasan QA render terakhir dari status.json (tanpa link berisi token)."""
    st = json.loads((Path(a.folder) / "status.json").read_text(encoding="utf-8"))
    ren = st.get("render") or {}
    q = ren.get("qa") or {}
    print("job %s | render %s | QA lolos %s | %s–%s" % (st.get("job_id"), ren.get("state"), q.get("lolos"), ren.get("mulai"), ren.get("selesai")))
    for k in ("durasi", "fps", "lufs", "peak_dbfs", "lra", "beku", "hitam", "loop_selisih", "hening", "kedip"):
        print("  %-13s %s" % (k, q.get(k)))
    for m in q.get("masalah") or []:
        print("MASALAH: " + m)
    for m in q.get("peringatan") or []:
        print("peringatan: " + m)
    for x in q.get("sinkron") or []:
        if x.get("lolos") is False:
            print("  tidak sinkron: %s gambar %.3f bunyi %s (%+d ms, %s)" % (x["cue"], x["gambar_s"], x.get("bunyi_s"), x.get("selisih_ms") or 0, x.get("cara")))
    for x in q.get("kontras") or []:
        print("  kontras %s di %s: %s:1 %s" % (x["teks"], x["latar"], x["rasio"], "✔" if x["lolos"] else "✘"))
    return 0 if q.get("lolos") else 1


def cmd_compliance(a):
    """OCR frame final.mp4: disclosure di setiap frame, tanpa Rp/%/diskon, angka asing ditandai (tools/qa_compliance.py)."""
    if not VENV_PY.exists():
        raise ProduksiError("venv belum ada (rembg + rapidocr_onnxruntime)")
    r = subprocess.run([str(VENV_PY), str(TOOLS / "qa_compliance.py"), "video", str(a.folder)], cwd=AKAR)
    return r.returncode


class kunci_log_unggah:
    """flock bersama atas uploads/.upload_log.lock: paket-unggah (di sini) dan konsol web (tarik, tandai terunggah)
    menulis ulang upload_log.csv hanya sambil memegangnya, jadi baris tidak hilang saat keduanya menulis bersamaan."""

    def __init__(self, log):
        self.path = Path(log).parent / ".upload_log.lock"

    def __enter__(self):
        import fcntl
        self.f = open(self.path, "a")
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        self.f.close()


def tulis_log_unggah(log, kolom, rows):
    import csv
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=kolom)
    w.writeheader()
    w.writerows(rows)
    tmp = Path(log).with_suffix(".tmp")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    tmp.replace(log)


def video_id(folder):
    st = json.loads((Path(folder) / "status.json").read_text(encoding="utf-8"))
    return "%s-%s" % (meta(folder)["produk"], st["job_id"])


def cmd_paket_unggah(a):
    """Video yang disetujui pemilik → <paket>/unggah/<video_id>/ (mp4, caption, meta) + baris uploads/upload_log.csv
    (format paket data sesi Chrome) berstatus siap_unggah. Mensyaratkan QA Slate dan QA compliance lolos."""
    import csv
    import datetime
    import shutil
    folder = Path(a.folder)
    m = meta(folder)
    st = json.loads((folder / "status.json").read_text(encoding="utf-8"))
    if not ((st.get("render") or {}).get("qa") or {}).get("lolos"):
        raise ProduksiError("QA Slate belum lolos")
    qc = folder / "qa_compliance.json"
    if not qc.exists() or not json.loads(qc.read_text(encoding="utf-8")).get("lolos"):
        raise ProduksiError("QA compliance belum lolos (python3 tools/produksi.py <folder> compliance)")
    produk = json.loads((folder / "produk.json").read_text(encoding="utf-8"))["produk"]
    vid = video_id(folder)
    tujuan = Path(m["paket"]) / "unggah" / vid
    tujuan.mkdir(parents=True, exist_ok=True)
    shutil.copy(folder / "final.mp4", tujuan / (vid + ".mp4"))
    caption = (folder / "teks_post.txt").read_text(encoding="utf-8").strip()
    (tujuan / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    info = {"video_id": vid, "variant_id": m.get("variant_id"), "product_id": produk["id"], "nama": produk["nama"],
            "affiliate_link": produk["link"], "job_id": st["job_id"], "durasi_s": ((st.get("render") or {}).get("qa") or {}).get("durasi"),
            "disetujui": datetime.datetime.now().isoformat(timespec="seconds"), "platform": a.platform}
    (tujuan / "meta.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    log = Path(m["paket"]) / "uploads" / "upload_log.csv"
    log.parent.mkdir(parents=True, exist_ok=True)
    berkas = str(tujuan / (vid + ".mp4"))
    kolom = ["timestamp", "product_id", "video_file", "platform", "caption", "affiliate_link", "status", "post_url", "notes"]
    with kunci_log_unggah(log):
        rows = []
        if log.exists() and log.stat().st_size:
            with open(log, newline="", encoding="utf-8") as f:
                rd = csv.DictReader(f)
                kolom, rows = rd.fieldnames, list(rd)
        lama = [r for r in rows if (r.get("video_file"), r.get("platform")) == (berkas, a.platform)]
        if not lama:
            rows.append(dict(zip(kolom, [info["disetujui"], produk["id"], berkas, a.platform, caption, produk["link"],
                                         "siap_unggah", "", "video_id=" + vid])))
        for r in lama:                 # disetujui lagi setelah ditarik (ditolak/ulang): tawarkan lagi
            if r.get("status") == "ditarik":
                r.update(status="siap_unggah", timestamp=info["disetujui"], caption=caption)
        tulis_log_unggah(log, kolom, rows)
    print("paket unggah: %s" % tujuan)
    return 0


def cmd_sheet(a):
    folder = Path(a.folder)
    from PIL import Image, ImageDraw
    import tempfile
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(folder / "final.mp4")], capture_output=True, text=True, check=True).stdout)
    waktu = [round(dur * i / 20, 2) for i in range(20)]
    sheet = Image.new("RGB", (10 * 270, 2 * 505), "#222")
    d = ImageDraw.Draw(sheet)
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(waktu):
            f = Path(tmp) / ("%02d.jpg" % i)
            subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(folder / "final.mp4"), "-frames:v", "1",
                            "-vf", "scale=270:480", str(f)], check=True)
            x, y = (i % 10) * 270, (i // 10) * 505
            with Image.open(f) as im:
                sheet.paste(im, (x, y))
            d.text((x + 6, y + 485), "t=%.2f" % t, fill="white")
    sheet.save(folder / "final_sheet.jpg", quality=88)
    print("%s/final_sheet.jpg (baca tanpa suara → cek_akhir.md)" % folder)
    return 0


LANGKAH = [("produksi.json", "init"), ("foto_sheet.jpg", "init"), ("cutout_sheet.jpg", "cutout"), ("aset/foto.js", "cutout"),
           ("naskah.txt", "naskah"), ("vo.json", "vo"), ("kata_koreksi.json", "vo"), ("brief.md", "brief"),
           ("pratinjau_r1.jpg", "pratinjau r1"), ("pratinjau_r2.jpg", "pratinjau r2"), ("score.json", "skor"),
           ("ledger.md", "ledger"), ("final.mp4", "render"), ("qa_compliance.json", "compliance"), ("final_sheet.jpg", "sheet"),
           ("cek_akhir.md", "cek akhir"), ("teks_post.txt", "teks post"), ("biaya.json", "biaya")]


def keadaan(folder):
    """belum | berjalan | gagal | selesai | disetujui | ditolak | ulang — dibaca konsol web dan status --json."""
    folder = Path(folder)
    run = AKAR / "logs" / ".produksi.run"
    try:
        di_penanda = run.read_text(encoding="utf-8", errors="replace").split()[2] == str(folder)
    except (OSError, IndexError):
        di_penanda = False
    if di_penanda and kunci_dipegang():
        return "berjalan"
    rv = folder / "review.json"
    if rv.exists():
        st = json.loads(rv.read_text(encoding="utf-8")).get("status")
        if st in ("disetujui", "ditolak", "ulang"):
            return st
    if (folder / "GAGAL.md").exists():
        return "gagal"
    if (folder / "final.mp4").exists() and (folder / "cek_akhir.md").exists():
        return "selesai"
    return "belum" if not (folder / "naskah.txt").exists() else "terhenti"


def cmd_status(a):
    folder = Path(a.folder)
    if a.json:
        print(json.dumps({"keadaan": keadaan(folder), "langkah": [{"file": f, "langkah": l, "ada": (folder / f).exists()} for f, l in LANGKAH]}))
        return 0
    print("keadaan: " + keadaan(folder))
    for f, langkah in LANGKAH:
        print("%s %-18s %s" % ("✔" if (folder / f).exists() else "·", langkah, f))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    if argv and argv[0] == "init":
        ap.add_argument("cmd")
        ap.add_argument("--paket", required=True)
        ap.add_argument("--produk", required=True)
        ap.add_argument("--folder")
        ap.add_argument("--baru", action="store_true", help="naskah dan voiceover baru: folder lama diarsipkan utuh ke produksi/_arsip/")
        a = ap.parse_args(argv)
        fn = cmd_init
    else:
        ap.add_argument("folder")
        sub = ap.add_subparsers(dest="cmd", required=True)
        s = sub.add_parser("cutout")
        s.add_argument("--foto", required=True, type=int)
        s.add_argument("--nama", required=True)
        s.add_argument("--crop")
        s.add_argument("--model", choices=["isnet-general-use", "u2net", "u2netp", "silueta"],
                       help="model rembg (bawaan isnet-general-use; u2net kadang lebih baik untuk produk gelap)")
        for n in ("naskah", "kata", "audit", "skor", "render", "qa", "compliance", "sheet"):
            sub.add_parser(n)
        s = sub.add_parser("status")
        s.add_argument("--json", action="store_true")
        s = sub.add_parser("paket-unggah")
        s.add_argument("--platform", default="shopee_video", choices=["shopee_video", "tiktok", "threads"])
        s = sub.add_parser("vo")
        s.add_argument("--voice")
        s = sub.add_parser("pratinjau")
        s.add_argument("--t", required=True)
        s.add_argument("--keluar", required=True)
        s.add_argument("--kol")
        s.add_argument("--slate", action="store_true")
        a = ap.parse_args(argv)
        fn = {"cutout": cmd_cutout, "naskah": cmd_naskah, "vo": cmd_vo, "kata": cmd_kata, "audit": cmd_audit,
              "pratinjau": cmd_pratinjau, "skor": cmd_skor, "render": cmd_render, "qa": cmd_qa, "compliance": cmd_compliance,
              "paket-unggah": cmd_paket_unggah, "sheet": cmd_sheet,
              "status": cmd_status}[a.cmd]
    try:
        return fn(a)
    except (ProduksiError, paket.PaketError, OSError, ValueError) as e:
        print("gagal: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
