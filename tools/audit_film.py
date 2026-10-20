"""
audit_film: numeric audit of an episode BEFORE rendering. Renders nothing and needs no browser.

    python3 tools/audit_film.py episodes/NNN [--fps 24]

Reads from the episode folder:
  film.js     must export META = { dur } and CUES = [{id, t, kata?, teks?}, ...]: the time (seconds) of every visual
              hit, stamp or label landing. `kata` = 0-based index of the word in vo.json "kata" that the picture
              lands on; `teks` (optional) = that word, to catch an off-by-one index.
  vo.json     per-word timing from buat_voiceover ("kata": [{teks, mulai, selesai}]). aff_studio: kata_koreksi.json
              (onsets moved to the end of measured silences in vo.mp3) is used instead when present.
  score.json  (optional) partitur from tools/slate_score.py; hits recorded with put(..., cue="<id>") are listed under
              "hits": [{cue, t}] and must land 1 frame AFTER their picture.
  audit.json  (optional) expectations: [{"t": 12.5 | "kata": 37, "harapan": "label X terlihat", "cue": "<id>"?}].
              Each one is resolved to a frame (+1 frame when tied to a word or cue, so the landing is complete);
              the frames are printed as a `waktu` list for pratinjau_film, to check by eye on exactly that frame.
              Without audit.json the list is every cue's frame +1.

Checks (each "GAGAL" line fails the audit, exit 1; usage or unreadable files exit 2):
  - render contract: no Math.random, Date, performance.now, timers, requestAnimationFrame, own fonts in film.js,
  - CUES: unique ids, 0 <= t <= META.dur, a cue with `kata` lands within +-1 frame of that word's start,
  - score hits: the cue exists, the hit lands 1 frame after it (0.5-1.5 frames), not inside `hening`, not after durasi,
  - audit.json: every expectation resolves to a time inside the film, and its `cue` (if named) is on that frame.

film.js is evaluated by node (no document/window; imports such as ./engine/toon.js are replaced by inert stubs;
node runs with --permission, read access to a temporary copy only). If that fails, `export const CUES = [...]` and
`META = { dur: <number> }` are parsed as literals.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EPS = 1e-3
BANNED = [
    (r"\bMath\.random\s*\(", "Math.random (pakai rng(seed) dari engine)"),
    (r"\bDate\.now\s*\(|\bnew\s+Date\b", "Date (film harus fungsi murni dari t)"),
    (r"\bperformance\.now\s*\(", "performance.now"),
    (r"\b(setTimeout|setInterval|requestAnimationFrame)\s*\(", "timer/requestAnimationFrame"),
    (r"\bnew\s+FontFace\b|@font-face", "font sendiri (renderer hanya menunggu font kit)"),
]

STUB = r"""
const __mk = () => { let p; const f = function () {};
  p = new Proxy(f, { get(_, k) {
      if (k === Symbol.toPrimitive) return h => (h === 'string' ? '' : 0);
      if (k === Symbol.iterator) return function* () {};
      if (k === 'then' || k === 'toJSON') return undefined;
      return p; },
    apply() { return p; }, construct() { return p; } });
  return p; };
const __S = __mk();
"""
RUNNER = """const F = await import('./film.mjs');
console.log('@@AUDIT@@' + JSON.stringify({META: F.META ?? null, CUES: F.CUES ?? null}));
"""


def strip_comments(src):
    """Remove // and /* */ comments, leaving string literals alone."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "'\"`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1]); i = j + 1
        elif src.startswith("//", i):
            j = src.find("\n", i); i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); i = n if j < 0 else j + 2
        else:
            out.append(c); i += 1
    return "".join(out)


def _clause(cl):
    """`a, { b, c as d }` / `* as F` -> list of `const ... = __S;` statements."""
    parts, cl = [], cl.strip()
    m = re.search(r"\{([^}]*)\}", cl)
    if m:
        names = [x.strip() for x in m.group(1).split(",") if x.strip()]
        parts.append("const { %s } = __S;" % ", ".join(re.sub(r"\s+as\s+", ": ", x) for x in names))
        cl = (cl[:m.start()] + cl[m.end():]).strip().strip(",").strip()
    m = re.match(r"\*\s*as\s+([\w$]+)", cl)
    if m:
        parts.append("const %s = __S;" % m.group(1))
        cl = cl[m.end():].strip().strip(",").strip()
    if re.fullmatch(r"[\w$]+", cl or "-"):
        parts.append("const %s = __S;" % cl)
    return " ".join(parts)


def stub_imports(src):
    src = re.sub(r"^\s*import\s+([\w$\s,{}*]+?)\s+from\s*(['\"])[^'\"]+\2\s*;?", lambda m: _clause(m.group(1)), src,
                 flags=re.M)
    return re.sub(r"^\s*import\s*(['\"])[^'\"]+\1\s*;?", "", src, flags=re.M)


def via_node(src):
    node = shutil.which("node")
    if not node:
        return None, "node tidak ada"
    tmp = tempfile.mkdtemp(prefix="audit_film_")
    try:
        Path(tmp, "film.mjs").write_text(STUB + stub_imports(src), encoding="utf-8")
        Path(tmp, "run.mjs").write_text(RUNNER, encoding="utf-8")
        err = ""
        for flag in ("--permission", "--experimental-permission"):
            try:
                p = subprocess.run([node, flag, "--allow-fs-read=" + tmp + os.sep, os.path.join(tmp, "run.mjs")],
                                   cwd=tmp, capture_output=True, text=True, timeout=15)
            except subprocess.TimeoutExpired:
                return None, "node timeout (kode top-level film.js terlalu lama)"
            for line in p.stdout.splitlines():
                if line.startswith("@@AUDIT@@"):
                    return json.loads(line[len("@@AUDIT@@"):]), None
            err = (p.stderr.strip().splitlines() or ["kode keluar %d" % p.returncode])
            err = next((x for x in err if "Error" in x), err[-1])
            if "bad option" not in p.stderr:
                break
        return None, err.strip()[:200]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _literal(src, name, open_ch, close_ch):
    m = re.search(r"export\s+const\s+%s\s*=\s*\%s" % (name, open_ch), src)
    if not m:
        return None
    i, depth, j = m.end() - 1, 0, m.end() - 1
    while j < len(src):
        c = src[j]
        if c in "'\"`":
            k = j + 1
            while k < len(src) and src[k] != c:
                k += 2 if src[k] == "\\" else 1
            j = k
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
        j += 1
    return None


def js_to_json(lit):
    lit = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: json.dumps(m.group(1).replace("\\'", "'")), lit)
    lit = re.sub(r"([{,]\s*)([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', lit)
    return json.loads(re.sub(r",\s*([\]}])", r"\1", lit))


def via_regex(src):
    src = strip_comments(src)
    out = {"META": None, "CUES": None}
    meta = _literal(src, "META", "{", "}")
    if meta:
        m = re.search(r"\bdur\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*[,}]", meta)
        out["META"] = {"dur": float(m.group(1))} if m else None
    cues = _literal(src, "CUES", "[", "]")
    if cues:
        try:
            out["CUES"] = js_to_json(cues)
        except ValueError as e:
            raise ValueError("CUES bukan literal sederhana (%s); pastikan node bisa mengimpor film.js" % e)
    return out


def norm(w):
    return re.sub(r"[^\w]", "", str(w).lower())


def main(argv):
    args, fps = [], 24.0
    i = 0
    while i < len(argv):
        if argv[i] == "--fps" and i + 1 < len(argv):
            fps = float(argv[i + 1]); i += 2
        else:
            args.append(argv[i]); i += 1
    if len(args) != 1 or args[0] in ("-h", "--help", "bantuan"):
        print(__doc__.strip())
        return 2
    d = Path(args[0])
    F = 1.0 / fps
    try:
        src = (d / "film.js").read_text(encoding="utf-8")
    except OSError as e:
        print("GAGAL film.js tidak terbaca:", e)
        return 2
    ok = gagal = 0

    def hasil(lulus, teks):
        nonlocal ok, gagal
        print(("lolos " if lulus else "GAGAL ") + teks)
        ok, gagal = ok + bool(lulus), gagal + (not lulus)

    # 1. render contract
    bersih = strip_comments(src)
    for pat, label in BANNED:
        n = len(re.findall(pat, bersih))
        if n:
            hasil(False, "kontrak render: %s dipakai %d kali" % (label, n))
    if not any(re.search(p, bersih) for p, _ in BANNED):
        hasil(True, "kontrak render: tanpa Math.random/Date/timer/font sendiri")

    # 2. exported constants
    data, err = via_node(src)
    sumber = "node"
    if data is None:
        try:
            data, sumber = via_regex(src), "regex (node: %s)" % err
        except ValueError as e:
            print("GAGAL", e, "| node:", err)
            return 1
    print("info: konstanta dibaca lewat", sumber)
    dur = (data.get("META") or {}).get("dur")
    if not isinstance(dur, (int, float)):
        print("GAGAL META.dur tidak terbaca (export const META = { dur: <angka> })")
        return 1
    cues = data.get("CUES")
    if not isinstance(cues, list) or not cues:
        print("GAGAL film.js tidak mengekspor CUES = [{id, t, kata?}, ...] (minimal satu cue per hentakan/label)")
        return 1
    try:
        kata = json.loads((d / "vo.json").read_text(encoding="utf-8")).get("kata") or []
        koreksi = d / "kata_koreksi.json"
        if koreksi.exists():   # aff_studio: onset dikoreksi ke akhir jendela sunyi terukur di vo.mp3
            kata = [{"teks": w[2], "mulai": w[0], "selesai": w[1]} for w in json.loads(koreksi.read_text(encoding="utf-8"))["kata"]]
            print("info: timing kata dari kata_koreksi.json (%d kata)" % len(kata))
    except (OSError, ValueError) as e:
        print("GAGAL vo.json tidak terbaca:", e)
        return 2
    if not kata:
        print("info: vo.json tanpa timing kata; cue dengan `kata` tidak bisa dicek")

    # 3. cues
    peta, ids = {}, []
    for c in cues:
        cid, t = (c or {}).get("id"), (c or {}).get("t")
        if not isinstance(cid, str) or not isinstance(t, (int, float)):
            hasil(False, "cue tidak valid (perlu id teks dan t angka): %s" % json.dumps(c)[:80])
            continue
        ids.append(cid)
        peta[cid] = t
        fr = round(t * fps)
        if not -EPS <= t <= dur + EPS:
            hasil(False, "cue %s: t=%.3f di luar film (0–%.3f)" % (cid, t, dur))
            continue
        k = c.get("kata")
        if k is None:
            hasil(True, "cue %s: t=%.3f (frame %d) di dalam film" % (cid, t, fr))
            continue
        if not isinstance(k, int) or not 0 <= k < len(kata):
            hasil(False, "cue %s: kata=%s tidak ada di vo.json (%d kata)" % (cid, k, len(kata)))
            continue
        w = kata[k]
        if c.get("teks") is not None and norm(c["teks"]) != norm(w.get("teks")):
            hasil(False, "cue %s: kata %d adalah \"%s\", bukan \"%s\" (indeks bergeser?)" % (cid, k, w.get("teks"), c["teks"]))
            continue
        selisih = (t - float(w["mulai"])) * fps
        hasil(abs(selisih) <= 1 + EPS * fps,
              "cue %s: frame %d vs kata %d \"%s\" mulai %.3f (frame %d): %+.1f frame (batas ±1)"
              % (cid, fr, k, w.get("teks"), w["mulai"], round(w["mulai"] * fps), selisih))
    for cid in sorted({x for x in ids if ids.count(x) > 1}):
        hasil(False, "cue %s: id dipakai lebih dari sekali" % cid)

    # 4. score hits
    p = d / "score.json"
    if p.exists():
        try:
            sc = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            print("GAGAL score.json bukan JSON:", e)
            return 1
        hits = sc.get("hits") or []
        if not hits:
            print("info: score.json tanpa \"hits\" (put(..., cue=\"<id>\") di score.py); sinkron hentakan tidak dicek")
        sdur = float(sc.get("durasi") or dur)
        for h in hits:
            cid, t = h.get("cue"), h.get("t")
            if cid not in peta or not isinstance(t, (int, float)):
                hasil(False, "hit %s: tidak ada cue dengan id itu di CUES" % cid)
                continue
            f = (t - peta[cid]) * fps
            msg = "hit %s: %.3f s = %+.1f frame setelah gambar (target +1, batas 0,5–1,5)" % (cid, t, f)
            sunyi = [a for a, z in sc.get("hening") or [] if a - EPS <= t < z]
            if sunyi:
                hasil(False, msg + "; jatuh di dalam hening")
            elif t > sdur:
                hasil(False, msg + "; setelah durasi partitur")
            else:
                hasil(0.5 - EPS <= f <= 1.5 + EPS, msg)
    else:
        print("info: score.json belum ada; sinkron hentakan belum dicek")

    # 5. expectations
    p = d / "audit.json"
    waktu = []
    if p.exists():
        try:
            ex = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            print("GAGAL audit.json bukan JSON:", e)
            return 1
        for e in ex if isinstance(ex, list) else []:
            label = str(e.get("harapan") or "?")
            t = e.get("t")
            if e.get("kata") is not None:
                k = e["kata"]
                if not isinstance(k, int) or not 0 <= k < len(kata):
                    hasil(False, "harapan \"%s\": kata=%s tidak ada di vo.json" % (label, k))
                    continue
                t = float(kata[k]["mulai"])
            if not isinstance(t, (int, float)) or not 0 <= t <= dur:
                hasil(False, "harapan \"%s\": waktu %s di luar film" % (label, t))
                continue
            fr = round(t * fps)
            if e.get("cue") is not None:
                c = peta.get(e["cue"])
                hasil(c is not None and abs(c - t) * fps <= 1 + EPS * fps,
                      "harapan \"%s\": cue %s di %s, harapan di frame %d"
                      % (label, e["cue"], "frame %d" % round(c * fps) if c is not None else "tidak ada", fr))
            else:
                print("cek mata: frame %d (%.3f s): %s" % (fr, fr * F, label))
            # a landing (word or cue) is judged one frame later, when it is fully on screen; a plain time as given
            waktu.append(round((fr + (e.get("kata") is not None or e.get("cue") is not None)) * F, 3))
    else:
        waktu = [round((round(t * fps) + 1) * F, 3) for t in peta.values() if 0 <= t <= dur]
    waktu = sorted(set(waktu))[:24]
    print("waktu pratinjau (frame tiap harapan, +1 frame untuk kata/cue; maks 24): " + json.dumps(waktu))
    print("audit_film: %d lolos, %d gagal" % (ok, gagal))
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
