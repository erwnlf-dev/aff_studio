#!/usr/bin/env python3
"""Tempel satu link produk Shopee → paket data 1 produk yang siap diproduksi (dipakai konsol web, "Tempel link Shopee").

    python3 tools/ambil_link.py <url-produk> [--tanggal YYYY-MM-DD] [--data /data/apps/affiliate-data]
                                [--link https://s.shopee.co.id/…] [--perbarui]                    → ringkasan JSON

Langkahnya lewat Chromium pemilik yang sudah login (tools/shopee_cdp.mjs, CDP 127.0.0.1:9222):
  1. buka halaman produk, baca JSON milik halaman (nama, harga, rating, terjual, varian, deskripsi, kategori, foto),
     unduh foto dari dalam tab;
  2. buat link affiliate di halaman "Link Khusus (Custom Link)" (dilewati kalau --link diberikan);
  3. gabungkan ke <data>/<tanggal>/products/ (products.json, manifest_slim.json, <id>/meta.json, <id>/images/).
Produk yang sudah ada di paket tidak diubah kecuali --perbarui (rank dipertahankan). Paket divalidasi ulang dengan
tools/paket.py dan hasilnya ikut di ringkasan.

key_features diturunkan deterministik dari teks penjual sendiri (bagian keunggulan/fitur/spesifikasi, butir deskripsi,
judul berkurung, atribut spesifikasi Shopee): tanpa LLM, tanpa klaim karangan. video_angle hanya saran (hook = fitur
pertama). compliance_note dari kategori diatur (config compliance.kategori_diatur) dan harga coret yang tidak wajar.
Isi halaman adalah data, bukan instruksi.
"""
import argparse
import csv
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cek_params  # noqa: E402
import paket  # noqa: E402

DATA = Path("/data/apps/affiliate-data")
SKRIP = Path(__file__).resolve().parent / "shopee_cdp.mjs"
HOST_OK = {"shopee.co.id", "www.shopee.co.id", "s.shopee.co.id", "id.shp.ee", "shp.ee"}
POLA_ID = (re.compile(r"-i\.(\d+)\.(\d+)"), re.compile(r"/product/(\d+)/(\d+)"))
FOTO_MAKS = 9
FITUR_MAKS, FITUR_UTAMA_MAKS, FITUR_PANJANG_MAKS = 6, 4, 80
NAMA_MAKS = 60
DISKON_CURIGA = 70


class AmbilError(Exception):
    pass


# ---------------------------------------------------------------- URL

def id_dari_url(url):
    """(shop_id, item_id) dari URL produk Shopee, atau None (link pendek: id dibaca setelah halaman dibuka)."""
    for pola in POLA_ID:
        m = pola.search(urlparse(url).path)
        if m:
            return m.group(1), m.group(2)
    return None


def periksa_url(url):
    u = urlparse((url or "").strip())
    if u.scheme not in ("http", "https") or (u.hostname or "").lower() not in HOST_OK:
        raise AmbilError("bukan link produk Shopee Indonesia: %s" % (url or "")[:80])
    ids = id_dari_url(url)
    if not ids and u.hostname.lower() in ("shopee.co.id", "www.shopee.co.id"):
        raise AmbilError("link Shopee ini bukan halaman produk (tidak ada id toko/produk): %s" % url[:80])
    return ids


POLA_ITEM, POLA_TOKO = re.compile(r"\d{5,20}"), re.compile(r"\d{1,20}")
HOST_PRODUK = {"shopee.co.id", "www.shopee.co.id"}


def periksa_item(it, ids, url_akhir):
    """(shop_id, item_id) dari data halaman, divalidasi SEBELUM apa pun ditulis (review 22 Okt): id harus angka
    (dipakai sebagai nama folder), sama dengan id di URL yang ditempel kalau ada, dan halaman akhir (setelah redirect
    link pendek) harus halaman produk shopee.co.id dengan id yang sama."""
    toko, item = str(it.get("shop_id") or ""), str(it.get("item_id") or "")
    if not POLA_ITEM.fullmatch(item) or not POLA_TOKO.fullmatch(toko):
        raise AmbilError("id produk/toko dari halaman tidak valid: %r / %r" % (item[:30], toko[:30]))
    if ids and (toko, item) != (str(ids[0]), str(ids[1])):
        raise AmbilError("halaman menampilkan produk lain (%s.%s) dari link yang ditempel (%s.%s)" % (toko, item, ids[0], ids[1]))
    u = urlparse(url_akhir or "")
    if u.scheme != "https" or (u.hostname or "").lower() not in HOST_PRODUK:
        raise AmbilError("halaman akhir bukan shopee.co.id: %s" % (url_akhir or "?")[:80])
    akhir = id_dari_url(url_akhir)
    if akhir and (str(akhir[0]), str(akhir[1])) != (toko, item):
        raise AmbilError("id di halaman akhir (%s.%s) tidak sama dengan data produk (%s.%s)" % (akhir[0], akhir[1], toko, item))
    return toko, item


def url_produk(shop_id, item_id):
    return "https://shopee.co.id/product/%s/%s" % (shop_id, item_id)


# ---------------------------------------------------------------- CDP

def cdp_node(perintah, *argumen, timeout=180):
    """Jalankan tools/shopee_cdp.mjs; keluarannya satu objek JSON. Tes mengganti fungsi ini."""
    node = shutil.which("node")
    if not node:
        raise AmbilError("node tidak ada di PATH")
    try:
        r = subprocess.run([node, str(SKRIP), perintah, *argumen], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AmbilError("CDP %s melewati %d s" % (perintah, timeout))
    try:
        hasil = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AmbilError("CDP %s gagal: %s" % (perintah, (r.stderr or r.stdout)[-300:]))
    if hasil.get("error"):
        raise AmbilError("CDP %s: %s" % (perintah, hasil["error"]))
    return hasil


# ---------------------------------------------------------------- teks → data

def angka_rp(teks):
    """'Rp32.900' / 'Rp26.900 - Rp34.900' → 32900 (batas bawah)."""
    m = re.search(r"Rp\s?([\d.]+)", teks or "")
    return int(m.group(1).replace(".", "")) if m else None


def angka_singkat(teks):
    """'266,1RB' → 266100, '1,2JT' → 1200000, '512' → 512."""
    m = re.match(r"^\s*([\d.,]+)\s*(RB|JT)?\+?\s*$", teks or "", re.I)
    if not m:
        return None
    n = float(m.group(1).replace(".", "").replace(",", "."))
    return int(round(n * {"RB": 1e3, "JT": 1e6}.get((m.group(2) or "").upper(), 1)))


def nama_pendek(judul):
    """Judul toko yang panjang/berisi kata kunci → nama ≤ 60 karakter (tanpa [TAG]/【TAG】/(HF) di depan, bagian
    pertama sebelum ' | ', potong di batas kata)."""
    s = re.sub(r"\[[^\]]*\]|【[^】]*】|^\s*\([A-Z0-9+ ]{1,6}\)", " ", judul or "")
    s = re.sub(r"\s+", " ", s).strip(" -|")
    awal = s.split(" | ")[0].strip()
    if len(awal) >= 15:
        s = awal
    if len(s) <= NAMA_MAKS:
        return s
    potong = s[:NAMA_MAKS + 1].rsplit(" ", 1)[0]
    return potong.rstrip(" -|,&/")


JUDUL_FITUR = re.compile(r"keunggulan|kelebihan|benefit|manfaat|fitur|feature|spesifikasi|specification|spec\b|detail|"
                         r"kandungan|komposisi|bahan", re.I)
JUDUL_ISI = re.compile(r"isi paket|isi dalam|isi kemasan|aksesori|kelengkapan|package|dalam kotak|in the box", re.I)
JUDUL_BUANG = re.compile(r"cara|pakai|penggunaan|penyajian|pengiriman|kirim|catatan|note|penting|perhatian|garansi|klaim|"
                         r"komplain|retur|kata kunci|keyword|hashtag|tag\b|shade|warna|varian|variasi|pilihan|jam|operasional|"
                         r"info toko|tentang kami|disclaimer|faq|syarat", re.I)
BARIS_BUANG = re.compile(r"https?:|www\.|@|#|shopee|order|pesan|chat|admin|toko|voucher|diskon|promo|ongkir|murah|"
                         r"komplain|retur|unboxing|video|resi|kirim|\bstok|ready|terima ?kasih|follow|jangan lupa|"
                         r"original|\bori\b|garansi|klaim|checkout|keranjang|harga", re.I)
KUNCI_BUANG = re.compile(r"^(nama )?produk$|diimpor|distribusi|diproduksi|produsen|kata kunci|merek|brand|stok|dikirim|"
                         r"asal|kedaluwarsa|expired|exp\b|sku|kode", re.I)
KUNCI_SPEK = re.compile(r"ukuran|dimensi|bahan|material|berat|netto|isi\b|volume|kapasitas|daya|baterai|battery|watt|"
                        r"bpom|izin edar|komposisi|panjang|lebar|tinggi|jumlah", re.I)
ATRIBUT_OK = re.compile(r"^(bahan|berat produk|volume|ukuran|kapasitas|komposisi|kapasitas baterai|daya|"
                        r"no\. izin edar.*|masa penyimpanan)$", re.I)
BUTIR = re.compile(r"^\s*(?:[-•*·▪●○◆◇►➤➢✓✔✅☑️✨🔥⭐️💯]+|\d{1,2}[.)])\s*")
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️]")


def _bersih(teks):
    s = EMOJI.sub("", BUTIR.sub("", teks or ""))
    s = re.sub(r"\s+", " ", s).strip(" .;-–—")
    s = re.sub(r"\s*:\s*", ": ", s, count=1) if re.search(r"\S\s*:\s*\S", s) else s
    if len(s) > 70:
        s = re.split(r"[,;]| - | – ", s)[0].strip(" .")
    return s


def _judul(baris):
    """Baris judul bagian: 'Benefit :', 'SPESIFIKASI PRODUK', '(Daya Pendinginan Instan)' → (teks, berkurung) atau None."""
    s = EMOJI.sub("", baris).strip()
    m = re.match(r"^\((.{3,45})\)$", s)
    if m:
        return m.group(1).strip(), True
    if re.match(r"^[^:.!?]{2,80}\s*:$", s):
        return s.rstrip(" :"), False
    if len(s) <= 40 and s.isupper() and re.search(r"[A-Z]{3}", s) and not re.search(r"\d", s):
        return s, False
    return None


def fitur_dari(deskripsi, atribut=(), nama=""):
    """3–6 fitur pendek dari teks penjual sendiri. Urutan prioritas: (1) butir di bagian keunggulan/fitur/spesifikasi dan
    judul berkurung (maks 4), (2) butir deskripsi lain dan baris spesifikasi 'Ukuran: …', sisa (1), (3) baris 'kunci: nilai'
    lain dan atribut Shopee, (4) baris pendek lain. Bagian cara pakai/pengiriman/catatan/varian dan baris promo/toko dibuang."""
    calon = []          # (prioritas, urutan, teks)
    bagian = "umum"
    nama_l = (nama or "").lower()
    for n, mentah in enumerate((deskripsi or "").splitlines()):
        if not mentah.strip():
            continue
        j = _judul(mentah)
        if j:
            teks, berkurung = j
            if berkurung and not JUDUL_BUANG.search(teks) and not BARIS_BUANG.search(teks):
                calon.append((1, n, teks))
                bagian = "berkurung"
                continue
            bagian = ("buang" if JUDUL_BUANG.search(teks) else "isi" if JUDUL_ISI.search(teks)
                      else "fitur" if JUDUL_FITUR.search(teks) else "umum")
            continue
        if bagian == "buang" or BARIS_BUANG.search(mentah):
            continue
        butir = bool(BUTIR.match(mentah))
        s = _bersih(mentah)
        if ":" in s:
            kunci = s.split(":", 1)[0].strip()
            if KUNCI_BUANG.search(kunci) or JUDUL_BUANG.search(kunci) and not KUNCI_SPEK.search(kunci):
                continue
            prio = 2 if KUNCI_SPEK.search(kunci) else 3
        elif bagian == "fitur":
            prio = 1
        elif bagian == "isi":
            prio = 4
        elif butir:
            prio = 2
        elif bagian == "umum" and len(s) <= 60 and not s.endswith((".", "!", "?")):
            prio = 4
        else:
            continue
        calon.append((prio, n, s))
    for k, a in enumerate(atribut or []):
        kunci, nilai = (a.get("name") or "").strip(), (a.get("value") or "").strip()
        if not ATRIBUT_OK.match(kunci) or nilai in ("", "-") or ("izin edar" in kunci.lower() and not re.search(r"\d", nilai)):
            continue
        calon.append((3, 10000 + k, "BPOM %s" % nilai if "izin edar" in kunci.lower() else "%s: %s" % (kunci, nilai)))

    sudah, terpilih = set(), []
    for prio, _, s in sorted(calon, key=lambda x: (x[0], x[1])):
        kunci = re.sub(r"[^a-z0-9]", "", s.lower())
        if not s or len(s) > FITUR_PANJANG_MAKS or len(s.split()) < 2 and ":" not in s or kunci in sudah:
            continue
        if kunci and (kunci in re.sub(r"[^a-z0-9]", "", nama_l)):
            continue
        sudah.add(kunci)
        terpilih.append((prio, s))
    utama = [s for p, s in terpilih if p == 1][:FITUR_UTAMA_MAKS]
    urut = [s for p, s in terpilih if p == 2] + [s for p, s in terpilih if p == 1 and s not in utama]
    urut += [s for p, s in terpilih if p > 2]
    return (utama + urut)[:FITUR_MAKS]


def kategori_dari(daftar):
    """['Perawatan & Kecantikan', 'Treatment Bibir', 'Pelembab Bibir'] → 'Perawatan & Kecantikan > Pelembab Bibir'
    (awalan + daun, format paket sesi Chrome)."""
    daftar = [d for d in daftar or [] if d]
    if not daftar:
        return ""
    return daftar[0] if len(daftar) == 1 else "%s > %s" % (daftar[0], daftar[-1])


def varian_dari(tier):
    return {t["name"]: list(t["options"]) for t in tier or [] if t.get("name") and len(t.get("options") or []) >= 2}


def catatan_compliance(kategori, diskon_persen, diatur):
    catatan = []
    if paket._awalan_diatur(kategori, diatur):
        catatan.append("Kategori diatur (%s): klaim hanya dari key_features penjual apa adanya; tanpa hook masalah/pain, "
                       "tanpa before/after, tanpa klaim medis/hasil instan." % kategori.split(" >")[0])
    if diskon_persen and diskon_persen >= DISKON_CURIGA:
        catatan.append("Harga coret -%d%% terindikasi inflasi diskon: jangan tonjolkan harga coret/%% diskon." % diskon_persen)
    return " ".join(catatan) or None


def susun_meta(d, link, rank, foto, params, sekarang):
    """Data mentah shopee_cdp.mjs → satu produk berskema paket sesi Chrome (CONTEXT.md §5 + field products.json)."""
    it, ld, dom = d["item"], d.get("ld") or {}, d.get("dom") or {}
    harga = int(float(ld["price"])) if ld.get("price") else angka_rp((dom.get("harga") or [None])[0])
    coret = angka_rp(dom["harga"][1]) if len(dom.get("harga") or []) > 1 else None
    if coret is not None and harga and coret <= harga:
        coret = None
    diskon = int(re.sub(r"\D", "", dom["diskon"])) if dom.get("diskon") else (
        round(100 * (1 - harga / coret)) if coret and harga else None)
    rating = round(float(ld["rating"]), 2) if ld.get("rating") else (float(dom["rating"]) if dom.get("rating") else None)
    ulasan = int(ld["rating_count"]) if ld.get("rating_count") else angka_singkat(dom.get("penilaian"))
    kategori = kategori_dari(it.get("categories") or d.get("breadcrumb"))
    nama = nama_pendek(it.get("title") or ld.get("name"))
    fitur = fitur_dari(it.get("description") or ld.get("description"), d.get("atribut"), nama)
    lokasi = (it.get("shop_location") or "").title() or None
    return {
        "rank": rank, "product_id": str(it["item_id"]), "shop_id": str(it["shop_id"]), "name": nama,
        "name_full": it.get("title"), "category": kategori,
        "category_path": list(it.get("categories") or d.get("breadcrumb") or []),
        "price": harga, "price_max": int(float(ld["price_max"])) if ld.get("price_max") else None,
        "price_before_discount": coret, "commission_rate": None, "est_commission_idr": None,
        "sold_30d": dom.get("terjual"), "sold_sumber": "halaman produk (total terjual)",
        "rating": rating, "reviews": ulasan,
        "shop_name": ld.get("seller"),
        "shop_type": "Mall" if it.get("is_official_shop") else "Star+" if it.get("is_preferred_plus_seller") else "regular",
        "location": lokasi, "has_video": bool(it.get("has_video")), "brand": it.get("brand") or None,
        "variants": varian_dari(it.get("tier_variations")),
        "key_features": fitur, "key_features_sumber": "otomatis dari deskripsi/spesifikasi penjual (ambil_link.py)",
        "video_angle": {"hook": fitur[0] if fitur else "", "pain_point": "", "usp": fitur[1:4],
                        "cta": "Cek keranjang oranye ya", "catatan": "saran otomatis; sutradara memilih sudut sendiri"},
        "compliance_note": catatan_compliance(kategori, diskon, params["compliance.kategori_diatur"]),
        "description_raw": it.get("description") or "",
        "cover": foto[0]["url"] if foto else None, "images": foto,
        "url": url_produk(it["shop_id"], it["item_id"]), "affiliate_link": link,
        "scraped_at": sekarang.strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "link_ready", "sumber": "tempel_link",
    }


# ---------------------------------------------------------------- foto & paket

def simpan_foto(mentah_dir, daftar, pid, tujuan):
    """Foto mentah (01.bin, …) → <tujuan>/<pid>_NN.jpg (dikonversi ke JPEG bila perlu). Foto rusak dilewati."""
    tujuan.mkdir(parents=True, exist_ok=True)
    out = []
    for f in daftar:
        if not f.get("berkas"):
            continue
        nama = "%s_%02d.jpg" % (pid, len(out) + 1)
        try:
            with Image.open(Path(mentah_dir) / f["berkas"]) as im:
                im.load()
                if im.format == "JPEG":
                    shutil.copyfile(Path(mentah_dir) / f["berkas"], tujuan / nama)
                else:
                    im.convert("RGB").save(tujuan / nama, "JPEG", quality=92)
        except (OSError, ValueError):
            continue
        out.append({"url": f["url"], "local": nama})
    return out


def _tulis_json(path, isi):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(isi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


SLIM = ("rank", "product_id", "name", "category", "price", "price_before_discount", "commission_rate",
        "est_commission_idr", "sold_30d", "rating", "reviews", "shop_name", "shop_type", "affiliate_link", "url",
        "variants", "key_features", "video_angle", "compliance_note")
KOLOM_SHORTLIST = ("rank", "product_id", "name", "price", "commission_%", "est_komisi_idr", "sold_30d", "rating",
                   "reviews", "shop_type", "score", "n_images", "url")


def gabung(akar, meta):
    """Tambahkan/perbarui satu produk di products.json, manifest_slim.json, shortlist.csv. Produk lain tidak disentuh."""
    prod = akar / "products"
    pj, sj = prod / "products.json", prod / "manifest_slim.json"
    semua = json.loads(pj.read_text(encoding="utf-8")) if pj.exists() else []
    slim = json.loads(sj.read_text(encoding="utf-8")) if sj.exists() else []
    if not isinstance(semua, list) or not isinstance(slim, list):
        raise AmbilError("products.json/manifest_slim.json paket ini bukan daftar; tidak diubah")
    pid = meta["product_id"]
    lama = next((p for p in semua if str(p.get("product_id")) == pid), None)
    if lama is not None:
        meta["rank"] = lama.get("rank", meta["rank"])
        semua = [meta if str(p.get("product_id")) == pid else p for p in semua]
    else:
        semua.append(meta)
    baris_slim = {k: meta.get(k) for k in SLIM}
    baris_slim["image_files"] = [i["local"] for i in meta["images"]]
    slim = [s for s in slim if str(s.get("product_id")) != pid] + [baris_slim]
    _tulis_json(prod / pid / "meta.json", meta)
    _tulis_json(sj, slim)
    _tulis_json(pj, semua)
    sl = prod / "shortlist.csv"
    baris = {"rank": meta["rank"], "product_id": pid, "name": meta["name"], "price": meta["price"],
             "commission_%": "", "est_komisi_idr": "", "sold_30d": meta["sold_30d"], "rating": meta["rating"],
             "reviews": meta["reviews"], "shop_type": meta["shop_type"], "score": "", "n_images": len(meta["images"]),
             "url": meta["url"]}
    if sl.exists():
        with open(sl, encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            kolom, isi = r.fieldnames or list(KOLOM_SHORTLIST), [x for x in r if x.get("product_id") != pid]
    else:
        kolom, isi = list(KOLOM_SHORTLIST), []
    isi.append({k: baris.get(k, "") for k in kolom})
    tmp = sl.with_suffix(".csv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        w.writeheader()
        w.writerows(isi)
    os.replace(tmp, sl)
    return lama is not None


def ambil(url, tanggal=None, data=DATA, link=None, perbarui=False, cdp=cdp_node, sekarang=None):
    """Satu link → produk di paket <data>/<tanggal>. Mengembalikan ringkasan (dict)."""
    tanggal = tanggal or date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", tanggal):
        raise AmbilError("tanggal harus YYYY-MM-DD: %s" % tanggal)
    if link and not paket.LINK_OK.match(link):
        raise AmbilError("--link bukan link Shopee: %s" % link[:80])
    ids = periksa_url(url)
    akar = Path(data) / tanggal
    if ids and not perbarui and _ada(akar, ids[1]):
        return _sudah_ada(akar, tanggal, ids[1])
    params = cek_params.resolve(cek_params.load())
    sekarang = sekarang or datetime.now(timezone.utc)
    with tempfile.TemporaryDirectory(prefix="ambil_link_") as tmp:
        d = cdp("produk", url_produk(*ids) if ids else url, "--gambar-ke", tmp, "--maks", str(FOTO_MAKS))
        it = d.get("item") or {}
        if not it.get("item_id") or not it.get("shop_id"):
            raise AmbilError("data produk tidak lengkap dari halaman")
        _, pid = periksa_item(it, ids, d.get("url_akhir"))
        if not ids and not perbarui and _ada(akar, pid):
            return _sudah_ada(akar, tanggal, pid)
        if not link:
            link = cdp("link", url_produk(it["shop_id"], pid)).get("link") or ""
            if not paket.LINK_OK.match(link):
                raise AmbilError("link affiliate tidak valid dari halaman Custom Link: %r" % link[:80])
        akar.mkdir(parents=True, exist_ok=True)
        with open(akar / ".ambil_link.lock", "w") as kunci:
            fcntl.flock(kunci, fcntl.LOCK_EX)
            semua = _baca_produk(akar)
            if not perbarui and any(str(p.get("product_id")) == pid for p in semua):
                return _sudah_ada(akar, tanggal, pid)
            rank = max([p.get("rank") or 0 for p in semua] + [0]) + 1
            folder_foto = akar / "products" / pid / "images"
            if perbarui and folder_foto.exists():
                shutil.rmtree(folder_foto)
            foto = simpan_foto(tmp, d.get("foto") or [], pid, folder_foto)
            meta = susun_meta(d, link, rank, foto, params, sekarang)
            diperbarui = gabung(akar, meta)
    hasil = {p["id"]: (p, dt, w) for p, dt, w in paket.muat(akar, params, sekarang)}
    p, ditolak, peringatan = hasil[pid]
    peringatan = ["key_features diturunkan otomatis dari deskripsi penjual: periksa sebelum produksi"] + peringatan
    return {"paket": str(akar), "tanggal": tanggal, "product_id": pid,
            "status": "diperbarui" if diperbarui else "ditambahkan", "nama": meta["name"], "kategori": meta["category"],
            "harga": meta["price"], "rating": meta["rating"], "ulasan": meta["reviews"], "terjual": meta["sold_30d"],
            "foto": len(foto), "link": meta["affiliate_link"], "key_features": meta["key_features"],
            "compliance_note": meta["compliance_note"], "siap": not ditolak, "ditolak": ditolak,
            "peringatan": peringatan}


def _baca_produk(akar):
    pj = akar / "products" / "products.json"
    return json.loads(pj.read_text(encoding="utf-8")) if pj.exists() else []


def _sudah_ada(akar, tanggal, pid):
    return {"paket": str(akar), "tanggal": tanggal, "product_id": str(pid), "status": "sudah_ada",
            "pesan": "produk sudah ada di paket %s (pakai --perbarui untuk menimpa)" % tanggal}


def _ada(akar, pid):
    return any(str(p.get("product_id")) == str(pid) for p in _baca_produk(akar))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url")
    ap.add_argument("--tanggal", help="folder paket (default hari ini)")
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--link", help="link affiliate yang sudah ada (lewati halaman Custom Link)")
    ap.add_argument("--perbarui", action="store_true", help="timpa produk yang sudah ada di paket (rank tetap)")
    a = ap.parse_args(argv)
    try:
        hasil = ambil(a.url, a.tanggal, Path(a.data), a.link, a.perbarui)
    except (AmbilError, paket.PaketError, OSError, ValueError, KeyError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(hasil, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
