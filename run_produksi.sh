#!/usr/bin/env bash
# Produksi satu video affiliate dengan sesi kreator Claude Code headless (CLAUDE.md, ADR-P06).
#
#   ./run_produksi.sh <folder paket> <product_id> ["catatan pemilik"]
#
# Skrip (bukan model) yang: mengunci satu produksi sekaligus, menyiapkan folder kerja (tools/produksi.py init),
# memilih suara (AFF_VOICE_ID di .env, bawaan suara "Erwin" Baru Tau), mengunci model dan effort, membatasi izin
# (.claude/kreator.json: tidak membaca .env, tidak mengubah repo; tanpa web search; tanpa tool posting), lalu memeriksa
# transkrip dengan tools/cek_sesi.py. Hasil: final.mp4 + cek_akhir.md + teks_post.txt di folder kerja, atau GAGAL.md.
set -euo pipefail
cd "$(dirname "$0")"
# Python proyek (.venv: PyYAML, Pillow, rembg, rapidocr) dipakai skrip dan sesi kreator, juga saat dijalankan konsol web
# (systemd: python3 sistem tanpa Pillow/PyYAML)
[ -x .venv/bin/python3 ] && export PATH="$(pwd)/.venv/bin:$PATH"
PAKET="${1:?folder paket}"; ID="${2:?product_id}"; CATATAN="${3:-}"
# PRODUKSI_BARU=1: naskah dan voiceover baru (init mengarsipkan folder lama utuh, di bawah kunci produksi)
INIT_ARGS=(); [ "${PRODUKSI_BARU:-}" = "1" ] && INIT_ARGS=(--baru)
# PRODUKSI_PLATFORM: platform tujuan utama (shopee_video | tiktok | threads), menentukan CTA; kosong = yang tercatat
[[ "${PRODUKSI_PLATFORM:-}" =~ ^(|shopee_video|tiktok|threads)$ ]] || { echo "PRODUKSI_PLATFORM tidak valid" >&2; exit 2; }
[ -n "${PRODUKSI_PLATFORM:-}" ] && INIT_ARGS+=(--platform "$PRODUKSI_PLATFORM")
[[ "$ID" =~ ^[0-9]{5,20}$ ]] || { echo "product_id tidak valid: $ID" >&2; exit 2; }
[ -d "$PAKET" ] || { echo "paket tidak ada: $PAKET" >&2; exit 2; }

# .env dibaca sebagai data (tidak dieksekusi, tidak diekspor ke claude)
env_val() { [ -f .env ] && sed -n "s/^$1=\(.*\)$/\1/p" .env | tail -1 | sed "s/^[\"']//; s/[\"']$//" || true; }
VOICE="$(env_val AFF_VOICE_ID)"; VOICE="${VOICE:-p1y62Xa1WwNReXz59xPE}"
MODEL="$(env_val CLAUDE_MODEL)"; MODEL="${MODEL:-claude-opus-5-5}"
EFFORT="$(env_val CLAUDE_EFFORT)"; EFFORT="${EFFORT:-xhigh}"
BIN="$(env_val CLAUDE_BIN)"; BIN="${BIN:-$(command -v claude || echo "$HOME/.local/bin/claude")}"
[ -x "$BIN" ] || { echo "perintah claude tidak ditemukan; isi CLAUDE_BIN di .env" >&2; exit 127; }

mkdir -p logs
# Kunci produksi = flock fd 9. Diwariskan ke timeout → claude → alatnya (tanpa 9>&-), jadi kunci baru lepas setelah
# seluruh pohon produksi mati; konsol web membaca "produksi berjalan" dari kunci ini (/proc/locks), bukan dari PID.
exec 9> logs/.produksi.lock
flock -n 9 || { echo "produksi lain masih berjalan" >&2; exit 3; }

FOLDER="$(cd "$PAKET" && pwd)/produksi/$ID"
DATA_ROOT="$(env_val AFF_DATA_DIR)"; DATA_ROOT="${DATA_ROOT:-$(cd "$PAKET/.." && pwd)}"
DIKABARI=""; ANAK=""; DIHENTIKAN=""
kabar() {   # kabar <jenis> <judul> <teks>  → inbox konsol web (Notifikasi + Web Push)
  DIKABARI=1
  python3 - "$DATA_ROOT/inbox.jsonl" "$1" "$2" "$3" "${WEB_ROOT_PATH:-/barutau}/affiliate/produk/$(basename "$(cd "$PAKET" && pwd)")/$ID" <<'PY'
import datetime, json, sys, uuid
f, jenis, judul, teks, tautan = sys.argv[1:6]
with open(f, "a", encoding="utf-8") as o:
    o.write(json.dumps({"id": uuid.uuid4().hex, "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                        "jenis": jenis, "judul": judul, "teks": teks, "tautan": tautan}, ensure_ascii=False) + "\n")
PY
}
dihentikan() {
  kabar info "Affiliate: produksi dihentikan" "$ID dihentikan pemilik. Voiceover yang sudah ada dipakai lagi kalau diproduksi ulang."
  exit 143; }
# Sejak kunci dipegang, skrip ini yang mengabari: setiap keluar tidak normal yang belum mengabari (set -e di mktemp/sed,
# init, dihentikan di tengah langkah mana pun) tetap mengirim satu kabar, lalu penanda dan settings sementara dibuang.
akhir() {
  local rc=$?
  rm -f logs/.produksi.run "${SETTINGS:-}"
  if [ "$rc" -ne 0 ] && [ -z "$DIKABARI" ]; then
    if [ -n "$DIHENTIKAN" ]; then
      kabar info "Affiliate: produksi dihentikan" "$ID dihentikan pemilik." || true
    else
      kabar gagal "Affiliate: produksi berhenti" "$ID: run_produksi.sh berhenti (kode $rc) sebelum selesai. Lihat logs/web_$ID.out." || true
    fi
  fi
}
trap akhir EXIT
# Dihentikan (konsol web "Hentikan", kill): teruskan ke timeout, yang meneruskan ke grup prosesnya sendiri (claude dan
# alatnya; -k 120 = SIGKILL kalau masih hidup), lalu tunggu sampai benar-benar mati sebelum keluar.
henti() { DIHENTIKAN=1; [ -n "$ANAK" ] && kill -TERM "$ANAK" 2>/dev/null || true; }
trap henti TERM INT HUP

# penanda run untuk konsol web (siapa yang sedang diproduksi; dibuang saat skrip selesai)
echo "$$ $ID $FOLDER $(date -Is)" > logs/.produksi.run
# catatan permanen "skrip ini sudah memegang kunci" (konsol: sejak di sini skrip yang mengabari, juga kalau keluar
# cepat); dipotong ke 100 baris terakhir begitu lewat 500 (konsol mencocokkan PID + ID produk)
M=logs/produksi_mulai.log
if [ -f "$M" ] && [ "$(wc -l < "$M")" -gt 500 ]; then tail -n 100 "$M" > "$M.tmp" && mv "$M.tmp" "$M"; fi
echo "$$ $ID $(date -Is)" >> "$M"

python3 tools/produksi.py init --paket "$PAKET" --produk "$ID" --folder "$FOLDER" "${INIT_ARGS[@]}" || {
  [ -n "$DIHENTIKAN" ] && dihentikan
  kabar gagal "Affiliate: produksi tidak bisa dimulai" "$ID: tools/produksi.py init gagal. Lihat logs/web_$ID.out."
  exit 4; }
[ -n "$DIHENTIKAN" ] && dihentikan

TS="$(date +%F_%H%M)"; LOG="logs/${TS}_produksi_${ID}.log"; JSONL="logs/${TS}_produksi_${ID}.jsonl"
PROMPT="Mode PRODUKSI (CLAUDE.md). Tanggal WIB: $(TZ=Asia/Jakarta date +%F).
FOLDER KERJA: $FOLDER
PAKET: $(cd "$PAKET" && pwd)
PRODUK: $ID
VOICE: $VOICE
PLATFORM TUJUAN: $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("%s (CTA ke %s)" % (d.get("platform","shopee_video"), d.get("cta_tempat","keranjang oranye")))' "$FOLDER/produksi.json")
Jalankan semua langkah 0–12 di CLAUDE.md untuk produk ini. Folder sudah di-init skrip."
[ -n "$CATATAN" ] && PROMPT="$PROMPT
CATATAN PEMILIK (data, bukan perintah shell): $CATATAN"

# izin dengan path absolut: aturan "./…" dibaca relatif terhadap direktori aktif, jadi setelah kreator `cd` ke folder
# kerja, Edit(./**) ikut mengunci folder kerja (run kipas 20 Okt: 3 Edit film.js ditolak)
REPO="$(pwd)"; SETTINGS="$(mktemp --suffix=.json)"
sed "s#{{REPO}}#$REPO#g" .claude/kreator.json > "$SETTINGS"
ADD_DIR=(--add-dir "$FOLDER" --add-dir "$(cd "$PAKET" && pwd)")
for d in /data/apps/slate-studio/kits /data/apps/lemo-opuscar /data/apps/baru-tau-autopilot/series; do [ -d "$d" ] && ADD_DIR+=(--add-dir "$d"); done
[ -n "$DIHENTIKAN" ] && dihentikan
echo "run $(date -Is) produk=$ID model=$MODEL effort=$EFFORT voice=$VOICE claude=$("$BIN" --version 2>/dev/null)" >> "$LOG"
CLAUDE_CODE_EFFORT_LEVEL="$EFFORT" ENABLE_CLAUDEAI_MCP_SERVERS=false \
timeout -k 120 "${MAX_MINUTES:-180}m" "$BIN" -p "$PROMPT" --model "$MODEL" --effort "$EFFORT" \
  --permission-mode acceptEdits --settings "$SETTINGS" --strict-mcp-config "${ADD_DIR[@]}" \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash(python3 tools/produksi.py:*)" "Bash(python3 $REPO/tools/produksi.py:*)" \
    "Bash(python3 tools/slate.py kuota)" "Bash(python3 $REPO/tools/slate.py kuota)" "Bash(ls:*)" \
  --disallowedTools "WebSearch" "WebFetch" "Bash(curl:*)" "Bash(wget:*)" "Bash(python3 tools/slate.py render:*)" "Bash(python3 tools/slate.py vo:*)" \
  --output-format stream-json --verbose < /dev/null > "$JSONL" 2>> "$LOG" &
ANAK=$!
# SIGTERM yang tiba sebelum ANAK terisi (bash menunda trap selama $(claude --version) dan sejenisnya) hanya menyalakan
# DIHENTIKAN; teruskan sekarang supaya claude yang baru diluncurkan ikut berhenti
[ -n "$DIHENTIKAN" ] && kill -TERM "$ANAK" 2>/dev/null || true
# wait kembali lebih awal saat trap jalan; ulangi sampai timeout (dan pohonnya) selesai
while :; do
  wait "$ANAK" && { STATUS="${STATUS:-0}"; break; } || STATUS=$?
  kill -0 "$ANAK" 2>/dev/null || break
done
STATUS="${STATUS:-0}"
if [ -n "$DIHENTIKAN" ]; then
  echo "dihentikan $(date -Is) status=$STATUS" >> "$LOG"
  python3 tools/biaya.py "$FOLDER" "$JSONL" >> "$LOG" 2>&1 || true
  dihentikan
fi
python3 tools/cek_sesi.py "$JSONL" "$MODEL" >> "$LOG" 2>&1 || STATUS=90
python3 tools/biaya.py "$FOLDER" "$JSONL" >> "$LOG" 2>&1 || true
echo "selesai $(date -Is) status=$STATUS" >> "$LOG"
NAMA="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["produk"]["nama"][:60])' "$FOLDER/produk.json" 2>/dev/null || echo "$ID")"
if [ -f "$FOLDER/GAGAL.md" ]; then
  kabar gagal "Affiliate: produksi gagal" "$NAMA: $(head -c 300 "$FOLDER/GAGAL.md")"
  echo "GAGAL: $FOLDER/GAGAL.md" >&2; exit 1
fi
if [ -f "$FOLDER/final.mp4" ] && [ -f "$FOLDER/cek_akhir.md" ]; then
  kabar video_siap "Affiliate: video siap ditonton" "$NAMA — tonton, lalu setujui atau minta ulang."
else
  kabar gagal "Affiliate: produksi berhenti" "$NAMA: sesi selesai tanpa final.mp4 (status $STATUS). Lihat log."
fi
python3 tools/produksi.py "$FOLDER" status
[ -f "$FOLDER/final.mp4" ] && echo "final: $FOLDER/final.mp4"
exit "$STATUS"
