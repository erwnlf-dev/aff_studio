#!/usr/bin/env python3
"""Cek config/video-params.yaml dan buat snapshot parameter + variant_id.

    python3 tools/cek_params.py                      # cek konsistensi registry (exit 1 kalau ada kesalahan)
    python3 tools/cek_params.py snapshot             # parameter aktif MVP + variant_id (JSON)
    python3 tools/cek_params.py snapshot --eksperimen EXP-02 --lengan C
    python3 tools/cek_params.py snapshot --set hook.tipe=pain --setujui template.pilih_per_kategori

Aturan yang dicek ada di doc 12 §2.2–2.3. variant_id adalah hash dari parameter yang dipakai saja, jadi dua video
dengan parameter identik selalu mendapat id yang sama, dari eksperimen mana pun asalnya.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parent.parent / "config" / "video-params.yaml"
STATUS = {"default", "eksperimen", "usulan"}
KUNCI = {"compliance", "qa"}
WAJIB = {"status", "nilai", "alasan", "sumber"}
BOLEH = WAJIB | {"rentang", "pilihan", "satuan", "kunci", "eksperimen"}
EKSP_WAJIB = {"judul", "status", "lengan", "metrik_utama", "unit", "sampel_min_per_lengan", "durasi_min_hari"}
EKSP_BOLEH = EKSP_WAJIB | {"metrik_diagnosis", "pengaman", "catatan", "syarat"}
EKSP_STATUS = {"antre", "siap", "jalan", "selesai", "dihentikan"}
KONTROL = "A"


def load(path=REGISTRY):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _angka(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def cek_nilai(spec, nilai):
    """Pesan kesalahan kalau nilai tidak sah menurut rentang/pilihan spec, atau None."""
    isi = nilai if isinstance(nilai, list) else [nilai]
    if isinstance(nilai, list) and not nilai:
        return "daftar kosong"
    if "rentang" in spec:
        lo, hi = spec["rentang"]
        for v in isi:
            if not _angka(v):
                return "%r bukan angka" % (v,)
            if not lo <= v <= hi:
                return "%r di luar rentang [%s, %s]" % (v, lo, hi)
    if "pilihan" in spec:
        for v in isi:
            if v not in spec["pilihan"]:
                return "%r tidak ada di pilihan %s" % (v, spec["pilihan"])
    return None


def validate(reg):
    """Daftar kesalahan registry; kosong berarti sah."""
    err = []
    params = reg.get("parameter") or {}
    eksp = reg.get("eksperimen") or {}
    rujukan = set(reg.get("sumber") or {}) | set(reg.get("hipotesis") or {})
    metrik = set(reg.get("metrik") or {})

    for nama, spec in params.items():
        p = "parameter %s" % nama
        if not isinstance(spec, dict):
            err.append("%s: harus berupa mapping" % p)
            continue
        for k in sorted(WAJIB - set(spec)):
            err.append("%s: field '%s' wajib" % (p, k))
        for k in sorted(set(spec) - BOLEH):
            err.append("%s: field '%s' tidak dikenal" % (p, k))
        if ("rentang" in spec) == ("pilihan" in spec):
            err.append("%s: isi tepat satu dari 'rentang' atau 'pilihan'" % p)
        if "rentang" in spec:
            r = spec["rentang"]
            if not (isinstance(r, list) and len(r) == 2 and all(_angka(x) for x in r) and r[0] <= r[1]):
                err.append("%s: rentang harus [min, max] angka dengan min <= max" % p)
                continue
        if spec.get("status") not in STATUS:
            err.append("%s: status %r bukan salah satu dari %s" % (p, spec.get("status"), sorted(STATUS)))
        if "kunci" in spec:
            if spec["kunci"] not in KUNCI:
                err.append("%s: kunci %r bukan salah satu dari %s" % (p, spec["kunci"], sorted(KUNCI)))
            if spec.get("status") == "eksperimen":
                err.append("%s: parameter berkunci tidak boleh berstatus eksperimen" % p)
        if "nilai" in spec:
            m = cek_nilai(spec, spec["nilai"])
            if m:
                err.append("%s: nilai %s" % (p, m))
        if not str(spec.get("alasan") or "").strip():
            err.append("%s: alasan kosong" % p)
        src = spec.get("sumber")
        if not isinstance(src, list) or not src:
            err.append("%s: sumber harus daftar yang tidak kosong" % p)
        else:
            for s in src:
                if s not in rujukan:
                    err.append("%s: sumber %r tidak ada di 'sumber' atau 'hipotesis'" % (p, s))
        if "eksperimen" in spec and spec["eksperimen"] not in eksp:
            err.append("%s: eksperimen %r tidak terdaftar" % (p, spec["eksperimen"]))
        if spec.get("status") == "eksperimen" and "eksperimen" not in spec:
            err.append("%s: status eksperimen tanpa id eksperimen" % p)

    for eid, e in eksp.items():
        p = "eksperimen %s" % eid
        if not isinstance(e, dict):
            err.append("%s: harus berupa mapping" % p)
            continue
        for k in sorted(EKSP_WAJIB - set(e)):
            err.append("%s: field '%s' wajib" % (p, k))
        for k in sorted(set(e) - EKSP_BOLEH):
            err.append("%s: field '%s' tidak dikenal" % (p, k))
        if e.get("status") not in EKSP_STATUS:
            err.append("%s: status %r bukan salah satu dari %s" % (p, e.get("status"), sorted(EKSP_STATUS)))
        for m in [e.get("metrik_utama")] + list(e.get("metrik_diagnosis") or []) + list(e.get("pengaman") or []):
            if m not in metrik:
                err.append("%s: metrik %r tidak ada di 'metrik'" % (p, m))
        lengan = e.get("lengan") or {}
        if KONTROL not in lengan:
            err.append("%s: lengan kontrol '%s' wajib" % (p, KONTROL))
        if len(lengan) < 2:
            err.append("%s: minimal 2 lengan" % p)
        kunci_set = None
        for nama_l, set_l in lengan.items():
            if not isinstance(set_l, dict) or not set_l:
                err.append("%s lengan %s: harus mapping parameter→nilai yang tidak kosong" % (p, nama_l))
                continue
            if kunci_set is None:
                kunci_set = set(set_l)
            elif set(set_l) != kunci_set:
                err.append("%s lengan %s: harus mengubah parameter yang sama dengan lengan lain" % (p, nama_l))
            for nama, v in set_l.items():
                spec = params.get(nama)
                if spec is None:
                    err.append("%s lengan %s: parameter %r tidak ada" % (p, nama_l, nama))
                    continue
                if "kunci" in spec:
                    err.append("%s lengan %s: parameter %s berkunci %s, tidak boleh diuji"
                               % (p, nama_l, nama, spec["kunci"]))
                if spec.get("status") != "eksperimen":
                    err.append("%s lengan %s: parameter %s harus berstatus eksperimen" % (p, nama_l, nama))
                m = cek_nilai(spec, v)
                if m:
                    err.append("%s lengan %s: %s %s" % (p, nama_l, nama, m))
                if nama_l == KONTROL and "nilai" in spec and v != spec["nilai"]:
                    err.append("%s: lengan kontrol %s = %r, harus sama dengan nilai registry %r"
                               % (p, nama, v, spec["nilai"]))
        if not (isinstance(e.get("sampel_min_per_lengan"), int) and e["sampel_min_per_lengan"] > 0):
            err.append("%s: sampel_min_per_lengan harus bilangan bulat > 0" % p)
    return err


def resolve(reg, overrides=None, disetujui=()):
    """Parameter aktif: default dan eksperimen memakai nilai registry, usulan hanya kalau disetujui.
    overrides menimpa nilai dan dicek terhadap rentang/pilihan serta kunci."""
    params = reg["parameter"]
    out = {}
    for nama, spec in params.items():
        if spec["status"] == "usulan" and nama not in disetujui:
            continue
        out[nama] = spec["nilai"]
    for nama, v in (overrides or {}).items():
        spec = params.get(nama)
        if spec is None:
            raise ValueError("parameter %r tidak ada" % nama)
        if spec["status"] == "usulan" and nama not in disetujui:
            raise ValueError("%s masih usulan; setujui dulu" % nama)
        if "kunci" in spec and v != spec["nilai"]:
            raise ValueError("%s berkunci %s; mengubahnya butuh ADR" % (nama, spec["kunci"]))
        m = cek_nilai(spec, v)
        if m:
            raise ValueError("%s: %s" % (nama, m))
        out[nama] = v
    return out


def variant_id(params):
    teks = json.dumps(params, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "v_" + hashlib.sha256(teks.encode("utf-8")).hexdigest()[:12]


def snapshot(reg, overrides=None, disetujui=(), eksperimen=None, lengan=None):
    ov = {}
    if eksperimen:
        e = reg["eksperimen"].get(eksperimen)
        if e is None:
            raise ValueError("eksperimen %r tidak ada" % eksperimen)
        if lengan not in e["lengan"]:
            raise ValueError("lengan %r tidak ada di %s (%s)" % (lengan, eksperimen, ", ".join(e["lengan"])))
        ov.update(e["lengan"][lengan])
    ov.update(overrides or {})
    params = resolve(reg, ov, disetujui)
    return {"variant_id": variant_id(params), "versi_skema": reg.get("versi_skema"),
            "eksperimen": {"id": eksperimen, "lengan": lengan} if eksperimen else None, "params": params}


def _pasangan(teks):
    if "=" not in teks:
        raise argparse.ArgumentTypeError("format nama=nilai")
    k, v = teks.split("=", 1)
    return k.strip(), yaml.safe_load(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", default=str(REGISTRY))
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("snapshot", help="parameter aktif + variant_id sebagai JSON")
    s.add_argument("--set", action="append", type=_pasangan, default=[], metavar="nama=nilai")
    s.add_argument("--setujui", action="append", default=[], metavar="nama", help="aktifkan parameter usulan")
    s.add_argument("--eksperimen")
    s.add_argument("--lengan")
    a = ap.parse_args(argv)

    reg = load(a.registry)
    err = validate(reg)
    if err:
        print("%d kesalahan di %s:" % (len(err), a.registry), file=sys.stderr)
        for m in err:
            print("  - " + m, file=sys.stderr)
        return 1
    if a.cmd == "snapshot":
        try:
            out = snapshot(reg, dict(a.set), a.setujui, a.eksperimen, a.lengan)
        except ValueError as e:
            print("ditolak: %s" % e, file=sys.stderr)
            return 2
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    n = reg["parameter"]
    hit = {st: sum(1 for x in n.values() if x["status"] == st) for st in sorted(STATUS)}
    print("ok: %d parameter (%s), %d berkunci, %d eksperimen" % (
        len(n), ", ".join("%s %d" % kv for kv in hit.items()),
        sum(1 for x in n.values() if "kunci" in x), len(reg.get("eksperimen") or {})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
