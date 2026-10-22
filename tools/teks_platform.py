#!/usr/bin/env python3
"""Teks per platform untuk satu video (doc 16 §2): cek teks_platform.json di folder kerja.

    python3 tools/teks_platform.py <folder kerja>          # cek; menulis teks_post.txt (caption Shopee + disclosure)

teks_platform.json:
    {"shopee_video": {"caption": "..."},
     "tiktok":       {"caption": "... #a #b #c"},
     "threads":      {"teks": "...\\n🔊 Narasi: suara AI", "topik": "Rumah Tangga", "balasan": "Link: {LINK} (link afiliasi)"}}

Platform yang wajib ada mengikuti produksi.json "platform" (semua = ketiganya). Keluar 0 = lolos, 1 = ada pelanggaran
(dicetak), 2 = berkas tidak terbaca.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_compliance  # noqa: E402

PLATFORM_WAJIB = {"semua": ("shopee_video", "tiktok", "threads"), "shopee_video": ("shopee_video",),
                  "tiktok": ("tiktok",), "threads": ("threads",)}
CAPTION_SHOPEE = 150            # batas form Shopee Video (diamati 22 Okt 2026)
CAPTION_TIKTOK = 2200           # API TikTok (UTF-16), praktis jauh di bawahnya
THREADS_BYTE = 500              # Threads: 500, emoji dihitung per byte UTF-8 (doc 16)
HASHTAG = re.compile(r"#[\w]+", re.U)
LINK = re.compile(r"https?://|www\.|s\.shopee", re.I)
LABEL_AI = re.compile(r"suara\s+ai|narasi\s+ai|ai\s+voice", re.I)


def umum(nama, teks, sah):
    salah = []
    for rx, kata in qa_compliance.TERLARANG:
        if rx.search(teks):
            salah.append("%s: kata terlarang '%s' (tanpa harga, diskon, promo, gratis, termurah)" % (nama, kata))
    asing = sorted(v for v in qa_compliance.angka(teks) if v not in sah)
    if asing:
        salah.append("%s: angka %s tidak ada di data produk/naskah" % (nama, ", ".join("%g" % v for v in asing)))
    if re.search(r"\b(kenal(in|kan)|perkenalkan|fun fact)\b", teks, re.I) or "—" in teks:
        salah.append("%s: hindari 'Kenalin', 'Fun fact', dan tanda pisah panjang (suara manusia, doc 15)" % nama)
    return salah


def cek(folder):
    folder = Path(folder)
    d = json.loads((folder / "teks_platform.json").read_text(encoding="utf-8"))
    try:
        platform = json.loads((folder / "produksi.json").read_text(encoding="utf-8")).get("platform") or "semua"
    except (OSError, ValueError):
        platform = "semua"
    sah = qa_compliance.sumber_angka(folder)
    salah = []
    for p in PLATFORM_WAJIB.get(platform, PLATFORM_WAJIB["semua"]):
        if not isinstance(d.get(p), dict):
            salah.append("%s: tidak ada (platform tujuan %s)" % (p, platform))

    s = (d.get("shopee_video") or {}).get("caption")
    if s is not None:
        s = s.strip()
        if not s or len(s) > CAPTION_SHOPEE:
            salah.append("shopee_video.caption: %d karakter, harus 1–%d (tidak bisa diedit setelah posting)" % (len(s), CAPTION_SHOPEE))
        if LINK.search(s) or re.search(r"\b(link|bio)\b", s, re.I):
            salah.append("shopee_video.caption: tanpa link/bio (produk ada di keranjang oranye)")
        salah += umum("shopee_video.caption", s, sah)

    t = (d.get("tiktok") or {}).get("caption")
    if t is not None:
        t = t.strip()
        tag = HASHTAG.findall(t)
        if not t or len(t) > CAPTION_TIKTOK:
            salah.append("tiktok.caption: kosong atau > %d karakter" % CAPTION_TIKTOK)
        if not 3 <= len(tag) <= 5:
            salah.append("tiktok.caption: %d hashtag, harus 3–5 yang spesifik" % len(tag))
        if any(x.lower() in ("#fyp", "#foryou", "#foryoupage", "#viral", "#xyzbca") for x in tag):
            salah.append("tiktok.caption: tanpa #fyp/#viral (hashtag generik)")
        m = re.search(r"\b(shopee|link|bio|keranjang oranye)\b", t, re.I) or LINK.search(t)
        if m:
            salah.append("tiktok.caption: %r dilarang (TikTok Shop melarang ajakan ke luar platform, doc 16)" % m.group(0))
        badan = HASHTAG.sub("", t).strip().split("\n")[0]
        if len(badan.split()) < 3:
            salah.append("tiktok.caption: kalimat pertama harus berisi kata kunci produk (TikTok SEO)")
        salah += umum("tiktok.caption", t, sah)

    th = d.get("threads")
    if isinstance(th, dict):
        teks, topik, balas = (th.get("teks") or "").strip(), (th.get("topik") or "").strip(), (th.get("balasan") or "").strip()
        if not teks or len(teks.encode("utf-8")) > THREADS_BYTE:
            salah.append("threads.teks: %d byte UTF-8, harus 1–%d (emoji dihitung per byte)" % (len(teks.encode("utf-8")), THREADS_BYTE))
        if LINK.search(teks) or "{LINK}" in teks:
            salah.append("threads.teks: link di balasan pertama, bukan di badan post (doc 16)")
        if HASHTAG.search(teks):
            salah.append("threads.teks: tanpa hashtag; pakai 'topik' (satu topic tag)")
        if not LABEL_AI.search(teks):
            salah.append("threads.teks: tulis baris narasi suara AI, mis. '🔊 Narasi: suara AI' (Meta mewajibkan label; API tidak bisa)")
        if not 1 <= len(topik) <= 50 or re.search(r"[.&#]", topik):
            salah.append("threads.topik: 1–50 karakter, tanpa '.', '&', '#'")
        if "{LINK}" not in balas or not re.search(r"afiliasi", balas, re.I):
            salah.append("threads.balasan: harus memuat {LINK} dan kata 'afiliasi' (link afiliasi = branded content)")
        if len(balas.replace("{LINK}", "x" * 32).encode("utf-8")) > THREADS_BYTE:
            salah.append("threads.balasan: terlalu panjang")
        salah += umum("threads.teks", teks, sah) + umum("threads.balasan", balas.replace("{LINK}", ""), sah)
    return d, salah


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip())
        return 2
    folder = Path(argv[0])
    try:
        d, salah = cek(folder)
    except (OSError, ValueError) as e:
        print("teks_platform.json tidak terbaca: %s" % e)
        return 2
    for s in salah:
        print("GAGAL " + s)
    if salah:
        return 1
    cap = ((d.get("shopee_video") or {}).get("caption") or (d.get("tiktok") or {}).get("caption") or "").strip()
    (folder / "teks_post.txt").write_text(cap + "\n(link afiliasi)\n", encoding="utf-8")     # konsol lama / paket unggah
    print("teks platform LOLOS (%s); teks_post.txt ditulis dari caption Shopee" % ", ".join(sorted(k for k in d if isinstance(d[k], dict))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
