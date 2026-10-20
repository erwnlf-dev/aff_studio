"""
cek_sesi: check a headless Claude Code run from its --output-format stream-json transcript.

    python3 tools/cek_sesi.py logs/<run>.jsonl claude-opus-5-5
    python3 tools/cek_sesi.py --batas logs/<run>.jsonl     did the run stop on a Claude usage/rate limit? (JSON)

Prints one line per finding. "MASALAH ..." lines make the run invalid (exit 1): no init/result event,
another model did the work, the session ended in an error, or it hit a Claude usage
limit. "CATATAN ..." lines are informational (denied tool calls, cost, a usage-limit warning). Haiku is allowed:
WebFetch uses it to read pages. A usage limit also prints one "BATAS {json}" line (same object as --batas).

Usage limits (the owner's Claude subscription, shared with his own Claude Code use) are read only from what the CLI
itself reports, never from tool results or the model's prose:
  - a `rate_limit_event` whose rate_limit_info.status is "rejected" (resetsAt = unix seconds of the reset,
    rateLimitType five_hour | seven_day | seven_day_opus | ...),
  - an assistant event with error "rate_limit" (the CLI's synthetic message "You've hit your session limit ·
    resets 3pm (Asia/Jakarta)", apiError "usage_limit_reached" with apiErrorParams.rate_limit_info.resetsAt),
  - an error result whose text says so ("You've hit your ... limit · resets ...", "usage limit reached",
    the older "Claude AI usage limit reached|<epoch>", "API Error: 429 ... rate_limit_error", "529 overloaded").
A run that ended successfully never counts as limited. --batas answers
    {"batas": true|false, "jenis": "pemakaian"|"sementara"|null, "jendela": "five_hour"|...|null,
     "reset": "2026-10-20T15:00:00+07:00"|null, "pesan": "..."}
jenis "pemakaian" = the subscription limit (reset time when the CLI gave one); "sementara" = an API rate limit or
overload (429/529) without a reset time. The batch runner (run_batch.sh) waits and retries the same episode.
"""
import datetime
import json
import re
import sys

WIB = datetime.timezone(datetime.timedelta(hours=7))
BULAN = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
TEKS_PEMAKAIAN = re.compile(r"hit your [a-z0-9 -]*limit|usage limit|limit reached|out of usage|limit will reset", re.I)
TEKS_SEMENTARA = re.compile(r"\b429\b|rate[_ ]limit|\b529\b|overloaded", re.I)


def baca(path):
    ev = []
    for line in open(path, errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict):
            ev.append(e)
    return ev


def dari_epoch(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    if x > 1e12:   # milliseconds
        x /= 1000
    if x < 1e9:
        return None
    return datetime.datetime.fromtimestamp(x, WIB)


def dari_teks(teks, acuan):
    """'resets 3pm (Asia/Jakarta)', 'resets 3:30pm', 'resets Oct 21, 5am (UTC)', '...limit reached|1760000000'."""
    m = re.search(r"\|(\d{10,13})\b", teks)
    if m:
        return dari_epoch(m.group(1))
    m = re.search(r"resets?\s+(?:at\s+)?(?:(?P<mon>[A-Za-z]{3})[a-z]*\.?\s+(?P<day>\d{1,2}),?\s+(?:at\s+)?)?"
                  r"(?P<h>\d{1,2})(?::(?P<mi>\d{2}))?\s*(?P<ap>am|pm)?\s*(?:\((?P<tz>[A-Za-z_]+(?:/[A-Za-z_+-]+)*)\))?",
                  teks, re.I)
    if not m or (not m.group("ap") and not m.group("mi")):
        return None
    tz = WIB
    if m.group("tz"):
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(m.group("tz"))
        except Exception:  # noqa: BLE001
            tz = WIB
    h, mi = int(m.group("h")), int(m.group("mi") or 0)
    ap = (m.group("ap") or "").lower()
    if ap == "pm" and h < 12:
        h += 12
    if ap == "am" and h == 12:
        h = 0
    if h > 23 or mi > 59:
        return None
    lokal = acuan.astimezone(tz)
    if m.group("mon") and m.group("mon").lower()[:3] in BULAN:
        try:
            t = lokal.replace(month=BULAN[m.group("mon").lower()[:3]], day=int(m.group("day")), hour=h, minute=mi,
                              second=0, microsecond=0)
        except ValueError:
            return None
        if t < lokal - datetime.timedelta(days=1):
            t = t.replace(year=t.year + 1)
    else:
        t = lokal.replace(hour=h, minute=mi, second=0, microsecond=0)
        if t <= lokal:
            t += datetime.timedelta(days=1)
    return t.astimezone(WIB)


def batas(ev, acuan=None):
    """Did this transcript stop on a Claude usage or rate limit? (the dict documented above)"""
    acuan = acuan or datetime.datetime.now(WIB)
    hasil = {"batas": False, "jenis": None, "jendela": None, "reset": None, "pesan": ""}
    res = next((e for e in reversed(ev) if e.get("type") == "result"), None)
    if res and not res.get("is_error") and res.get("subtype") == "success":
        return hasil
    reset, jendela, pemakaian, sementara, pesan = None, None, False, False, ""
    for e in ev:
        if e.get("type") == "rate_limit_event":
            info = e.get("rate_limit_info") or {}
            if info.get("status") == "rejected":
                pemakaian = True
                jendela = info.get("rateLimitType") or jendela
                reset = dari_epoch(info.get("resetsAt")) or reset
        elif e.get("type") == "assistant" and e.get("error") in ("rate_limit", "overloaded", "billing_error"):
            teks = "".join(c.get("text", "") for c in (e.get("message") or {}).get("content") or [] if isinstance(c, dict))
            info = ((e.get("apiErrorParams") or {}).get("rate_limit_info") or {})
            if e.get("apiError") == "usage_limit_reached" or info or TEKS_PEMAKAIAN.search(teks):
                pemakaian = True
                jendela = info.get("rateLimitType") or jendela
                # the exact epoch (rate_limit_event, apiErrorParams) wins over the hour in the text
                reset = reset or dari_epoch(info.get("resetsAt")) or dari_teks(teks, acuan)
            else:
                sementara = True
            pesan = teks.strip() or pesan
    if res:
        teks = str(res.get("result") or "") + " " + " ".join(str(x) for x in res.get("errors") or [])
        if TEKS_PEMAKAIAN.search(teks):
            pemakaian = True
            reset = reset or dari_teks(teks, acuan)
            pesan = teks.strip() or pesan
        elif TEKS_SEMENTARA.search(teks) and (res.get("is_error") or res.get("subtype") != "success"):
            sementara = True
            pesan = pesan or teks.strip()
    if not (pemakaian or sementara):
        return hasil
    return {"batas": True, "jenis": "pemakaian" if pemakaian else "sementara", "jendela": jendela,
            "reset": reset.isoformat(timespec="seconds") if reset else None, "pesan": pesan[:300]}


def main(argv):
    if len(argv) == 2 and argv[0] == "--batas":
        try:
            ev = baca(argv[1])
        except OSError:
            ev = []
        print(json.dumps(batas(ev), ensure_ascii=False))
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    path, want = argv
    init = res = None
    turn_models = set()
    try:
        ev = baca(path)
    except OSError as err:
        print("MASALAH transkrip tidak terbaca:", err)
        return 1
    peringatan = None
    for e in ev:
        if e.get("type") == "system" and e.get("subtype") == "init":
            init = e
        elif e.get("type") == "assistant":
            turn_models.add((e.get("message") or {}).get("model") or "")
        elif e.get("type") == "result":
            res = e
        elif e.get("type") == "rate_limit_event" and (e.get("rate_limit_info") or {}).get("status") == "allowed_warning":
            peringatan = e["rate_limit_info"]

    masalah, catatan = [], []
    b = batas(ev)
    if b["batas"]:
        jam = f", reset {b['reset'][:16].replace('T', ' ')} WIB" if b["reset"] else ""
        masalah.append(("batas pemakaian Claude tercapai" if b["jenis"] == "pemakaian" else
                        "Claude API membatasi permintaan (rate limit/overload)") + jam)
    if not init:
        masalah.append("tidak ada event init (claude gagal sebelum mulai; lihat .log)")
    else:
        if not str(init.get("model", "")).startswith(want):
            masalah.append(f"model sesi {init.get('model')}, bukan {want}")
        # aff_studio: Slate dipanggil lewat tools/slate.py (HTTP), bukan MCP, jadi tidak ada server MCP yang dicek.
    lain = {m for m in turn_models | set((res or {}).get("modelUsage") or {})
            if m and not m.startswith(want) and "haiku" not in m and m != "<synthetic>"}
    if lain:
        masalah.append("model lain ikut dipakai (fallback): " + ", ".join(sorted(lain)))
    if not res:
        masalah.append("tidak ada event result (sesi terpotong)")
    else:
        if res.get("is_error") or res.get("subtype") != "success":
            masalah.append("sesi berakhir dengan " + str(res.get("subtype")))
        ditolak = sorted({d.get("tool_name", "?") for d in res.get("permission_denials") or []})
        if ditolak:
            catatan.append("izin ditolak: " + ", ".join(ditolak))
        catatan.append("turn=%s durasi=%ss biaya=%s" % (res.get("num_turns"), round((res.get("duration_ms") or 0) / 1000),
                                                      res.get("total_cost_usd")))
        if res.get("result"):
            catatan.append("hasil: " + str(res["result"]).strip().replace("\n", " ")[:600])
    if peringatan and not b["batas"]:
        catatan.append("kuota Claude hampir habis (%s, terpakai %s)" % (peringatan.get("rateLimitType") or "?",
                                                                      peringatan.get("utilization", "?")))

    for m in masalah:
        print("MASALAH", m)
    for c in catatan:
        print("CATATAN", c)
    if b["batas"]:
        print("BATAS", json.dumps(b, ensure_ascii=False))
    return 1 if masalah else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
