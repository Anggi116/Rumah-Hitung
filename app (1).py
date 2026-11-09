# ============================================================
#  Rumah Hitung – Kalkulator Material & Biaya Rumah
#  Versi Python (Streamlit) - simpan sebagai app.py
#  Jalankan lokal :  streamlit run app.py
#  Online (gratis):  GitHub + Streamlit Community Cloud
# ============================================================
import math
import re
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------- DATA ----------------------------
BAGIAN = [("Pondasi & struktur", .30), ("Dinding & plesteran", .18),
          ("Atap & plafon", .17), ("Lantai & finishing", .20),
          ("Pintu, jendela & kusen", .07), ("Listrik & air", .08)]
WARNA = ["#b85b6c", "#e08e9b", "#f2b5be", "#8f3847", "#f7d0d6", "#d98a97"]
DESC = {"hemat": "Rumah sederhana", "standar": "Rumah menengah", "premium": "Rumah besar / mewah"}
HARGA = {"kota": {"hemat": 4960000, "standar": 6330000, "premium": 7060000},
         "kab":  {"hemat": 4810000, "standar": 5750000, "premium": 6250000}}
SUMBER = {"kota": "Perwal Kota Magelang No. 13/2025", "kab": "Perbup Kab. Magelang No. 11/2026"}
TIPE_RN = {"hemat": "Rumah Negara Tipe C (C/D/E)", "standar": "Rumah Negara Tipe B", "premium": "Rumah Negara Tipe A"}


# ------------------------- FORMAT ANGKA -------------------------
def jround(x):
    return math.floor(x + 0.5)


def idn(x, maxfrac=3):
    """Format angka gaya Indonesia: 1.234,5"""
    x = round(x, maxfrac)
    if x == int(x):
        s = f"{int(x):,}"
    else:
        s = f"{x:,.{maxfrac}f}".rstrip("0")
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def rp(n):
    return "Rp " + idn(jround(n), 0)


def num(n):
    return idn(jround(n), 0)


def fm(n):
    return idn(round(n * 10) / 10, 1)


def ringkas(n):
    if n >= 1e9:
        return f"{n / 1e9:.2f}".replace(".", ",") + " miliar"
    if n >= 1e6:
        return num(n / 1e6) + " juta"
    return rp(n)


# --------------------------- LOGIKA ---------------------------
def efektif(tipe, lantai, wil):
    t, naik = tipe, False
    if tipe == "hemat" and lantai > 2:
        t, naik = "standar", True
    klas = "Sederhana" if (tipe == "hemat" and lantai <= 2) else "Tidak Sederhana"
    return {"h": HARGA[wil][t], "klas": klas, "naik": naik, "rn": TIPE_RN[t]}


def harga_skenario(wil, t, l):
    return HARGA[wil]["standar" if (t == "hemat" and l > 2) else t]


def data_lahan(TW, TP, KDB, KLB, GD, GS):
    TW, TP, GD, GS = TW or 0, TP or 0, GD or 0, GS or 0
    kdb, klb = (KDB or 0) / 100, KLB or 0
    return dict(TW=TW, TP=TP, kdb=kdb, klb=klb, gd=GD, gs=GS, tanah=TW * TP,
                bw=max(0, TW - 2 * GS), bd=max(0, TP - GD - GS))


# ----------------------------- DENAH -----------------------------
def layout(P, L, f, lantai):
    x1 = P * .5
    R, D, Wn, ST = [], [], [], []
    rm = lambda n, x, y, w, h, op=False: dict(n=n, x=x, y=y, w=w, h=h, open=op)
    dr = lambda o, x, y, s, w, sl=False: dict(o=o, x=x, y=y, s=s, w=w, sl=sl)
    wn = lambda o, x, y, l: dict(o=o, x=x, y=y, l=l)
    if f == 1:
        yA, y1, y2 = L * .45, L * .38, L * .62
        R += [rm("Ruang Keluarga", 0, 0, x1, yA), rm("Ruang Tamu", 0, yA, x1, L - yA),
              rm("Dapur", x1, 0, P - x1, y1), rm("KM", x1, y1, P - x1, y2 - y1),
              rm("Kamar Tidur", x1, y2, P - x1, L - y2)]
        D += [dr("h", x1 * .3, L, -1, 1), dr("v", x1, (y2 + L) / 2, 1, .9),
              dr("v", x1, y1 / 2, 1, .9), dr("v", x1, (y1 + y2) / 2, 1, .8)]
        Wn += [wn("v", 0, yA / 2, 1.4), wn("v", 0, (yA + L) / 2, 1.4), wn("h", x1 * .75, L, 1.2),
               wn("h", x1 + (P - x1) / 2, 0, 1), wn("v", P, (y1 + y2) / 2, .5),
               wn("v", P, (y2 + L) / 2, 1.2), wn("h", x1 + (P - x1) / 2, L, 1.2)]
    else:
        yS, y1, y2 = L * .45, L * .4, L * .6
        R += [rm("Ruang Santai", 0, 0, x1, yS), rm("Kamar Utama", 0, yS, x1, L - yS),
              rm("Kamar 2", x1, 0, P - x1, y1), rm("KM", x1, y1, P - x1, y2 - y1),
              rm("Balkon", x1, y2, P - x1, L - y2, True)]
        D += [dr("h", x1 * .7, yS, 1, .9), dr("v", x1, y1 / 2, 1, .9),
              dr("v", x1, (y1 + y2) / 2, 1, .8), dr("v", x1, (y2 + L) / 2, 1, 1.2, True)]
        Wn += [wn("v", 0, yS / 2, 1.4), wn("v", 0, (yS + L) / 2, 1.4), wn("h", x1 / 2, L, 1.4),
               wn("h", x1 + (P - x1) / 2, 0, 1), wn("v", P, y1 / 2, 1), wn("v", P, (y1 + y2) / 2, .5)]
    if lantai > 1:
        ST.append(dict(x=.2, y=.2, w=1, h=max(1, min(2.6, L * .45 - .4))))
    return R, D, Wn, ST


# ------------------------- LUAS DINDING DARI DENAH -------------------------
TINGGI_DINDING, TINGGI_PINTU, TINGGI_JENDELA = 3.0, 2.1, 1.2


def dinding_satu_lantai(P, L, f, lantai):
    """Luas dinding bersih satu lantai (m2), dihitung dari tepi ruangan pada denah.
    - dinding yang dipakai bersama dua ruangan dihitung sekali
    - ruangan terbuka (balkon) tidak punya dinding
    - dikurangi pintu (tinggi 2,1 m) dan jendela (tinggi 1,2 m) yang digambar di denah"""
    R, D, Wn, _ = layout(P, L, f, lantai)
    garis = {}  # (arah, koordinat) -> daftar ruas (awal, akhir)
    for r in R:
        if r["open"]:
            continue
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        for arah, k, a, b in (("h", y, x, x + w), ("h", y + h, x, x + w),
                              ("v", x, y, y + h), ("v", x + w, y, y + h)):
            garis.setdefault((arah, round(k, 4)), []).append((a, b))
    panjang = 0.0
    for ruas in garis.values():
        ruas.sort()
        a0, b0 = ruas[0]
        for a, b in ruas[1:]:
            if a <= b0 + 1e-9:
                b0 = max(b0, b)
            else:
                panjang += b0 - a0
                a0, b0 = a, b
        panjang += b0 - a0
    kotor = panjang * TINGGI_DINDING
    pintu = sum(d["w"] for d in D) * TINGGI_PINTU
    jendela = sum(w["l"] for w in Wn) * TINGGI_JENDELA
    return max(0.0, kotor - pintu - jendela), panjang


def luas_dinding(P, L, lantai):
    """Lantai 1 memakai denah lantai 1; lantai 2 dan 3 memakai denah lantai atas; semuanya dijumlahkan."""
    if P <= 0 or L <= 0:
        return 0.0
    total = dinding_satu_lantai(P, L, 1, lantai)[0]
    if lantai > 1:
        total += (lantai - 1) * dinding_satu_lantai(P, L, 2, lantai)[0]
    return total


def denah_svg(P, L, viewF, lantai):
    W, H, mx, my = 360, 270, 34, 40
    s = min((W - mx * 2) / P, (H - my - 30) / L)
    ox, oy = (W - P * s) / 2, my
    X = lambda v: round(ox + v * s, 2)
    Y = lambda v: round(oy + v * s, 2)
    R, D, Wn, ST = layout(P, L, viewF, lantai)

    o = (f'<text class="rh-ttl" x="10" y="16">DENAH LANTAI {viewF}</text>'
         f'<text class="rh-tx" x="10" y="28" style="text-anchor:start">ukuran dalam meter</text>')
    o += (f'<g transform="translate({W - 24},24)"><circle r="11" class="rh-nv"/>'
          f'<path d="M0,-8 L4,5 L0,2 L-4,5 Z" class="rh-na"/><text class="rh-tx" y="-14">U</text></g>')

    for r in R:
        cls = "rh-rmopen" if r["open"] else "rh-rm"
        o += f'<rect class="{cls}" x="{X(r["x"])}" y="{Y(r["y"])}" width="{r["w"] * s:.2f}" height="{r["h"] * s:.2f}"/>'

    for t in ST:
        o += f'<rect class="rh-stp" x="{X(t["x"])}" y="{Y(t["y"])}" width="{t["w"] * s:.2f}" height="{t["h"] * s:.2f}"/>'
        k = .3
        while k < t["h"]:
            o += f'<line class="rh-stp" x1="{X(t["x"])}" x2="{X(t["x"] + t["w"])}" y1="{Y(t["y"] + k)}" y2="{Y(t["y"] + k)}"/>'
            k += .3

    for w in Wn:
        l = w["l"] * s
        x, y = X(w["x"]), Y(w["y"])
        if w["o"] == "h":
            o += (f'<rect x="{x - l / 2:.2f}" y="{y - 2.5}" width="{l:.2f}" height="5" fill="#FDF2F4"/>'
                  f'<line class="rh-wl" x1="{x - l / 2:.2f}" x2="{x + l / 2:.2f}" y1="{y - 1.5}" y2="{y - 1.5}"/>'
                  f'<line class="rh-wl" x1="{x - l / 2:.2f}" x2="{x + l / 2:.2f}" y1="{y + 1.5}" y2="{y + 1.5}"/>')
        else:
            o += (f'<rect x="{x - 2.5}" y="{y - l / 2:.2f}" width="5" height="{l:.2f}" fill="#FDF2F4"/>'
                  f'<line class="rh-wl" y1="{y - l / 2:.2f}" y2="{y + l / 2:.2f}" x1="{x - 1.5}" x2="{x - 1.5}"/>'
                  f'<line class="rh-wl" y1="{y - l / 2:.2f}" y2="{y + l / 2:.2f}" x1="{x + 1.5}" x2="{x + 1.5}"/>')

    for d in D:
        r = d["w"] * s
        if d["o"] == "h":
            Hx, Hy = X(d["x"] - d["w"] / 2), Y(d["y"])
            o += f'<rect x="{Hx}" y="{Hy - 2.5}" width="{r:.2f}" height="5" fill="#FDF2F4"/>'
            if d["sl"]:
                o += (f'<line class="rh-wl" x1="{Hx}" x2="{Hx + r:.2f}" y1="{Hy - 1}" y2="{Hy - 1}"/>'
                      f'<line class="rh-wl" x1="{Hx}" x2="{Hx + r:.2f}" y1="{Hy + 1}" y2="{Hy + 1}"/>')
            else:
                sw = 1 if d["s"] == 1 else 0
                o += (f'<line class="rh-dl" x1="{Hx}" y1="{Hy}" x2="{Hx}" y2="{Hy + d["s"] * r:.2f}"/>'
                      f'<path class="rh-dr" d="M{Hx + r:.2f},{Hy} A{r:.2f},{r:.2f} 0 0 {sw} {Hx},{Hy + d["s"] * r:.2f}"/>')
        else:
            Hx, Hy = X(d["x"]), Y(d["y"] - d["w"] / 2)
            o += f'<rect x="{Hx - 2.5}" y="{Hy}" width="5" height="{r:.2f}" fill="#FDF2F4"/>'
            if d["sl"]:
                o += (f'<line class="rh-wl" y1="{Hy}" y2="{Hy + r:.2f}" x1="{Hx - 1}" x2="{Hx - 1}"/>'
                      f'<line class="rh-wl" y1="{Hy}" y2="{Hy + r:.2f}" x1="{Hx + 1}" x2="{Hx + 1}"/>')
            else:
                sw = 0 if d["s"] == 1 else 1
                o += (f'<line class="rh-dl" x1="{Hx}" y1="{Hy}" x2="{Hx + d["s"] * r:.2f}" y2="{Hy}"/>'
                      f'<path class="rh-dr" d="M{Hx},{Hy + r:.2f} A{r:.2f},{r:.2f} 0 0 {sw} {Hx + d["s"] * r:.2f},{Hy}"/>')

    for r in R:
        pw, ph = r["w"] * s, r["h"] * s
        if pw < 42 or ph < 20:
            continue
        cx, cy = X(r["x"]) + pw / 2, Y(r["y"]) + ph / 2
        o += f'<text class="rh-rmt" x="{cx:.2f}" y="{cy + (-1 if ph > 30 else 3):.2f}">{r["n"]}</text>'
        if ph > 30 and not r["open"]:
            o += f'<text class="rh-ar" x="{cx:.2f}" y="{cy + 10:.2f}">{fm(r["w"] * r["h"])} m²</text>'

    by, x1 = Y(L), X(P * .5)
    o += (f'<path class="rh-dm" d="M{X(0)},{by + 10} H{X(P)} M{X(0)},{by + 6} v8 M{x1},{by + 6} v8 M{X(P)},{by + 6} v8"/>'
          f'<text class="rh-dim" x="{(X(0) + x1) / 2:.2f}" y="{by + 9}" dy="-2">{P * .5:.1f}</text>'
          f'<text class="rh-dim" x="{(x1 + X(P)) / 2:.2f}" y="{by + 9}" dy="-2">{P * .5:.1f}</text>')
    o += (f'<path class="rh-dm" d="M{X(0)},{by + 24} H{X(P)} M{X(0)},{by + 20} v8 M{X(P)},{by + 20} v8"/>'
          f'<text class="rh-dim" x="{(X(0) + X(P)) / 2:.2f}" y="{by + 22}" dy="-2">{idn(P)} m</text>')
    o += (f'<path class="rh-dm" d="M{X(0) - 14},{Y(0)} V{by} M{X(0) - 18},{Y(0)} h8 M{X(0) - 18},{by} h8"/>'
          f'<text class="rh-dim" transform="translate({X(0) - 18},{(Y(0) + by) / 2:.2f}) rotate(-90)" dy="-2">{idn(L)} m</text>')
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block">{o}</svg>'


# ------------------------- LAHAN & SITEPLAN -------------------------
def lahan_html(P, L, lantai, d):
    dasar, total = P * L, P * L * lantai
    kdb_max, klb_max = d["tanah"] * d["kdb"], d["tanah"] * d["klb"]
    fit = P <= d["bw"] + 1e-9 and L <= d["bd"] + 1e-9
    max_lt = math.floor(d["klb"] / d["kdb"] + 1e-9) if d["kdb"] > 0 else 0
    cks = [
        (dasar <= kdb_max, f"Luas dasar {fm(dasar)} m² {'masih di bawah' if dasar <= kdb_max else 'melebihi'} "
                           f"batas KDB {fm(kdb_max)} m² ({fm(d['kdb'] * 100)}% × {fm(d['tanah'])} m²)"),
        (total <= klb_max, f"Total luas lantai {fm(total)} m² {'masih di bawah' if total <= klb_max else 'melebihi'} "
                           f"batas KLB {fm(klb_max)} m² ({idn(d['klb'], 2)} × {fm(d['tanah'])} m²)"),
        (fit, f"Rumah {idn(P)} × {idn(L)} m {'muat' if fit else 'tidak muat'} di area bangun "
              f"{fm(d['bw'])} × {fm(d['bd'])} m (setelah sempadan)"),
    ]
    h = "".join(f'<div class="rh-chk {"" if ok else "bad"}"><span>{"✅" if ok else "⚠️"}</span><span>{t}</span></div>'
                for ok, t in cks)
    h += (f'<div class="rh-chk"><span>ℹ️</span><span>Jika KDB dipakai penuh, KLB {idn(d["klb"], 2)} mengizinkan '
          f'sekitar {max_lt} lantai. Luas dasar terbesar yang mungkin: '
          f'{fm(min(kdb_max, d["bw"] * d["bd"]))} m².</span></div>')

    svg = ""
    if d["TW"] and d["TP"]:
        W, H, oy = 360, 200, 16
        s = min((W - 40) / d["TW"], (H - oy - 24) / d["TP"])
        ox = (W - d["TW"] * s) / 2
        bx, by = ox + d["gs"] * s, oy + d["gs"] * s
        hx, hy = bx + (d["bw"] - P) / 2 * s, oy + (d["TP"] - d["gd"] - L) * s
        bad = not (fit and dasar <= kdb_max and total <= klb_max)
        o = f'<text class="rh-ttl" x="{ox:.2f}" y="11">Lahan {fm(d["TW"])} × {fm(d["TP"])} m = {fm(d["tanah"])} m²</text>'
        o += f'<rect class="rh-land" x="{ox:.2f}" y="{oy}" width="{d["TW"] * s:.2f}" height="{d["TP"] * s:.2f}"/>'
        o += f'<rect class="rh-bld" x="{bx:.2f}" y="{by:.2f}" width="{d["bw"] * s:.2f}" height="{d["bd"] * s:.2f}"/>'
        o += f'<rect class="rh-hs {"bad" if bad else ""}" x="{hx:.2f}" y="{hy:.2f}" width="{P * s:.2f}" height="{L * s:.2f}"/>'
        if P * s > 70:
            o += f'<text class="rh-rmt" x="{hx + P * s / 2:.2f}" y="{hy + L * s / 2 + 3:.2f}">Rumah {idn(P)}×{idn(L)}</text>'
        o += (f'<rect class="rh-road" x="{ox:.2f}" y="{oy + d["TP"] * s + 4:.2f}" width="{d["TW"] * s:.2f}" height="8"/>'
              f'<text class="rh-tx" x="{W / 2}" y="{oy + d["TP"] * s + 22:.2f}">jalan (sisi depan)</text>')
        svg = f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block;margin-bottom:6px">{o}</svg>'
    return svg + h


# --------------------------- TABEL BANDING ---------------------------
def banding_html(P, L, B, wil, tipe, lantai, d):
    klb_max = d["tanah"] * d["klb"]
    T = ["hemat", "standar", "premium"]
    h = '<table class="rh-cmp"><tr><th></th>' + "".join(f"<th>{t.capitalize()}</th>" for t in T) + "</tr>"
    for l in (1, 2, 3):
        h += f'<tr><th class="rowh">{l} lantai</th>'
        for t in T:
            luas = P * L * l
            tot = luas * harga_skenario(wil, t, l)
            cls = (("ok" if tot <= B else "no") if B else "") + (" sel" if (t == tipe and l == lantai) else "")
            warn = " ⚠" if (d["tanah"] > 0 and luas > klb_max) else ""
            h += f'<td class="{cls}">{ringkas(tot)}{warn}<small>{fm(luas)} m²</small></td>'
        h += "</tr>"
    return h + "</table>"


# --------------------------- HITUNG UTAMA ---------------------------
def card(title, body, extra=""):
    return f'<div class="rh-card {extra}"><h2 class="rh-h2">{title}</h2>{body}</div>'


def hitung(P, L, lantai, wil, tipe, harga_manual, B, TW, TP, KDB, KLB, GD, GS, viewF):
    P, L, B = max(0, P or 0), max(0, L or 0), B or 0
    lantai = int(lantai)
    viewF = min(int(viewF), lantai)
    e = efektif(tipe, lantai, wil)
    manual = harga_manual if (harga_manual and harga_manual > 0) else None
    h = manual or e["h"]
    luas = P * L * lantai
    total = luas * h
    d = data_lahan(TW, TP, KDB, KLB, GD, GS)

    # --- ringkasan harga ---
    if not B:
        status = "Isi anggaran untuk melihat apakah cukup atau tidak."
    elif total <= B:
        status = f"✅ Anggaran cukup. Sisa {rp(B - total)} ({jround((B - total) / B * 100)}%)."
    else:
        status = f"⚠️ Kurang {rp(total - B)}. Dengan anggaran ini, luas maksimal sekitar {math.floor(B / h)} m² (tipe {tipe})."
    klas = "Klasifikasi: " + e["klas"]
    if e["naik"]:
        klas += " (rumah tipe C/D/E di atas 2 lantai masuk klasifikasi tidak sederhana, harga dinaikkan ke Tipe B sebagai pendekatan)"
    elif manual:
        klas += " (harga diubah manual)"
    hero = f'''
    <div class="rh-card rh-hero">
      <small>Estimasi total biaya bangun</small>
      <div class="rh-big">{rp(total)}</div>
      <small class="rh-sub">≈ {ringkas(total)} · {idn(luas)} m² × {rp(h)}/m²</small>
      <div class="rh-status">{status}</div>
      <div class="rh-info">{DESC[tipe]}. Acuan {SUMBER[wil]}: {e["rn"]}.<br>{klas}</div>
    </div>'''

    # --- banding ---
    cmp_html = card("Bandingkan skenario", banding_html(P, L, B, wil, tipe, lantai, d) + '''
      <p class="rh-hint">Ukuran rumah mengikuti isian di kiri, harga memakai SHST resmi wilayah terpilih.
      Hijau = masuk anggaran, merah = melebihi anggaran, ⚠ = melebihi batas KLB lahan.
      Kotak bergaris = skenario yang sedang dipilih.</p>''')

    # --- lahan ---
    lahan = card("Cek kelayakan lahan (KDB / KLB / sempadan)", lahan_html(P or 1, L or 1, lantai, d))

    # --- denah ---
    den = card("Denah rumah (gaya gambar DED)", denah_svg(P or 1, L or 1, viewF, lantai) + '''
      <p class="rh-hint">Denah ini ilustrasi pembagian ruang dari ukuran yang kamu isi, bukan gambar kerja.
      Rumah 3 lantai butuh pondasi lebih kuat, jadi naikkan harga per m² bila perlu.</p>''')

    # --- pie ---
    acc, grad, lg = 0, [], ""
    for i, (n, p) in enumerate(BAGIAN):
        a, b = acc * 100, (acc + p) * 100
        acc += p
        grad.append(f"{WARNA[i]} {a:.2f}% {b:.2f}%")
        lg += (f'<div class="rh-lg"><i style="background:{WARNA[i]}"></i><span>{n}</span>'
               f'<em>{jround(p * 100)}% · {ringkas(total * p)}</em></div>')
    pie = card("Perkiraan komposisi biaya", f'''
      <div class="rh-chart">
        <div class="rh-pie" style="background:conic-gradient({",".join(grad)})">
          <div class="rh-hole"><div><b>{idn(luas)} m²</b>total luas</div></div>
        </div>
        <div class="rh-legend">{lg}</div>
      </div>
      <p class="rh-hint">Persentase per pekerjaan adalah perkiraan umum, bukan data resmi SHST.</p>''')

    # --- material ---
    dinding = luas_dinding(P, L, lantai)
    mat = card("Perkiraan kebutuhan material utama", f'''
      <div class="rh-stats">
        <div class="rh-stat"><b>{num(dinding * 70)}</b><span>bata merah (buah)</span></div>
        <div class="rh-stat"><b>{num(dinding * .58 + luas * 1.1)}</b><span>semen 40 kg (sak)</span></div>
        <div class="rh-stat"><b>{num(luas * 30)}</b><span>besi beton (kg)</span></div>
      </div>
      <p class="rh-hint">Luas dinding bersih: <b>{fm(dinding)} m²</b>. Dihitung dari tepi ruangan pada denah
      (dinding bersama dihitung sekali, balkon tanpa dinding), tinggi dinding 3 m, dikurangi pintu (tinggi 2,1 m)
      dan jendela (tinggi 1,2 m) sesuai denah; lantai 2 dan 3 memakai denah lantai atas. Bata 70 buah/m² dinding,
      semen 0,58 sak/m² dinding + 1,1 sak/m² lantai, besi 30 kg/m² lantai. Angka kasar, untuk RAB resmi tetap
      perlu gambar kerja.</p>''')

    return hero, cmp_html, lahan, den, pie, mat


def pakai_maksimal(P, L, lantai, TW, TP, KDB, KLB, GD, GS):
    d = data_lahan(TW, TP, KDB, KLB, GD, GS)
    P0, L0 = (P or 1), (L or 1)
    max_a = min(d["tanah"] * d["kdb"], d["bw"] * d["bd"],
                d["tanah"] * d["klb"] / int(lantai) if d["klb"] > 0 else float("inf"))
    k = math.sqrt(max_a / (P0 * L0))
    k = min(k, d["bw"] / P0, d["bd"] / L0)
    nP, nL = math.floor(P0 * k * 2) / 2, math.floor(L0 * k * 2) / 2
    if nP >= 1 and nL >= 1:
        return nP, nL
    return P, L


# ------------------------------ TAMPILAN ------------------------------
CSS = """
.gradio-container{background-color:#F8FAFC !important;
  background-image:radial-gradient(#F8E1E5 .5px,transparent .5px),radial-gradient(#F8E1E5 .5px,transparent .5px);
  background-size:24px 24px;background-position:0 0,12px 12px;font-family:'Nunito',system-ui,sans-serif}
.rh-header{display:flex;gap:12px;align-items:center;padding:14px 18px;background:#1E293B;
  border-bottom:4px solid #E08E9B;border-radius:16px;box-shadow:0 8px 20px rgba(15,23,42,.18)}
.rh-logo{width:48px;height:48px;border-radius:16px;background:linear-gradient(135deg,#E08E9B,#B85B6C);
  display:grid;place-items:center;font-size:26px;flex:none}
.rh-header h1{margin:0;font-size:1.4rem;font-weight:800;color:#fff;letter-spacing:.04em}
.rh-header p{margin:0;color:#F8E1E5;font-size:.85rem}
.rh-card{background:#fff;border:1px solid #F8E1E5;border-radius:20px;padding:18px;color:#1E293B;
  box-shadow:0 2px 12px rgba(184,91,108,.08)}
.rh-h2{margin:0 0 10px;font-size:.95rem;font-weight:800;color:#B85B6C}
.rh-hint{font-size:.78rem;color:#475569;margin:8px 0 0}
.rh-hero{background:#0F172A;color:#fff;border:1px solid #1E293B}
.rh-hero small{color:#E08E9B;font-weight:700}
.rh-hero .rh-sub{color:#94a3b8;display:block}
.rh-big{font-family:'Fira Code',ui-monospace,monospace;font-size:clamp(1.5rem,6vw,2.1rem);font-weight:600;margin:4px 0;color:#34d399}
.rh-status{margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(224,142,155,.15);
  border:1px solid rgba(224,142,155,.35);font-size:.88rem;font-weight:700}
.rh-info{margin-top:8px;font-size:.78rem;color:#cbd5e1}
.rh-cmp{width:100%;border-collapse:separate;border-spacing:4px;font-size:.78rem}
.rh-cmp th{color:#475569;font-weight:800;padding:4px}
.rh-cmp th.rowh{text-align:left;white-space:nowrap}
.rh-cmp td{padding:9px 4px;border-radius:10px;text-align:center;font-weight:800;background:#FDF2F4;color:#1E293B}
.rh-cmp td.ok{background:rgba(46,139,106,.16);color:#2e8b6a}
.rh-cmp td.no{background:rgba(192,57,79,.14);color:#c0394f}
.rh-cmp td.sel{outline:2px solid #B85B6C}
.rh-cmp td small{display:block;font-weight:700;opacity:.8;font-size:.68rem}
.rh-chk{display:flex;gap:8px;align-items:flex-start;font-size:.84rem;font-weight:700;padding:9px 11px;
  border-radius:12px;background:#FDF2F4;margin-top:6px;color:#1E293B}
.rh-chk.bad{background:rgba(192,57,79,.13);color:#c0394f}
.rh-chart{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.rh-pie{position:relative;width:150px;height:150px;border-radius:50%;flex:none}
.rh-hole{position:absolute;inset:30px;border-radius:50%;background:#fff;display:grid;place-items:center;
  text-align:center;font-size:.72rem;color:#475569;font-weight:700;line-height:1.2}
.rh-hole b{display:block;font-size:1.05rem;color:#1E293B}
.rh-legend{flex:1;min-width:200px;display:grid;gap:6px}
.rh-lg{display:flex;align-items:center;gap:8px;font-size:.82rem;color:#1E293B}
.rh-lg i{width:12px;height:12px;border-radius:4px;flex:none}
.rh-lg span{flex:1;font-weight:700}
.rh-lg em{font-style:normal;font-weight:800;white-space:nowrap}
.rh-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.rh-stat{background:#FDF2F4;border-radius:14px;padding:12px;text-align:center}
.rh-stat b{display:block;font-size:1.1rem;color:#B85B6C}
.rh-stat span{font-size:.72rem;color:#475569;font-weight:700}
.rh-note{margin:0;font-size:.75rem;color:#94a3b8;text-align:center;padding:18px 16px;background:#1E293B;
  border-top:4px solid #E08E9B;border-radius:16px}
/* gambar SVG */
.rh-card svg text{font-family:'Nunito',system-ui,sans-serif}
.rh-tx{fill:#475569;font-size:9px;font-weight:700;text-anchor:middle}
.rh-dim{fill:#B85B6C;font-size:10px;font-weight:800;text-anchor:middle}
.rh-rm{fill:#FDF2F4;stroke:#1E293B;stroke-width:2.5}
.rh-rmopen{fill:none;stroke:#B85B6C;stroke-width:1.2;stroke-dasharray:4 3}
.rh-rmt{fill:#1E293B;font-size:9.5px;font-weight:800;text-anchor:middle}
.rh-ar{fill:#475569;font-size:8px;font-weight:700;text-anchor:middle}
.rh-ttl{fill:#B85B6C;font-size:11px;font-weight:800}
.rh-dr{fill:none;stroke:#B85B6C;stroke-width:1.2}
.rh-dl{stroke:#B85B6C;stroke-width:1.6}
.rh-wl{stroke:#B85B6C;stroke-width:1}
.rh-stp{fill:none;stroke:#475569;stroke-width:1}
.rh-nv{fill:none;stroke:#1E293B;stroke-width:1}
.rh-na{fill:#1E293B}
.rh-dm{stroke:#475569;stroke-width:1;fill:none}
.rh-land{fill:#fff;stroke:#1E293B;stroke-width:2}
.rh-bld{fill:none;stroke:#E08E9B;stroke-width:1.5;stroke-dasharray:5 4}
.rh-hs{fill:#FDF2F4;stroke:#B85B6C;stroke-width:2}
.rh-hs.bad{fill:rgba(192,57,79,.18);stroke:#c0394f}
.rh-road{fill:#475569;opacity:.25}
@media print{button,.rh-input{display:none !important}}
"""

HEADER = '''<div class="rh-header"><div class="rh-logo">🏠</div>
<div><h1>Rumah Hitung</h1><p>Kalkulator material &amp; biaya rumah untuk calon pemilik</p></div></div>'''

NOTE = '''<p class="rh-note">Harga acuan per m² memakai Standar Harga Satuan Tertinggi (SHST) Rumah Negara:
Kota Magelang (Perwal No. 13 Tahun 2025) atau Kabupaten Magelang (Perbup No. 11 Tahun 2026).
Biaya konstruksi fisik, belum termasuk perencanaan dan pengawasan. Estimasi awal, harga bisa diubah.
KDB, KLB, dan sempadan harus dicek ke KRK/RDTR lokasi.</p>'''




# Gaya SVG ditulis langsung di tiap elemen supaya gambar tetap tampil walau CSS kelas tidak terbawa
SVG_STYLE = {
    "rh-tx": "fill:#475569;font-size:9px;font-weight:700;text-anchor:middle",
    "rh-dim": "fill:#B85B6C;font-size:10px;font-weight:800;text-anchor:middle",
    "rh-rm": "fill:#FDF2F4;stroke:#1E293B;stroke-width:2.5",
    "rh-rmopen": "fill:none;stroke:#B85B6C;stroke-width:1.2;stroke-dasharray:4 3",
    "rh-rmt": "fill:#1E293B;font-size:9.5px;font-weight:800;text-anchor:middle",
    "rh-ar": "fill:#475569;font-size:8px;font-weight:700;text-anchor:middle",
    "rh-ttl": "fill:#B85B6C;font-size:11px;font-weight:800",
    "rh-dr": "fill:none;stroke:#B85B6C;stroke-width:1.2",
    "rh-dl": "stroke:#B85B6C;stroke-width:1.6",
    "rh-wl": "stroke:#B85B6C;stroke-width:1",
    "rh-stp": "fill:none;stroke:#475569;stroke-width:1",
    "rh-nv": "fill:none;stroke:#1E293B;stroke-width:1",
    "rh-na": "fill:#1E293B",
    "rh-dm": "stroke:#475569;stroke-width:1;fill:none",
    "rh-land": "fill:#ffffff;stroke:#1E293B;stroke-width:2",
    "rh-bld": "fill:none;stroke:#E08E9B;stroke-width:1.5;stroke-dasharray:5 4",
    "rh-hs": "fill:#FDF2F4;stroke:#B85B6C;stroke-width:2",
    "rh-road": "fill:#475569;opacity:.25",
}
SVG_BAD = "fill:rgba(192,57,79,.18);stroke:#c0394f"


def inline_svg(html):
    """Ubah class="rh-..." di dalam <svg> menjadi style langsung."""
    def ganti_svg(m):
        svg = m.group(0)

        def ganti_tag(t):
            tag = t.group(0)
            c = re.search(r'class="([^"]*)"', tag)
            if not c:
                return tag
            kelas = c.group(1).split()
            gaya = [SVG_STYLE[k] for k in kelas if k in SVG_STYLE]
            if "bad" in kelas:
                gaya.append(SVG_BAD)
            if not gaya:
                return tag
            tag = tag.replace(c.group(0), "")
            ada = re.search(r'style="([^"]*)"', tag)
            if ada:
                return tag.replace(ada.group(0), 'style="' + ";".join(gaya) + ";" + ada.group(1) + '"')
            return re.sub(r"^<(\w+)", lambda x: f'<{x.group(1)} style="{";".join(gaya)}"', tag, count=1)

        return re.sub(r"<[a-zA-Z][^>]*>", ganti_tag, svg)

    return re.sub(r"<svg\b.*?</svg>", ganti_svg, html, flags=re.S)


# ------------------------------ TAMPILAN STREAMLIT ------------------------------
st.set_page_config(page_title="Rumah Hitung", page_icon="🏠", layout="wide")


def tampil(html, tinggi=300):
    """Tampilkan HTML/SVG di dalam iframe sendiri (lengkap dengan CSS) supaya gambar denah tidak hilang."""
    dasar = "body{margin:0;background:transparent;font-family:'Nunito',system-ui,-apple-system,'Segoe UI',sans-serif}"
    components.html(f"<style>{CSS}{dasar}</style>{inline_svg(html)}", height=tinggi, scrolling=True)


tampil(HEADER, 90)

st.session_state.setdefault("P", 9.0)
st.session_state.setdefault("L", 7.0)


def _fit():
    nP, nL = pakai_maksimal(st.session_state.P, st.session_state.L, st.session_state.lantai,
                            st.session_state.TW, st.session_state.TP, st.session_state.KDB,
                            st.session_state.KLB, st.session_state.GD, st.session_state.GS)
    st.session_state.P, st.session_state.L = float(nP), float(nL)


kiri, kanan = st.columns([5, 7], gap="large")

with kiri:
    st.markdown("### 1. Ukuran rumah")
    c1, c2 = st.columns(2)
    P = c1.number_input("Panjang (m)", min_value=1.0, step=0.5, key="P")
    L = c2.number_input("Lebar (m)", min_value=1.0, step=0.5, key="L")
    lantai = st.radio("Jumlah lantai", [1, 2, 3], horizontal=True, key="lantai",
                      format_func=lambda v: f"{v} lantai")

    st.markdown("### 2. Wilayah & kualitas bangunan")
    wil = st.radio("Wilayah acuan harga (SHST)", ["kota", "kab"], horizontal=True,
                   format_func=lambda v: {"kota": "Kota Magelang", "kab": "Kab. Magelang"}[v])
    tipe = st.radio("Kualitas bangunan", ["hemat", "standar", "premium"], index=1, horizontal=True,
                    format_func=str.capitalize)
    hm = st.number_input("Harga bangun per m² (Rp). Kosongkan untuk pakai harga SHST",
                         value=None, min_value=0, step=100000)

    st.markdown("### 3. Anggaran kamu")
    B = st.number_input("Anggaran (Rp), kosongkan jika belum ada", value=500000000, min_value=0,
                        step=10000000)

    st.markdown("### 4. Lahan & aturan bangunan")
    c1, c2 = st.columns(2)
    TW = c1.number_input("Lebar tanah (m)", min_value=1.0, value=12.0, step=0.5, key="TW")
    TP = c2.number_input("Panjang tanah (m)", min_value=1.0, value=20.0, step=0.5, key="TP")
    c1, c2 = st.columns(2)
    KDB = c1.number_input("KDB maks (%)", min_value=1.0, max_value=100.0, value=60.0, step=5.0, key="KDB")
    KLB = c2.number_input("KLB maks (kali)", min_value=0.1, value=1.2, step=0.1, key="KLB")
    c1, c2 = st.columns(2)
    GD = c1.number_input("Sempadan depan (m)", min_value=0.0, value=3.0, step=0.5, key="GD")
    GS = c2.number_input("Sempadan samping & belakang (m)", min_value=0.0, value=1.0, step=0.5, key="GS")
    st.caption("Angka di atas hanya contoh. KDB, KLB, dan sempadan ditentukan tiap lokasi, cek di KRK atau "
               "RDTR kotamu. Panjang rumah dianggap sejajar lebar tanah (sisi depan).")
    st.button("📐 Pakai ukuran rumah maksimal di lahan ini", on_click=_fit, use_container_width=True)

with kanan:
    c_hero = st.container()
    c_cmp = st.container()
    c_lahan = st.container()
    c_pilih = st.container()   # pilihan lantai tepat di atas gambar denah
    c_den = st.container()
    c_pie = st.container()
    c_mat = st.container()
    c_print = st.container()

    with c_pilih:
        viewF = st.radio("Denah lantai yang ditampilkan", [1, 2, 3], horizontal=True,
                         format_func=lambda v: f"Lantai {v}")

    hero, cmp_html, lahan, den, pie, mat = hitung(P, L, lantai, wil, tipe, hm, B, TW, TP, KDB, KLB, GD, GS, viewF)
    for wadah, blok, tinggi in ((c_hero, hero, 270), (c_cmp, cmp_html, 360), (c_lahan, lahan, 780),
                                (c_den, den, 700), (c_pie, pie, 360), (c_mat, mat, 240)):
        with wadah:
            tampil(blok, tinggi)
    with c_print:
        components.html(
            '<button onclick="window.parent.print()" style="width:100%;padding:13px;border:0;border-radius:14px;'
            'background:#B85B6C;color:#fff;font-weight:800;font-size:15px;cursor:pointer">'
            '🖨️ Cetak / simpan PDF</button>', height=60)

tampil(NOTE, 160)
