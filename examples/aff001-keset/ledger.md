# Ledger critic loop — keset (55566811995)

## Audit numerik sebelum putaran 1 (`python3 tools/audit_film.py <folder>`)

```
lolos kontrak render; timing kata dari kata_koreksi.json (38 kata)
lolos 2 cue tanpa kata + 17 cue dengan kata: selisih −0,5 … +0,5 frame (batas ±1)
audit_film: 20 lolos, 0 gagal (score.json belum ada)
```

## Putaran 1 — `pratinjau_r1.jpg` (28 momen, termasuk frame setelah setiap transisi)

Cek TERLARANG: tanpa glow, partikel, gradien polos, teks karangan, atau garis kecepatan. Teks penjual tidak ada (cutout bersih). Label "ilustrasi" ada di demo air dan sisi bawah.

Masalah, urut dari yang terbesar:

1. **Frame 62–118 (2,6–4,9 s): kaki dan genangan di belakang caption.** Lantai di y 1.240, tapak di y 1.310, caption di y 1.300–1.470, jadi aksi utama scene masalah tidak terlihat; betis 124 px terlalu kurus. → Lantai naik ke y 1.000, genangan di y 1.095–1.200, tapak di y 1.080; betis 190 px.
2. **Frame 0–55 dan 200–268: gayung terpotong di tepi kanan, tangan di luar layar**; baris "Keset ini" (baseline 400) menempel ke pelat "nyerap air?" (atas 388). → Gayung digeser 80–100 px ke kiri, pegangan di x ≈ 1.000, lengan dari (1.200, 140); baseline baris 1 ke y 362.
3. **Frame 276 (11,5 s): sisi bawah keset terbaca sebagai lubang hitam** (#3B4766 di thumbnail). → #7F8FB4 dengan titik #C9D3EA.
4. **Frame 408–446 (17,0–18,6 s): motif panda dan pink tertutup caption** (y 1.250+). → Dipindah ke y 1.130–1.140; keset ke (500, 860).

Catatan untuk putaran berikutnya: hook frame 0 belum menyorot kejanggalan selain pelat teks (tetes menggantung + jalur putus-putus tipis, baru terbaca di 270 px); tangan di fitur ② kecil (k 2,6).

## Putaran 2 — `pratinjau_r2.jpg` (21 momen) + `pratinjau_r2b.jpg` (cek perbaikan)

Perbaikan putaran 1 terkonfirmasi:
- frame 86–115: kaki menapak dan tergelincir di y 1.080, di atas caption;
- gayung dan tangan masuk layar;
- teks hook tidak bertumpuk;
- motif CTA di atas caption.

1. **Frame 276 (11,5 s): sisi bawah masih hitam.** Penyebab: bug di `topeng()`, titik digambar dengan `source-in` sehingga semua di luar titik terakhir terhapus. → Titik digambar dengan `source-atop`. Di r2b sisi bawah terlihat berpola titik.
2. **Frame 0: kejanggalan belum disorot di ukuran thumbnail** (tetes 52 px + garis putus-putus 5 px). → Tetes dilingkari tinta #B8452B 7 px (hilang di 0,2–0,3 s); garis putus-putus 7 px.

## Audit numerik setelah score.json

```
lolos kontrak render; 19 cue (selisih −0,5 … +0,5 frame)
lolos 19 hit: semuanya +1,0 frame setelah gambarnya; tidak ada bunyi di hening 4,58–5,10 (bunyi terakhir selesai 4,40, pertama sesudah 5,167)
audit_film: 39 lolos, 0 gagal
```
score.py: 132 event, 19 hit, 2 event dibuang (menabrak hening/akhir).

## Putaran 3 — `pratinjau_r3.jpg` (24 momen, termasuk frame tepat setelah setiap transisi)

1. **Frame 56 (2,333 s), tepat setelah potong ke masalah: kaki belum masuk** (masuk 2,42 dari x −260), jadi kamar mandi kosong (BASELINE 5). → Kaki sudah di layar sejak frame 56 (x −40).
2. **Frame 120 (5,0 s), tepat setelah potong ke produk: keset masih di luar layar** (y −500; hanya genangan). → Keset mulai di y 330, sudah terlihat jatuh di frame 120.
3. Tangan pendorong di fitur ② kecil (k 2,6, terpotong tepi kanan). → k 3,2.
4. (Kecil) frame 336 (14,0 s): kartu bukti masih kosong sebelum dicap. Subjek (keset) ada, jadi BASELINE 5 tetap lolos; dibiarkan.

## Putaran 4 (akhir) — `pratinjau_r4.jpg` + `pratinjau_slate.jpg` (renderer Slate, paritas)

Perbaikan putaran 3 terkonfirmasi: frame 56 kaki sudah di layar; frame 120 keset sudah terlihat jatuh. Pratinjau dari renderer Slate (font, kit `midcentury`, `aset/foto.js`) sama dengan pratinjau lokal.

### Perbandingan BASELINE affiliate (berdampingan dengan Baru Tau #003 `final_sheet.jpg`)

| # | Butir | Hasil |
|---|---|---|
| 1 | Frame 0 thumbnail utuh | ✔ keset cutout 820 px, hook "Keset ini / nyerap air?" 150 px (pelat mustard), tetes dilingkari tinta merah, gayung + tangan |
| 2 | Hook 1 detik tanpa suara | ✔ aksi pertama 0,06 s (gayung miring), hook selesai 2,333 s (12 %) |
| 3 | Tangan/karakter berakting | ✔ tangan gayung (antisipasi 3 frame), kaki (busur, squash, gelincir), tangan cap (antisipasi 5 frame), tangan dorong (mundur 30 px), tangan tunjuk (busur) |
| 4 | Warna + komposisi per bagian | ✔ 7 latar: toska, pink samping, mustard, biru, avokad, krem, krem + sinar |
| 5 | Transisi dari konten, subjek setelah transisi | ✔ setelah perbaikan r3 (frame 56, 120, 200, 268, 336, 396 berisi keset/kaki) |
| 6 | Subjek ≥ 640 px | ✔ keset 820×650; bukti: kartu cap + keset 960 px gabungan (keset sendiri 508 px, dicatat) |
| 7 | Tanpa diam > 0,5 s | QA server |
| 8 | Caption | ✔ Jost 600 68 px, ≤ 6 kata, 1 kata disorot, dasar y 1.470, "10" sebagai digit |
| 9 | Momen puncak | ✔ hening 4,58–5,10 (di jendela sunyi terukur 4,52–5,14), keset mendarat frame 123 di "Kenalin…", hentakan frame 124, tampil 3,2 s |
| 10 | End card | ✔ setelah perbaikan: keset 830 px (≈ 655 px tinggi), CTA "Cek motif di link", disclosure, tanpa harga; loop iris ke frame 0 |
| 11 | Musik | ✔ 7 aransemen, 19 hit + foley, hit +1 frame; LRA → QA server |
| 12 | Klaim bersumber | ✔ `siapkan_film.py` lolos (fitur:0–3, terjual, rating, varian) |
| 13 | Kedip/kontras | QA server (META.kontras 6 pasangan) |
| 14 | Audit numerik | ✔ 39 lolos, 0 gagal |
| 15 | Tanpa teks penjual | ✔ semua foto lewat cutout; banner/ikon hilang (cutout_sheet.jpg) |
| 16 | Tanpa foto utuh/model | ✔ |
| 17 | Demo fitur digambar | ✔ tetes diserap (ilustrasi), sisi bawah anti-slip (ilustrasi), didorong tidak geser |
| 18 | Disclosure | ✔ tag "Link afiliasi" 34 px setiap frame, tinta di atas #FBF6EA |
| 19 | Compliance data | ✔ tanpa harga/diskon; "10RB+" persis; "4,89"; "9,5rb+" (9.538 dibulatkan ke bawah) |
| 20 | Kategori diatur | ✔ tidak berlaku (Perlengkapan Rumah) |

Keputusan: boleh render.

## Render

| Render | Hasil QA | Perubahan sesudahnya |
|---|---|---|
| 1 | lolos; LRA 1,2; sinkron `serap` +153 ms, `kaki_basah` +105, `balik` +106, `pental` +89 | hentakan dibuka klik/clack (attack tajam); paper/swish jadi bunyi antisipasi; level musik per bagian |
| 2 | lolos; LRA 1,4; sinkron `serap` +153, `kaki_basah` +112 | hit `serap` dihapus (tertutup kata "nyerap"); percik sesudah benturan; kontras level lebih besar |
| 3 (final) | lolos; LRA 1,5; sinkron `kaki_basah` +105, `balik` +106; 1 pop −2,1 dB | berhenti (QA lolos, sisa peringatan dijelaskan di cek_akhir.md) |
