HOOK: pertanyaan + demonstrasi (tetes air diserap) sebelum detik 2

# Brief: Keset diatomite motif kucing (55566811995)

**Gaya: `midcentury-toon`** (kit Slate `midcentury`: toon.js, chars.js). Alasan: gaya yang terbukti di Baru Tau (#001–#003) dan disetujui pemilik. Bahasanya cocok untuk demo rumah tangga ala film kelas 1950-an: tangan yang berakting, gayung, ubin kamar mandi, dan cap karet untuk bukti. Ringan di CPU.

**Produk:** cutout dari foto penjual. Hero `keset` dari foto 5 (kucing tabby), `keset_abu` dari foto 3, dan motif `motif_pink`, `motif_anjing`, `motif_panda` dari foto 6. Cutout memakai rembg `isnet-general-use`; teks penjual hilang bersama latar. Cek mata `cutout_sheet.jpg`: tepi bersih, tanpa teks. Di film, cutout diberi garis tinta stiker 4 px dan bayangan siluet cokelat.

**Benchmark:**
- **Dipelajari:**
  - *Baru Tau.* #003: cap karet bukti, tangan dengan antisipasi, slab caption, wipe blok warna;
  - iklan alat rumah tangga 1950-an: demo dengan tangan, masalah → produk → bukti dalam satu adegan yang jelas.
- **Tidak diambil:** jingle, logo, atau desain merek apa pun; klaim berlebihan ala iklan lama ("ajaib", "dijamin"); angka yang tidak ada di data.

**Snapshot parameter:** variant_id `v_90c98942c712`. Suara "Erwin" (`p1y62Xa1WwNReXz59xPE`, sama dengan Baru Tau; EXP-04 belum dipilih).

## Voiceover (vo.json, job 2026-10-20-9fed21)

- Durasi 18,42 detik → `META.dur` = 18,72. 38 kata, 257 karakter.
- **Jendela sunyi terukur dari `vo.mp3`** (puncak −40 dB, ≥ 0,3 detik): 1,74–2,36 · 4,52–5,14 · 5,72–6,12 · 7,80–8,38 · 10,70–11,28 · 13,52–14,12 · 15,96–16,56.
  - Alignment server menyerap jeda ke durasi kata ("Kenalin…" 4,56–5,78; "keset" tercatat 5,82 padahal suara mulai 6,12).
  - Onset dikoreksi ke akhir jendela sunyi (`kata_koreksi.json`), dan semua CUES memakai onset koreksi.
- **HENING = 4,58–5,10** (0,52 detik, di dalam jendela 4,52–5,14, setelah "licin?"). Keset mendarat di "Kenalin…" (kata 11, 5,14 detik, frame 123); bunyi pertama frame 124.
- **PERLU DICEK telinga:** pengucapan "diatomite" dan "anti-slip".

## Blok arahan

```
TUJUAN:    detik 0–2: "keset kok nyerap air?" sambil melihat tetes air hilang ke keset; detik 5: lega waktu keset jatuh ke lantai basah; akhir: klik link untuk lihat motif
OUTPUT:    1080×1920, 24 fps, META.dur = 18,42 + 0,3 = 18,72 s, loop ke frame 0 (iris 18,45–18,68, frame ≥ 18,68 = renderAll(0))
WAKTU:     hook 0–2,333 (12 %); masalah 2,333–5,125 (hening 4,58–5,10); produk 5,125–8,333; fitur ① 8,333–11,167; fitur ② 11,167–14,0;
           bukti 14,0–16,5; CTA 16,5–18,72. Produk masuk di kata 11 (5,14 s, 27 %), demo serap di kata 3 (0,99 s)
LOOK:      midcentury-toon; latar per bagian: hook ubin #8ACFC6/nat #FBF6EA (atas); masalah dinding #F0B4A8 + lantai #E6D8BC (samping);
           produk ubin #F3D37F (atas); fitur ① ubin #B5C8DE; fitur ② #CBD08E; bukti #F4EAD5; CTA #F4EAD5 + sinar #F3D37F.
           Benda hero = keset cutout (selalu sama). Air #B5C8DE bertinta + kilau #FBF6EA. Tinta #2B2420; cap #B8452B di atas #FBF6EA.
           Font kit: Slab (hook 150 px, teks kunci 84–96 px), Jost 600 (caption 68 px, label 34 px), Barlow Condensed 800 (angka cap).
           Subjek ≥ 640 px: keset 820×650 (hook, produk, fitur ①, ②), 640×510 (bukti), 720×570 (CTA); kaki+betis 700 (masalah).
           Caption slab kertas bergaris tinta, ≤ 6 kata, dasar y = 1.470; disclosure tag kraft "Link afiliasi" 34 px di (60, 175) setiap frame.
MOTION:    antisipasi 4–5 frame (gayung miring balik 8°, tangan mundur 30 px, cap naik 60 px); jatuh keset 4 frame ease-in lalu squash 1,12×0,9
           (benda datar, dikurangi dari 1,25×0,7); tetes jatuh ease-in 8 frame, cincin percik 6 frame; genangan menyusut 0,9 s eio;
           pegas label back(·,1,8) 6–7 frame; sekunder 50–70 % jarak hero, mulai 3–5 frame kemudian; ambient < 5 % (dorongan kamera 1→1,04)
SHOTS:     7 shot, satu gerak hero per shot. Transisi: potong keras (hook→masalah 2,333; masalah→produk 5,125, keset sudah di udara),
           wipe dari konten (produk→① wipe bawah 8,0–8,333 dibawa tetes besar; ①→② wipe kiri 10,833–11,167; ②→bukti wipe atas 13,65–14,0),
           iris dari keset (bukti→CTA 16,1–16,5), iris ke frame 0 (loop). Frame setelah transisi sudah berisi keset.
TERLARANG: daftar BIBLE Baru Tau + A1–A7 affiliate + episode ini: tanpa onomatope/teks karangan ("srup", "WOW"); tanpa garis kecepatan
           (motion blur palsu); tanpa angka detik serap (data tidak menyebut waktu); tanpa foto penjual utuh; tanpa merek lain; tanpa harga
           coret/diskon; demo air diberi label "ilustrasi"
QA:        audit_film.py (kontrak render, CUES ±1 frame terhadap kata_koreksi, hit +1 frame) → ledger; pratinjau lokal ≥ 2 putaran 16–24 momen
           + pratinjau Slate; BASELINE affiliate 1–20 di ledger; QA server: beku, loop ≤ 2/255, kedip, hening, kontras, LRA
```

## Tiga momen andalan

1. **Frame 0:**
   - keset kucing tabby di atas ubin hijau-toska,
   - gayung koral di kanan atas dipegang tangan, dengan satu tetes air menggantung di bibirnya dan panah putus-putus ke keset,
   - teks hook "Keset ini / nyerap air?" ("nyerap air?" di pelat mustard).

   Di 0,12 detik gayung miring, dan tetes jatuh lalu menghilang ke keset sebelum "nyerap" selesai.
2. **Produk (5,14 detik):** setelah hening, keset jatuh dari atas ke lantai ubin mustard yang penuh genangan, squash, dan genangan di sekitarnya menyusut dan hilang satu per satu dari dekat ke jauh.
3. **Anti-slip (12,3–13,0 detik):** tangan mendorong keras keset (antisipasi mundur 30 px), keset hanya bergeser 6 px lalu kembali, dan tangan terpental.

## Storyboard

| Waktu | Di layar | Gerak hero | Teks kunci | Audio | Keluar |
|---|---|---|---|---|---|
| 0–2,333 Hook | Ubin toska (atas). Keset 820 px miring −6° di (540, 1.080). Gayung koral 260 px di kanan atas + tangan grip dari pojok kanan atas | Gayung miring balik 8° (0–0,12) lalu maju 22° (0,12–0,25); tetes lepas 0,2, jatuh 420 px (8 frame, ease-in) mendarat 0,55, cincin percik, genangan r 80 menyusut 0,55–1,45 (selesai setelah "nyerap" kata 3, 0,99). Tetes kedua 1,15 → mendarat 1,45 → hilang 2,25 | Keset ini nyerap air? | plink 0,57, serap (swell pendek) 0,6–1,4; vibrafon + jentikan; motif 3 nada di celah 1,74–2,36 | Potong keras 2,333 |
| 2,333–5,125 Masalah | Kamar mandi samping: dinding pink bernat putih, lantai krem y 1.240, tirai mustard bergaris di kiri, rel handuk. 3 genangan | Betis + kaki masuk dari kiri atas lewat busur (antisipasi angkat 30 px), mendarat di genangan di "basah" (kata 8, 3,54) + percik; di "licin?" (kata 10, 4,02) kaki tergelincir 220 px ke kanan dalam 6 frame dan berhenti miring 14°. HENING 4,58–5,10: pose tahan + goyang 3 px | Lantai licin? | Langkah (clack), percik (swish 2–6 kHz), gelincir (whistle turun) 4,04; musik berhenti 4,52; hening | Potong keras 5,125 (keset sudah di udara) |
| 5,125–8,333 Produk | Ubin mustard (atas), 5 genangan | Keset jatuh 600 px (4,98–5,14, 4 frame ease-in) mendarat di "Kenalin…" (kata 11, frame 123), squash 1,12×0,9; genangan menyusut berurutan dari dekat ke jauh (5,25–6,1, stagger 4 frame). Di "keset" (kata 12, 6,12) pelat "Keset diatomite" dicap. Di "motif" (kata 14, 6,97) cincin tinta digambar di kepala kucing + label "motif kucing" | Keset diatomite | Hentakan pertama setelah hening: stamp 300 Hz + clack + bell (frame 124); genangan pop kecil; marimba | Wipe toska dari bawah (8,0–8,333) |
| 8,333–11,167 Fitur ① | Ubin biru muda (atas). Keset kiri-tengah miring 8°. Tangan + gayung dari kanan | Antisipasi gayung 6 frame; 2 tetes besar jatuh (stagger 0,3 s) mendarat di "serapnya" (kata 17, 8,63) dan "tinggi" (kata 18, 8,94) → genangan menyusut 0,8 s. Di "kering" (kata 21, 10,2) segel centang toska dicap tangan di lantai kanan keset. Label "ilustrasi" | Cepat kering | plink ×2, serap, cap kecil (stamp 400 Hz + click) | Wipe avokad dari kiri (10,833–11,167) |
| 11,167–14,0 Fitur ② | Avokad. Keset abu 820 px tengah | Di "Alasnya" (kata 22, 11,28) keset membalik (skalaY cos, 8 frame) → sisi bawah navy berpola titik (ilustrasi) 0,6 s → balik lagi 12,1. Di "nggak" (kata 24, 12,31) tangan datar dari kanan: antisipasi mundur 30 px (4 frame), dorong 120 px, keset bergeser 6 px + squash 1,03; di "geser." (kata 26, 12,99) tangan terpental 80 px | Anti-slip | Balik (paper), dorong (scratch), pental (pop); pluck rapat | Wipe krem dari atas (13,65–14,0) |
| 14,0–16,5 Bukti | Krem. Keset 640 px di bawah (540, 1.150); kartu putih 640×300 di atas (540, 600) | Tangan + cap karet: antisipasi naik 60 px (5 frame), hentak 3 frame, mendarat di "sepuluh" (kata 29, 14,95) → "10RB+ terjual/bulan" (#B8452B). Di "lebih." (kata 31, 15,69) segel bulat "★ 4,89 · 9,5rb+ ulasan" pop | — (cap = teks kunci) | Cap: stamp 320 Hz + clack + bell; segel pop | Iris dari keset (16,1–16,5) |
| 16,5–18,72 CTA | Krem + sinar mustard. Keset 720 px tengah (540, 880). Motif pink/anjing/panda 300 px | Motif pop berurutan (stagger 4 frame) di "Motifnya" (kata 32, 16,56); pelat "Cek motif di link" pop di "cek" (kata 34, 17,55); tangan menunjuk ke bawah (ke link) di "link" (kata 36, 17,88) dengan busur | Cek motif di link | Pop ×3, bell di "link"; motif 3 nada terselesaikan setelah kata terakhir | Iris ke frame 0 (18,45–18,68) |

Tanpa suara: hook tertulis besar, setiap scene punya teks kunci ≤ 3 kata atau cap, caption tertanam ≤ 6 kata dengan satu kata disorot, dan keset yang sama membawa cerita dari frame 0 sampai end card.
