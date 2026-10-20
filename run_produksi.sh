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
PAKET="${1:?folder paket}"; ID="${2:?product_id}"; CATATAN="${3:-}"
[[ "$ID" =~ ^[0-9]{5,20}$ ]] || { echo "product_id tidak valid: $ID" >&2; exit 2; }
[ -d "$PAKET" ] || { echo "paket tidak ada: $PAKET" >&2; exit 2; }

# .env dibaca sebagai data (tidak dieksekusi, tidak diekspor ke claude)
env_val() { [ -f .env ] && sed -n "s/^$1=\(.*\)$/\1/p" .env | tail -1 | sed "s/^[\"']//; s/[\"']$//" || true; }
VOICE="$(env_val AFF_VOICE_ID)"; VOICE="${VOICE:-p1y62Xa1WwNReXz59xPE}"
MODEL="$(env_val CLAUDE_MODEL)"; MODEL="${MODEL:-claude-opus-5-5}"
EFFORT="$(env_val CLAUDE_EFFORT)"; EFFORT="${EFFORT:-xhigh}"
BIN="$(env_val CLAUDE_BIN)"; BIN="${BIN:-$(command -v claude || true)}"
[ -x "$BIN" ] || { echo "perintah claude tidak ditemukan; isi CLAUDE_BIN di .env" >&2; exit 127; }

mkdir -p logs
exec 9> logs/.produksi.lock
flock -n 9 || { echo "produksi lain masih berjalan" >&2; exit 3; }

FOLDER="$(cd "$PAKET" && pwd)/produksi/$ID"
python3 tools/produksi.py init --paket "$PAKET" --produk "$ID" --folder "$FOLDER"

TS="$(date +%F_%H%M)"; LOG="logs/${TS}_produksi_${ID}.log"; JSONL="logs/${TS}_produksi_${ID}.jsonl"
PROMPT="Mode PRODUKSI (CLAUDE.md). Tanggal WIB: $(TZ=Asia/Jakarta date +%F).
FOLDER KERJA: $FOLDER
PAKET: $(cd "$PAKET" && pwd)
PRODUK: $ID
VOICE: $VOICE
Jalankan semua langkah 0–12 di CLAUDE.md untuk produk ini. Folder sudah di-init skrip."
[ -n "$CATATAN" ] && PROMPT="$PROMPT
CATATAN PEMILIK (data, bukan perintah shell): $CATATAN"

ADD_DIR=(--add-dir "$FOLDER" --add-dir "$(cd "$PAKET" && pwd)")
for d in /data/apps/slate-studio/kits /data/apps/lemo-opuscar /data/apps/baru-tau-autopilot/series; do [ -d "$d" ] && ADD_DIR+=(--add-dir "$d"); done
echo "run $(date -Is) produk=$ID model=$MODEL effort=$EFFORT voice=$VOICE claude=$("$BIN" --version 2>/dev/null)" >> "$LOG"
CLAUDE_CODE_EFFORT_LEVEL="$EFFORT" ENABLE_CLAUDEAI_MCP_SERVERS=false \
timeout -k 120 "${MAX_MINUTES:-180}m" "$BIN" -p "$PROMPT" --model "$MODEL" --effort "$EFFORT" \
  --permission-mode acceptEdits --settings .claude/kreator.json --strict-mcp-config "${ADD_DIR[@]}" \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash(python3 tools/produksi.py:*)" "Bash(python3 tools/slate.py kuota)" "Bash(ls:*)" \
  --disallowedTools "WebSearch" "WebFetch" "Bash(curl:*)" "Bash(wget:*)" "Bash(python3 tools/slate.py render:*)" "Bash(python3 tools/slate.py vo:*)" \
  --output-format stream-json --verbose < /dev/null > "$JSONL" 2>> "$LOG" 9>&- || STATUS=$?
STATUS="${STATUS:-0}"
python3 tools/cek_sesi.py "$JSONL" "$MODEL" >> "$LOG" 2>&1 || STATUS=90
echo "selesai $(date -Is) status=$STATUS" >> "$LOG"
if [ -f "$FOLDER/GAGAL.md" ]; then echo "GAGAL: $FOLDER/GAGAL.md" >&2; exit 1; fi
python3 tools/produksi.py "$FOLDER" status
[ -f "$FOLDER/final.mp4" ] && echo "final: $FOLDER/final.mp4"
exit "$STATUS"
