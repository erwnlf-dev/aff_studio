"""tools/slate.py dengan server MCP tiruan lokal: tidak ada panggilan ke Slate sungguhan dan tidak ada kredit terpakai."""
import contextlib
import http.server
import io
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import slate  # noqa: E402

RAHASIA = "s3cr3t-path-0123456789"


class Tiruan(http.server.BaseHTTPRequestHandler):
    panggilan = []
    jawaban = {}

    def log_message(self, *a):
        pass

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        nama, args = req["params"]["name"], req["params"]["arguments"]
        Tiruan.panggilan.append((self.path, nama, args))
        hasil = Tiruan.jawaban.get(nama, {"ok": True})
        body = json.dumps({"jsonrpc": "2.0", "id": 1,
                           "result": {"content": [{"type": "text", "text": json.dumps(hasil)}]}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        Tiruan.panggilan.append((self.path, "GET", None))
        body = json.dumps({"kata": [{"teks": "Halo", "mulai": 0.0, "selesai": 0.3}]}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)


class Slate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Tiruan)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.tmp = tempfile.TemporaryDirectory()
        env = Path(cls.tmp.name) / "slate.env"
        cls.url = "http://127.0.0.1:%d/mcp/%s" % (cls.srv.server_address[1], RAHASIA)
        env.write_text("SLATE_MCP_URL=%s\n" % cls.url)
        cls.env_lama = slate.ENV_CALON
        slate.ENV_CALON = [str(env)]

    @classmethod
    def tearDownClass(cls):
        slate.ENV_CALON = cls.env_lama
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def setUp(self):
        Tiruan.panggilan = []
        Tiruan.jawaban = {}
        self.folder = Path(tempfile.mkdtemp(dir=self.tmp.name))
        isi = {"produk_id": "1", "variant_id": "v_abc", "dur": 20.2, "timing": "perkiraan",
               "params": {"vo.model": "eleven_v3", "vo.v2.speed": 1.0, "musik.ada": True, "vo.jeda_kalimat_detik": 0.3,
                          "vo.jeda_bagian_detik": 0.5, "motion.fps": 30}}
        (self.folder / "isi.json").write_text(json.dumps(isi))
        (self.folder / "foto.json").write_text(json.dumps({"foto": []}))
        (self.folder / "naskah.txt").write_text("Halo.\n")
        (self.folder / "scenes.json").write_text(json.dumps([{"no": 1, "vo": "Halo."}]))

    def jalan(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            kode = slate.main(list(argv))
        return kode, out.getvalue()

    def test_sensor_menyembunyikan_url(self):
        self.assertNotIn(RAHASIA, slate.sensor("gagal ke %s/x" % self.url))
        self.assertIn("<SLATE_MCP_URL>", slate.sensor("gagal ke %s" % self.url))

    def test_tool_posting_ditolak(self):
        for t in ("posting", "posting_zernio", "kirim_telegram", "batal_jadwal"):
            with self.assertRaises(slate.SlateError):
                slate.panggil(t, {})
        self.assertEqual(Tiruan.panggilan, [])

    def test_vo_menyimpan_dan_menolak_ulang(self):
        Tiruan.jawaban["buat_voiceover"] = {"job_id": "2026-10-20-abc", "durasi": 1.2, "karakter_terpakai": 5,
                                            "link_job": "https://studio.example/j/2026-10-20-abc?k=TOKEN123"}
        kode, out = self.jalan("vo", str(self.folder), "--voice", "VOICE1")
        self.assertEqual(kode, 0, out)
        _, nama, args = Tiruan.panggilan[0]
        self.assertEqual(nama, "buat_voiceover")
        self.assertEqual((args["model"], args["jeda_kalimat"], args["jeda_bagian"], args["voice_id"]), ("v3", 0.3, 0.5, "VOICE1"))
        get = [p for p, n, _ in Tiruan.panggilan if n == "GET"]
        self.assertEqual(get, ["/j/2026-10-20-abc/f/timing.json?k=TOKEN123"])      # link publik → server lokal
        vo = json.loads((self.folder / "vo.json").read_text())
        self.assertEqual(vo["kata"][0]["teks"], "Halo")
        self.assertNotIn("TOKEN123", out)
        kode, out = self.jalan("vo", str(self.folder))
        self.assertEqual(kode, 1)
        self.assertIn("sudah ada", out)
        self.assertEqual(len([n for _, n, _ in Tiruan.panggilan if n == "buat_voiceover"]), 1)

    def test_vo_error_tidak_menulis_file(self):
        Tiruan.jawaban["buat_voiceover"] = {"error": "voice_id belum ada"}
        kode, _ = self.jalan("vo", str(self.folder))
        self.assertEqual(kode, 1)
        self.assertFalse((self.folder / "vo.json").exists())

    def test_render_butuh_timing_vo(self):
        (self.folder / "vo.json").write_text(json.dumps({"job_id": "j1"}))
        kode, out = self.jalan("render", str(self.folder))
        self.assertEqual(kode, 1)
        self.assertIn("timing perkiraan", out)
        self.assertEqual(Tiruan.panggilan, [])

    def test_render_argumen(self):
        isi = json.loads((self.folder / "isi.json").read_text())
        isi["timing"] = "vo"
        (self.folder / "isi.json").write_text(json.dumps(isi))
        (self.folder / "vo.json").write_text(json.dumps({"job_id": "j1"}))
        Tiruan.jawaban["render_film"] = {"job_id": "j1", "status": "antre"}
        kode, out = self.jalan("render", str(self.folder))
        self.assertEqual(kode, 0, out)
        _, nama, args = Tiruan.panggilan[0]
        self.assertEqual(nama, "render_film")
        self.assertIs(args["telegram"], False)
        self.assertIs(args["qa_wajib"], True)
        self.assertEqual((args["fps"], args["durasi"], args["kit"]), (30, 20.2, "none"))
        self.assertEqual(sorted(args["file_tambahan"]), ["foto.json", "isi.json"])
        self.assertIn("export function renderFilm", args["film_js"])

    def test_render_menolak_file_terlalu_besar(self):
        isi = json.loads((self.folder / "isi.json").read_text())
        isi["timing"] = "vo"
        (self.folder / "isi.json").write_text(json.dumps(isi))
        (self.folder / "vo.json").write_text(json.dumps({"job_id": "j1"}))
        (self.folder / "foto.json").write_text("x" * 2_100_000)
        kode, out = self.jalan("render", str(self.folder))
        self.assertEqual(kode, 1)
        self.assertIn("batas renderer", out)

    def test_tanpa_link(self):
        d = slate.tanpa_link({"a": "https://x/j/1?k=T", "b": [{"c": "biasa"}]})
        self.assertEqual(d, {"a": "<link>", "b": [{"c": "biasa"}]})


if __name__ == "__main__":
    unittest.main()
