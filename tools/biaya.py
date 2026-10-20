#!/usr/bin/env python3
"""Log biaya satu video → <folder>/biaya.json (TODO §6 butir 9). Dipanggil run_produksi.sh setelah sesi.

    python3 tools/biaya.py <folder produksi> [transkrip sesi .jsonl]

Isi: biaya sesi kreator (USD dari event `result` transkrip stream-json, turn, durasi), karakter ElevenLabs (vo.json),
jumlah render (final.mp4 + final_r*.mp4), durasi render terakhir (status.json mulai→selesai), dan durasi video.
"""
import datetime
import json
import sys
from pathlib import Path


def sesi(jsonl):
    out = {}
    for line in Path(jsonl).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "result":
            out = {"biaya_usd": d.get("total_cost_usd"), "turn": d.get("num_turns"), "durasi_s": round((d.get("duration_ms") or 0) / 1000),
                   "berhasil": d.get("subtype") == "success"}
        if d.get("type") == "system" and d.get("subtype") == "init":
            out.setdefault("model", d.get("model"))
    return out


def hitung(folder, jsonl=None):
    folder = Path(folder)
    b = {"dicatat": datetime.datetime.now().isoformat(timespec="seconds")}
    if jsonl and Path(jsonl).exists():
        b["sesi"] = sesi(jsonl)
    vo = folder / "vo.json"
    if vo.exists():
        v = json.loads(vo.read_text(encoding="utf-8"))
        b["tts"] = {"karakter": v.get("karakter_terpakai"), "durasi_vo_s": v.get("durasi"), "job_id": v.get("job_id")}
    b["render"] = {"jumlah": len(list(folder.glob("final_r*.mp4"))) + (folder / "final.mp4").exists()}
    st = folder / "status.json"
    if st.exists():
        r = json.loads(st.read_text(encoding="utf-8")).get("render") or {}
        if r.get("mulai") and r.get("selesai"):
            b["render"]["terakhir_s"] = round((datetime.datetime.fromisoformat(r["selesai"]) - datetime.datetime.fromisoformat(r["mulai"])).total_seconds())
        b["render"]["durasi_video_s"] = (r.get("qa") or {}).get("durasi")
    lama = folder / "biaya.json"
    if lama.exists() and "sesi" not in b:                  # catatan ulang tanpa transkrip: pertahankan biaya sesi lama
        b["sesi"] = json.loads(lama.read_text(encoding="utf-8")).get("sesi")
    lama.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    return b


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(2)
    print(json.dumps(hitung(*sys.argv[1:]), ensure_ascii=False))
