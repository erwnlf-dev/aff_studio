"""run_produksi.sh sungguhan di salinan repo sementara, dengan claude tiruan (CLAUDE_BIN di .env salinan): setelah kunci
dipegang, setiap keluar tidak normal mengirim tepat satu kabar ke inbox, penanda dibuang, dan catatan mulai ditulis."""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture  # noqa: E402

AKAR = Path(__file__).resolve().parent.parent
CLAUDE_TIRUAN = """#!/usr/bin/env bash
[ "${1:-}" = "--version" ] && { echo "tiruan 0"; exit 0; }
sleep 300 &
echo $! > "$(dirname "$0")/claude_anak.txt"
wait
"""


def hidup(pid):
    try:
        return Path("/proc/%d/stat" % pid).read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


class RunProduksi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.repo = t / "repo"
        shutil.copytree(AKAR, self.repo, ignore=shutil.ignore_patterns(".git", "logs", ".venv", ".env", ".env.*", "__pycache__"))
        (t / "claude").write_text(CLAUDE_TIRUAN)
        (t / "claude").chmod(0o755)
        (self.repo / ".env").write_text("CLAUDE_BIN=%s\n" % (t / "claude"))
        self.paket = t / "data" / "2026-10-19"
        fixture.buat(self.paket)
        self.inbox = t / "data" / "inbox.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def jalankan(self):
        return subprocess.Popen([str(self.repo / "run_produksi.sh"), str(self.paket), fixture.PRODUK_OK], cwd=self.repo,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                                env={k: v for k, v in os.environ.items() if k != "AFF_DATA_DIR"})

    def kabar(self):
        return [json.loads(x) for x in self.inbox.read_text().splitlines()] if self.inbox.exists() else []

    def test_gagal_set_e_setelah_kunci_tetap_mengabari(self):
        """mktemp/sed .claude/kreator.json gagal (set -e) setelah catatan mulai: satu kabar 'berhenti', penanda hilang."""
        (self.repo / ".claude" / "kreator.json").unlink()
        p = self.jalankan()
        self.assertNotEqual(p.wait(120), 0)
        k = self.kabar()
        self.assertEqual([(x["jenis"], x["judul"]) for x in k], [("gagal", "Affiliate: produksi berhenti")])
        self.assertFalse((self.repo / "logs" / ".produksi.run").exists())
        mulai = (self.repo / "logs" / "produksi_mulai.log").read_text().split()
        self.assertEqual(mulai[:2], [str(p.pid), fixture.PRODUK_OK])

    def test_dihentikan_saat_claude_berjalan(self):
        p = self.jalankan()
        anak = Path(self.tmp.name) / "claude_anak.txt"
        batas = time.monotonic() + 120
        while not anak.exists():
            self.assertLess(time.monotonic(), batas)
            time.sleep(0.1)
        os.kill(p.pid, signal.SIGTERM)                 # konsol juga mengirim ke seluruh pohon; ini jalur trap skrip
        self.assertEqual(p.wait(60), 143)
        self.assertEqual([x["judul"] for x in self.kabar()], ["Affiliate: produksi dihentikan"])
        self.assertFalse((self.repo / "logs" / ".produksi.run").exists())
        cucu = int(anak.read_text())                   # sleep anak claude tiruan: ikut mati lewat timeout
        time.sleep(0.5)
        self.assertFalse(hidup(cucu))


if __name__ == "__main__":
    unittest.main()
