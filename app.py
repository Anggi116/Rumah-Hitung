# ============================================================
#  Rumah Hitung v2 - Kota Magelang, rumah 1-2 lantai
#  Menu sidebar, denah DED beranimasi, RAB dari DED (harga HSP MAS PETRUK)
#  Simpan sebagai app.py   |   requirements.txt: streamlit
# ============================================================
import math
import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------- DATA ----------------------------
BAGIAN = [("Pondasi & struktur", .30), ("Dinding & plesteran", .18),
          ("Atap & plafon", .17), ("Lantai & finishing", .20),
          ("Pintu, jendela & kusen", .07), ("Listrik & air", .08)]
WARNA = ["#b85b6c", "#e08e9b", "#f2b5be", "#8f3847", "#f7d0d6", "#d98a97"]
DESC = {"hemat": "Rumah sederhana", "standar": "Rumah menengah", "premium": "Rumah besar / mewah"}
HARGA = {"mas": {"hemat": 4791000, "standar": 5659000, "premium": 6102000}}
SUMBER = {"mas": "SHST Provinsi Jateng (MAS PETRUK), Kota Magelang"}
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


def denah_svg(P, L, viewF, lantai, anim=False):
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

    for i, r in enumerate(R):
        cls = "rh-rmopen" if r["open"] else "rh-rm"
        o += f'<rect class="{cls}" pathLength="1" style="animation-delay:{i * 0.22:.2f}s" x="{X(r["x"])}" y="{Y(r["y"])}" width="{r["w"] * s:.2f}" height="{r["h"] * s:.2f}"/>'

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
            o += (f'<rect class="rh-pop" x="{x - l / 2:.2f}" y="{y - 2.5}" width="{l:.2f}" height="5" fill="#FDF2F4"/>'
                  f'<line class="rh-wl" x1="{x - l / 2:.2f}" x2="{x + l / 2:.2f}" y1="{y - 1.5}" y2="{y - 1.5}"/>'
                  f'<line class="rh-wl" x1="{x - l / 2:.2f}" x2="{x + l / 2:.2f}" y1="{y + 1.5}" y2="{y + 1.5}"/>')
        else:
            o += (f'<rect class="rh-pop" x="{x - 2.5}" y="{y - l / 2:.2f}" width="5" height="{l:.2f}" fill="#FDF2F4"/>'
                  f'<line class="rh-wl" y1="{y - l / 2:.2f}" y2="{y + l / 2:.2f}" x1="{x - 1.5}" x2="{x - 1.5}"/>'
                  f'<line class="rh-wl" y1="{y - l / 2:.2f}" y2="{y + l / 2:.2f}" x1="{x + 1.5}" x2="{x + 1.5}"/>')

    for d in D:
        r = d["w"] * s
        if d["o"] == "h":
            Hx, Hy = X(d["x"] - d["w"] / 2), Y(d["y"])
            o += f'<rect class="rh-pop" x="{Hx}" y="{Hy - 2.5}" width="{r:.2f}" height="5" fill="#FDF2F4"/>'
            if d["sl"]:
                o += (f'<line class="rh-wl" x1="{Hx}" x2="{Hx + r:.2f}" y1="{Hy - 1}" y2="{Hy - 1}"/>'
                      f'<line class="rh-wl" x1="{Hx}" x2="{Hx + r:.2f}" y1="{Hy + 1}" y2="{Hy + 1}"/>')
            else:
                sw = 1 if d["s"] == 1 else 0
                o += (f'<line class="rh-dl" x1="{Hx}" y1="{Hy}" x2="{Hx}" y2="{Hy + d["s"] * r:.2f}"/>'
                      f'<path class="rh-dr" d="M{Hx + r:.2f},{Hy} A{r:.2f},{r:.2f} 0 0 {sw} {Hx},{Hy + d["s"] * r:.2f}"/>')
        else:
            Hx, Hy = X(d["x"]), Y(d["y"] - d["w"] / 2)
            o += f'<rect class="rh-pop" x="{Hx - 2.5}" y="{Hy}" width="5" height="{r:.2f}" fill="#FDF2F4"/>'
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
    kls = 'class="rh-anim" ' if anim else ''
    return f'<svg {kls}viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block">{o}</svg>'


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
    for l in (1, 2):
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
      <div class="rh-big" data-count="{jround(total)}" data-pre="Rp ">{rp(total)}</div>
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
     </p>''')

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
            ada = re.search(r'style="([^"]*)"', tag)
            if ada:
                return tag.replace(ada.group(0), 'style="' + ";".join(gaya) + ";" + ada.group(1) + '"')
            return re.sub(r"^<(\w+)", lambda x: f'<{x.group(1)} style="{";".join(gaya)}"', tag, count=1)

        return re.sub(r"<[a-zA-Z][^>]*>", ganti_tag, svg)

    return re.sub(r"<svg\b.*?</svg>", ganti_svg, html, flags=re.S)



# ============================================================
#  RAB DARI DED  (volume diambil dari gambar denah)
# ============================================================
H_LANTAI, T_PINTU, T_JENDELA = 3.0, 2.1, 1.2

# Katalog harga satuan: kunci -> (kode, uraian, satuan, harga_atas, harga_bawah atau None, dasar)
# harga_atas = harga di tabel HSP Kota Magelang (MAS PETRUK, edisi I 2026).
# harga_bawah = hitung ulang AHSP dengan harga MINIMUM HSD (hanya perkiraan). None = belum ada.
KAT = {
    "pembersihan": ("U.3.1.a", "Pembersihan lahan", "m2", 15178, None, "HSP"),
    "bouwplank": ("U.1.2.1.d", "Pasang bouwplank", "m'", 97075, None, "HSP"),
    "galian": ("U.3.4.1.a.1", "Galian tanah biasa s.d. 1 m (manual)", "m3", 113970, 66473, "AHSP"),
    "urugan_tanah": ("U.3.5.1.a", "Urugan kembali galian (manual)", "m3", 75892, None, "HSP"),
    "urugan_pasir": ("U.3.5.1.b", "Urugan pasir bawah lantai", "m3", 540535, None, "HSP"),
    "fondasi": ("2.2.2.1.4", "Fondasi batu belah 1SP:3PP", "m3", 1411313, 979739, "AHSP"),
    "beton": ("2.2.1.4.5", "Beton f'c 20 MPa (sloof, kolom, balok, plat)", "m3", 1681431, 1433609, "AHSP"),
    "tulang_kbs": ("2.2.1.1.3", "Pembesian sloof, kolom, balok", "kg", 25257, 22727, "AHSP"),
    "tulang_slab": ("2.2.1.1.1", "Pembesian plat lantai", "kg", 20983, 19876, "AHSP"),
    "bek_sloof": ("2.2.1.3.3", "Bekisting sloof", "m2", 340990, None, "HSP"),
    "bek_kolom": ("2.2.1.3.4", "Bekisting kolom", "m2", 352442, 259334, "AHSP"),
    "bek_balok": ("2.2.1.3.5", "Bekisting balok", "m2", 364718, 268684, "AHSP"),
    "bek_plat": ("2.2.1.3.6", "Bekisting plat lantai", "m2", 416774, 301876, "AHSP"),
    "plester": ("3.7.4", "Plesteran 1SP:4PP t=15 mm", "m2", 72291, 46503, "AHSP"),
    "acian": ("3.7.8", "Acian", "m2", 55742, 34261, "AHSP"),
    "rangka_atap": ("2.1.1.1", "Rangka atap baja ringan C75 (pelana)", "m2", 348814, 256072, "AHSP"),
    "gypsum": ("3.5.2.1", "Plafon gypsum 9 mm (penutup)", "m2", 85136, 74896, "AHSP"),
    "rangka_plafon": ("3.5.3.1", "Rangka plafon hollow galvanis 40x40", "m2", 235707, None, "HSP"),
    "cat_int": ("3.8.10.1", "Cat tembok interior", "m2", 50415, 26736, "AHSP"),
    "cat_ext": ("3.8.10.2", "Cat tembok eksterior", "m2", 72900, 36673, "AHSP"),
    "cat_plafon": ("3.8.20.1", "Cat plafon interior", "m2", 57101, None, "HSP"),
    "pintu": ("3.11.1.12", "Daun pintu plywood rangkap", "m2", 1031120, 667159, "AHSP"),
    "kusen": ("3.11.3.4", "Kusen pintu kayu kelas II/III 6x12", "m'", 216832, 148872, "AHSP"),
    "jendela": ("3.11.2.1", "Jendela kaca 5 mm nako aluminium", "m2", 673733, 642862, "AHSP"),
    "closet": ("3.18.3.1", "Closet duduk", "buah", 2071001, None, "HSP"),
    "kran": ("3.18.6.2.1", "Kran 1/2 inci", "buah", 146642, None, "HSP"),
    "floor_drain": ("3.18.6.1", "Floor drain", "buah", 132912, None, "HSP"),
    "lampu": ("5.3.1.1", "Titik instalasi lampu", "titik", 700340, None, "HSP"),
    "stop_kontak": ("5.1.5.13", "Titik instalasi stop kontak", "titik", 891008, None, "HSP"),
    "saklar": ("5.1.5.1", "Saklar tunggal", "unit", 55973, None, "HSP"),
    # pilihan dinding
    "dd_bata14": ("3.6.1.8", "Dinding bata merah 1/2 batu 1SP:4PP", "m2", 288045, 134246, "AHSP"),
    "dd_bata13": ("3.6.1.7", "Dinding bata merah 1/2 batu 1SP:3PP", "m2", 291472, None, "HSP"),
    "dd_ringan": ("3.6.4.2", "Dinding bata ringan tebal 10 cm", "m2", 172154, None, "HSP"),
    "dd_batako": ("3.6.5.2", "Dinding batako mortar tipe N", "m2", 355875, None, "HSP"),
    # pilihan lantai
    "lt_2020": ("3.9.8.1", "Lantai keramik 20x20", "m2", 245649, 166418, "AHSP"),
    "lt_3060": ("3.9.8.5", "Lantai keramik 30x60 polished", "m2", 178609, 144575, "AHSP"),
    "lt_homog": ("3.9.4.3", "Lantai homogeneous tile polish 60x60", "m2", 568801, None, "HSP"),
    # pilihan atap
    "at_palentong": ("3.1.1.3", "Atap genteng palentong besar", "m2", 110284, None, "HSP"),
    "at_kodok": ("3.1.1.2", "Atap genteng kodok glazuur", "m2", 202684, None, "HSP"),
    "at_beton": ("3.1.1.4", "Atap genteng beton", "m2", 232726, 169776, "AHSP"),
    "at_metal": ("3.1.3.7", "Atap metal lembaran", "m2", 148229, None, "HSP"),
    "nok_palentong": ("3.1.1.7", "Nok genteng palentong besar", "m'", 258301, None, "HSP"),
    "nok_kodok": ("3.1.1.6", "Nok genteng kodok glazuur", "m'", 290535, None, "HSP"),
    "nok_beton": ("3.1.1.8", "Nok genteng beton", "m'", 238276, None, "HSP"),
    "nok_metal": ("3.1.3.14", "Nok genteng metal", "m'", 167658, None, "HSP"),
    # pelengkap (revisi 4): semua dari tabel HSP Kota Magelang
    "lisplank": ("3.3.6", "Lisplank non-kayu (GRC/serat semen) lebar 20 cm", "m'", 226013, None, "HSP"),
    "plint_30": ("3.9.8.6", "Plint keramik 10-15 x 30 cm", "m'", 79708, None, "HSP"),
    "plint_60": ("3.9.8.8", "Plint keramik 10-15 x 60 cm", "m'", 80033, None, "HSP"),
    "plint_homog": ("3.9.4.6", "Plint homogeneous tile polish 10-15 x 60 cm", "m'", 105058, None, "HSP"),
    "waterproof": ("3.4.4", "Waterproofing acrylic base (kamar mandi dan balkon)", "m2", 167776, None, "HSP"),
    "dd_keramik_km": ("3.10.1.4", "Dinding keramik 20x20 kamar mandi", "m2", 284797, None, "HSP"),
    "bek_tangga": ("2.2.1.3.8", "Bekisting tangga", "m2", 348799, None, "HSP"),
    "railing_tangga": ("3.13.5", "Railing tangga dan handrail", "m'", 565806, None, "HSP"),
    "railing_balkon": ("3.13.4", "Railing besi pengaman tinggi 1,2 m (balkon)", "m'", 798439, None, "HSP"),
    "kunci_biasa": ("3.11.4.2", "Kunci tanam biasa", "buah", 215299, None, "HSP"),
    "kunci_km": ("3.11.4.3", "Kunci tanam kamar mandi", "buah", 128806, None, "HSP"),
    "engsel": ("3.11.4.5", "Engsel pintu", "buah", 96367, None, "HSP"),
    "wastafel": ("3.18.1.1", "Wastafel", "buah", 1130783, None, "HSP"),
    "shower": ("3.18.6.9", "Shower set", "buah", 2510432, None, "HSP"),
}
# Analisa harga satuan (AHSP) dari MAS PETRUK, Kota Magelang. Koefisien bahan yang tampil dibulatkan di situs,
# jadi di sini dipakai koefisien yang sesuai dengan kolom jumlah harga di situs.
AHSP_DATA = {
    "beton": ("2.2.1.4.5", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.009, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.028, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Batu/Tembok', 'OH', 0.275, 'Tukang Batu/Tembok'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 1.65, 'Pekerja'),
        ('Bahan', 'Air', 'Liter', 202, 'Air (liter)'),
        ('Bahan', 'Kerikil', 'Kg', 1009, 'Kerikil (kg)'),
        ('Bahan', 'PB: Pasir Beton / Pasir Kasar', 'Kg', 790, 'Pasir Beton (kg)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 348, 'Semen (kg)'),
    ]),
    "tulang_kbs": ("2.2.1.1.3", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0016, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0016, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Besi / Besi Beton', 'OH', 0.016, 'Tukang Besi / Besi Beton'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.016, 'Pekerja'),
        ('Bahan', 'Kawat tali beton', 'Kg', 0.028, 'Kawat tali beton (kg)'),
        ('Bahan', 'Baja Tulangan Polos (BjTP) dia <12 mm', 'Kg', 1.05, 'Baja tulangan polos BjTP <12 mm (kg)'),
    ]),
    "tulang_slab": ("2.2.1.1.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0007, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0007, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Besi / Besi Beton', 'OH', 0.007, 'Tukang Besi / Besi Beton'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.007, 'Pekerja'),
        ('Bahan', 'Kawat tali beton', 'Kg', 0.015, 'Kawat tali beton (kg)'),
        ('Bahan', 'Baja Tulangan Polos (BjTP) dia <12 mm', 'Kg', 1.02, 'Baja tulangan polos BjTP <12 mm (kg)'),
    ]),
    "bek_kolom": ("2.2.1.3.4", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.011, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.033, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.33, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.66, 'Pekerja'),
        ('Bahan', 'Dolken kayu dia 8-10 cm panjang 4 m', 'batang', 0.65, 'Dolken kayu 8-10 cm p.4 m (batang)'),
        ('Bahan', 'Plywood tebal 12 mm', 'lbr', 0.12705, 'Plywood 12 mm (lbr)'),
        ('Bahan', 'Balok Kayu Kelas II', 'm3', 0.00465, 'Balok Kayu Kelas II (m3)'),
        ('Bahan', 'Minyak Bekisting', 'Liter', 0.2, 'Minyak bekisting (liter)'),
        ('Bahan', 'Paku 5-12 cm', 'Kg', 0.4, 'Paku (kg)'),
    ]),
    "bek_balok": ("2.2.1.3.5", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.011, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.033, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.33, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.66, 'Pekerja'),
        ('Bahan', 'Dolken kayu dia 8-10 cm panjang 4 m', 'batang', 0.65, 'Dolken kayu 8-10 cm p.4 m (batang)'),
        ('Bahan', 'Plywood tebal 12 mm', 'lbr', 0.12705, 'Plywood 12 mm (lbr)'),
        ('Bahan', 'Balok Kayu Kelas II', 'm3', 0.00558, 'Balok Kayu Kelas II (m3)'),
        ('Bahan', 'Minyak Bekisting', 'Liter', 0.2, 'Minyak bekisting (liter)'),
        ('Bahan', 'Paku 5-12 cm', 'Kg', 0.4, 'Paku (kg)'),
    ]),
    "bek_plat": ("2.2.1.3.6", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.011, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.033, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.33, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.66, 'Pekerja'),
        ('Bahan', 'Dolken kayu dia 8-10 cm panjang 4 m', 'batang', 1.95, 'Dolken kayu 8-10 cm p.4 m (batang)'),
        ('Bahan', 'Plywood tebal 12 mm', 'lbr', 0.127, 'Plywood 12 mm (lbr)'),
        ('Bahan', 'Balok Kayu Kelas II', 'm3', 0.00465, 'Balok Kayu Kelas II (m3)'),
        ('Bahan', 'Minyak Bekisting', 'Liter', 0.2, 'Minyak bekisting (liter)'),
        ('Bahan', 'Paku 5-12 cm', 'Kg', 0.4, 'Paku (kg)'),
    ]),
    "fondasi": ("2.2.2.1.4", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.15, 'Mandor'),
        ('Tenaga Kerja', 'Tukang Batu/Tembok', 'OH', 0.5, 'Tukang Batu/Tembok'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 1.5, 'Pekerja'),
        ('Bahan', 'Pasir Pasang', 'm3', 0.485, 'Pasir Pasang (m3)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 202, 'Semen (kg)'),
        ('Bahan', 'Batu Belah', 'm3', 1.2, 'Batu Belah (m3)'),
    ]),
    "dd_bata14": ("3.6.1.8", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0033, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.01, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.1, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2, 'Pekerja'),
        ('Bahan', 'Pasir Pasang', 'm3', 0.043, 'Pasir Pasang (m3)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 11.5, 'Semen (kg)'),
        ('Bahan', 'Bata Merah', 'Buah', 71.91, 'Bata Merah (buah)'),
    ]),
    "plester": ("3.7.4", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0033, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.01, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.1, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2, 'Pekerja'),
        ('Bahan', 'Pasir Pasang', 'm3', 0.024, 'Pasir Pasang (m3)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 6.24, 'Semen (kg)'),
    ]),
    "acian": ("3.7.8", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0033, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.01, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.1, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2, 'Pekerja'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 3.25, 'Semen (kg)'),
    ]),
    "lt_3060": ("3.9.8.5", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0026, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0077, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.0769, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.1538, 'Pekerja'),
        ('Bahan', 'Keramik Lantai uk. 30 x 60 cm, Polished', 'Buah', 5.833, 'Keramik 30x60 Polished (buah)'),
        ('Bahan', 'Pasir Pasang', 'm3', 0.027, 'Pasir Pasang (m3)'),
        ('Bahan', 'Semen Warna', 'Kg', 1.5, 'Semen Warna (kg)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 13.632, 'Semen (kg)'),
    ]),
    "lt_2020": ("3.9.8.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0022, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0067, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.0667, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.1333, 'Pekerja'),
        ('Bahan', 'Pasir Pasang', 'm3', 0.027, 'Pasir Pasang (m3)'),
        ('Bahan', 'Semen Warna', 'Kg', 1.5, 'Semen Warna (kg)'),
        ('Bahan', 'PC/Portland Cement', 'Kg', 13.632, 'Semen (kg)'),
        ('Bahan', 'Keramik Lantai uk. 20 x 20 cm', 'Buah', 26.25, 'Keramik Lantai 20x20 (buah)'),
    ]),
    "rangka_atap": ("2.1.1.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0006, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0017, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Besi / Besi Beton', 'OH', 0.0169, 'Tukang Besi / Besi Beton'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.1014, 'Pekerja'),
        ('Bahan', 'Self Drilling Screw 4x16 mm (Roof Bottom Screw)', 'Buah', 3, 'Self drilling screw 4x16 (buah)'),
        ('Bahan', 'Reng / Roof Bottom RT-35 t=0,45 mm', 'Batang', 0.335698, 'Reng RT-35 (batang)'),
        ('Bahan', 'Self Drilling Screw 6x20 mm (Main Truss Screw)', 'Buah', 15.75, 'Self drilling screw 6x20 (buah)'),
        ('Bahan', 'Baja Ringan C.75 t=1,00 mm (L Bracket)', 'Batang', 0.642903, 'Baja Ringan C75 (batang)'),
        ('Bahan', 'Baja Ringan C75 t=0,75 mm (Batang Pengaku)', 'Batang', 0.011303, 'Baja Ringan C75 (batang)'),
        ('Bahan', 'Baja Ringan C75 t=1 mm (Batang Utama)', 'Batang', 0.5016, 'Baja Ringan C75 (batang)'),
        ('Bahan', 'Mesin Bor Cordless Drill Bor', 'Hari', 0.6137, 'Mesin bor cordless (hari)'),
        ('Peralatan', 'Mesin bor listrik', 'Jam', 0.3726, 'Mesin bor listrik (jam)'),
    ]),
    "at_beton": ("3.1.1.4", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0033, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.01, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.1, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2, 'Pekerja'),
        ('Bahan', 'Paku Biasa 2"-5"', 'Kg', 0.03, 'Paku biasa 2-5 inci (kg)'),
        ('Bahan', 'Genteng Beton', 'Buah', 11, 'Genteng Beton (buah)'),
    ]),
    "gypsum": ("3.5.2.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0017, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.005, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.05, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.1, 'Pekerja'),
        ('Bahan', 'Paku Sekrup', 'Kg', 0.11, 'Paku sekrup (kg)'),
        ('Bahan', 'Papan Gypsum 120x240 cm tebal 9 mm', 'lbr', 0.364, 'Papan gypsum 9 mm (lbr)'),
    ]),
    "cat_int": ("3.8.10.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0022, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0067, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Cat/Pelitur', 'OH', 0.0667, 'Tukang Cat/Pelitur'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.0667, 'Pekerja'),
        ('Bahan', 'Cat Tembok Interior', 'Kg', 0.26, 'Cat Tembok Interior (kg)'),
        ('Bahan', 'Cat Dasar Tembok', 'Kg', 0.1, 'Cat Dasar Tembok (kg)'),
    ]),
    "cat_ext": ("3.8.10.2", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0026, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0077, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Cat/Pelitur', 'OH', 0.0769, 'Tukang Cat/Pelitur'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.0769, 'Pekerja'),
        ('Bahan', 'Cat Tembok Eksterior', 'Kg', 0.26, 'Cat Tembok Eksterior (kg)'),
        ('Bahan', 'Cat Dasar Tembok', 'Kg', 0.1, 'Cat Dasar Tembok (kg)'),
    ]),
    "kusen": ("3.11.3.4", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.0048, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.0143, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 0.1429, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2857, 'Pekerja'),
        ('Bahan', 'Lem Kayu (Putih)', 'Kg', 1, 'Lem Kayu Putih (kg)'),
        ('Bahan', 'Paku 10 cm', 'Kg', 0.127587, 'Paku (kg)'),
        ('Bahan', 'Balok Kayu 6/12 Kelas II atau III', 'm3', 0.0086, 'Balok Kayu 6/12 Kelas II/III (m3)'),
    ]),
    "pintu": ("3.11.1.12", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.07, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.21, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang Kayu', 'OH', 2.1, 'Tukang Kayu'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.7, 'Pekerja'),
        ('Bahan', 'Plywood tebal 4 mm uk. 90x220 cm', 'lbr', 1, 'Plywood 4 mm 90x220 (lbr)'),
        ('Bahan', 'Lem Kayu (Putih)', 'Kg', 0.5, 'Lem Kayu Putih (kg)'),
        ('Bahan', 'Paku 1-2,5 cm', 'Kg', 0.03, 'Paku (kg)'),
        ('Bahan', 'Papan Kayu Kelas II', 'm3', 0.025, 'Papan Kayu Kelas II (m3)'),
    ]),
    "jendela": ("3.11.2.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.007, 'Mandor'),
        ('Tenaga Kerja', 'Kepala Tukang', 'OH', 0.02, 'Kepala Tukang'),
        ('Tenaga Kerja', 'Tukang', 'OH', 0.2, 'Tukang'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.2, 'Pekerja'),
        ('Bahan', 'Paku Sekrup 1-2 cm', 'Buah', 10, 'Paku sekrup 1-2 cm (buah)'),
        ('Bahan', 'Jendela Nako Rangka Aluminium (rangka + kaca 5 mm)', 'm2', 1.1, 'Jendela nako rangka aluminium (m2)'),
    ]),
    "galian": ("U.3.4.1.a.1", [
        ('Tenaga Kerja', 'Mandor', 'OH', 0.038, 'Mandor'),
        ('Tenaga Kerja', 'Pekerja', 'OH', 0.75, 'Pekerja'),
    ]),
}

# Harga dasar upah, bahan, dan peralatan (kunci: jenis, satuan, minimum, maksimum, sumber, catatan)
HD = {
    'Mandor': dict(jenis='Upah', satuan='OH', min=110000, max=239711, sumber='HSD Upah (Mandor OH)', catatan=''),
    'Kepala Tukang': dict(jenis='Upah', satuan='OH', min=120000, max=170000, sumber='HSD Upah (Kepala Tukang OH)', catatan=''),
    'Tukang': dict(jenis='Upah', satuan='OH', min=100000, max=179783, sumber='HSD Upah (Tukang OH)', catatan=''),
    'Tukang Batu/Tembok': dict(jenis='Upah', satuan='OH', min=105000, max=160000, sumber='HSD Upah (Tukang Batu/Tembok OH)', catatan=''),
    'Tukang Besi / Besi Beton': dict(jenis='Upah', satuan='OH', min=105000, max=179783, sumber='HSD Upah (Tukang Besi / Besi Beton OH)', catatan='Ada 3 baris tukang besi dengan maksimum berbeda (160.000 / 179.783)'),
    'Tukang Kayu': dict(jenis='Upah', satuan='OH', min=105000, max=179783, sumber='HSD Upah (Tukang Kayu OH)', catatan=''),
    'Tukang Cat/Pelitur': dict(jenis='Upah', satuan='OH', min=105000, max=179783, sumber='HSD Upah (Tukang Cat/Pelitur OH)', catatan=''),
    'Pekerja': dict(jenis='Upah', satuan='OH', min=75000, max=126000, sumber='HSD Upah (Pekerja OH)', catatan="Baris 'Pekerja Biasa' satuan Jam (96.000-126.000) janggal, tidak dipakai"),
    'Semen (kg)': dict(jenis='Bahan', satuan='kg', min=1410, max=1540, sumber="HSD Bahan 'Semen' kg", catatan=''),
    'Pasir Pasang (m3)': dict(jenis='Bahan', satuan='m3', min=288095, max=435000, sumber="HSD Bahan 'Pasir Pasang' m3", catatan=''),
    'Pasir Beton (kg)': dict(jenis='Bahan', satuan='kg', min=205, max=304, sumber="HSD Bahan 'PB: Pasir Beton / Pasir Kasar' kg", catatan=''),
    'Bata Merah (buah)': dict(jenis='Bahan', satuan='buah', min=930, max=2500, sumber="HSD Bahan 'Bata Merah'", catatan=''),
    'Batu Belah (m3)': dict(jenis='Bahan', satuan='m3', min=237188, max=380000, sumber="HSD Bahan 'Batu Belah'", catatan=''),
    'Dolken kayu 8-10 cm p.4 m (batang)': dict(jenis='Bahan', satuan='batang', min=29750, max=45000, sumber="HSD Bahan 'Dolken kayu diameter 8-10 cm panjang 4 m' batang", catatan=''),
    'Balok Kayu Kelas II (m3)': dict(jenis='Bahan', satuan='m3', min=8500000, max=12000000, sumber="HSD Bahan 'Balok Kayu Kelas II'", catatan=''),
    'Balok Kayu 6/12 Kelas II/III (m3)': dict(jenis='Bahan', satuan='m3', min=8500000, max=12000000, sumber="HSD Bahan 'Balok Kayu 6/12 Kelas II atau III'", catatan=''),
    'Papan Kayu Kelas II (m3)': dict(jenis='Bahan', satuan='m3', min=8500000, max=13072000, sumber="HSD Bahan 'Papan Kayu Kelas II'", catatan=''),
    'Keramik 30x60 Polished (buah)': dict(jenis='Bahan', satuan='buah', min=9000, max=9000, sumber="HSD Bahan 'Keramik Lantai uk. 30 x 60 cm, Polished'", catatan='Min = maks di sumber'),
    'Keramik Lantai 20x20 (buah)': dict(jenis='Bahan', satuan='buah', min=2860, max=4500, sumber="HSD Bahan 'Keramik Lantai uk. 20 x 20 cm'", catatan=''),
    'Semen Warna (kg)': dict(jenis='Bahan', satuan='kg', min=21000, max=28000, sumber="HSD Bahan 'Semen Warna'", catatan=''),
    'Genteng Beton (buah)': dict(jenis='Bahan', satuan='buah', min=11489, max=15000, sumber="HSD Bahan 'Genteng Beton'", catatan=''),
    'Baja Ringan C75 (batang)': dict(jenis='Bahan', satuan='batang', min=92795, max=155000, sumber="HSD Bahan 'Baja ringan canai dingin C75'", catatan=''),
    'Reng RT-35 (batang)': dict(jenis='Bahan', satuan='batang', min=35544, max=53000, sumber="HSD Bahan 'Reng/Roof Bottom RT-35 t=0,45 mm'", catatan=''),
    'Cat Tembok Interior (kg)': dict(jenis='Bahan', satuan='kg', min=31250, max=69000, sumber="HSD Bahan 'Cat Tembok Interior'", catatan=''),
    'Cat Tembok Eksterior (kg)': dict(jenis='Bahan', satuan='kg', min=58300, max=134600, sumber="HSD Bahan 'Cat Tembok Eksterior'", catatan=''),
    'Cat Dasar Tembok (kg)': dict(jenis='Bahan', satuan='kg', min=31275, max=58300, sumber="HSD Bahan 'Cat Dasar Tembok'", catatan=''),
    'Lem Kayu Putih (kg)': dict(jenis='Bahan', satuan='kg', min=16500, max=25000, sumber="HSD Bahan 'Lem Kayu (Putih)'", catatan=''),
    'Air (liter)': dict(jenis='Bahan', satuan='liter', min=None, max=1375, sumber='Hanya dari AHSP beton', catatan='JANGGAL: Rp 1.375 per liter tampak terlalu mahal. Cek baris Air di HSD'),
    'Kerikil (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=214, sumber='Hanya dari AHSP beton', catatan='HSD yang terkumpul hanya kerikil per m3 (279.000-305.000)'),
    'Kawat tali beton (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=21875, sumber='Hanya dari AHSP pembesian', catatan=''),
    'Baja tulangan polos BjTP <12 mm (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=16000, sumber='Hanya dari AHSP pembesian', catatan="Tidak cocok dengan 'Besi beton polos' (10.574-14.000) di HSD yang terkumpul. Cek baris aslinya"),
    'Plywood 12 mm (lbr)': dict(jenis='Bahan', satuan='lbr', min=None, max=340000, sumber='Hanya dari AHSP bekisting', catatan=''),
    'Plywood 4 mm 90x220 (lbr)': dict(jenis='Bahan', satuan='lbr', min=None, max=79000, sumber='Hanya dari AHSP pintu', catatan=''),
    'Minyak bekisting (liter)': dict(jenis='Bahan', satuan='liter', min=None, max=149900, sumber='Hanya dari AHSP bekisting', catatan=''),
    'Paku (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=28600, sumber='Hanya dari AHSP', catatan=''),
    'Paku biasa 2-5 inci (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=30000, sumber='Hanya dari AHSP genteng', catatan=''),
    'Paku sekrup (kg)': dict(jenis='Bahan', satuan='kg', min=None, max=165000, sumber='Hanya dari AHSP plafon', catatan='Rp 165.000/kg terlihat tinggi, cek'),
    'Paku sekrup 1-2 cm (buah)': dict(jenis='Bahan', satuan='buah', min=None, max=1000, sumber='Hanya dari AHSP jendela', catatan=''),
    'Papan gypsum 9 mm (lbr)': dict(jenis='Bahan', satuan='lbr', min=None, max=100000, sumber='Hanya dari AHSP plafon', catatan=''),
    'Self drilling screw 4x16 (buah)': dict(jenis='Bahan', satuan='buah', min=None, max=6020, sumber='Hanya dari AHSP rangka atap', catatan=''),
    'Self drilling screw 6x20 (buah)': dict(jenis='Bahan', satuan='buah', min=None, max=2320, sumber='Hanya dari AHSP rangka atap', catatan=''),
    'Mesin bor cordless (hari)': dict(jenis='Bahan', satuan='hari', min=None, max=50000, sumber='Hanya dari AHSP rangka atap', catatan='Mesin bor muncul dua kali (bahan dan peralatan) di sumbernya'),
    'Mesin bor listrik (jam)': dict(jenis='Peralatan', satuan='jam', min=None, max=50000, sumber='Hanya dari AHSP rangka atap', catatan=''),
    'Jendela nako rangka aluminium (m2)': dict(jenis='Bahan', satuan='m2', min=None, max=487500, sumber='Hanya dari AHSP jendela', catatan='Harga paket rangka + kaca 5 mm'),
}


OVERHEAD = 0.10   # overhead + profit pada HSP


def harga_dasar(kunci, mode="max"):
    d = HD[kunci]
    if mode == "min" and d["min"]:
        return min(d["min"], d["max"])
    return d["max"]


def hitung_ahsp(key, mode="max"):
    """Harga satuan pekerjaan dari koefisien AHSP x harga dasar (maks atau min) + overhead dan profit."""
    kode, lines = AHSP_DATA[key]
    tot = {"Tenaga Kerja": 0.0, "Bahan": 0.0, "Peralatan": 0.0}
    for kat, kom, sat, koef, kunci in lines:
        tot[kat] += koef * harga_dasar(kunci, mode)
    D = sum(tot.values())
    E = D * OVERHEAD
    return dict(A=tot["Tenaga Kerja"], B=tot["Bahan"], C=tot["Peralatan"], D=D, E=E, F=round(D + E))


def segarkan_ahsp():
    """Hitung ulang harga 21 pekerjaan ber-AHSP dari harga dasar (dipanggil lagi kalau harga dasar berubah)."""
    for key in AHSP_DATA:
        kode, uraian, sat, _a, _b, _d = KAT[key]
        KAT[key] = (kode, uraian, sat, hitung_ahsp(key)["F"], hitung_ahsp(key, "min")["F"], "AHSP")


segarkan_ahsp()


def terbilang(n):
    n = int(round(n))
    sat = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]

    def t(x):
        if x < 12:
            return sat[x]
        if x < 20:
            return t(x - 10) + " belas"
        if x < 100:
            return t(x // 10) + " puluh" + (" " + t(x % 10) if x % 10 else "")
        if x < 200:
            return "seratus" + (" " + t(x - 100) if x > 100 else "")
        if x < 1000:
            return t(x // 100) + " ratus" + (" " + t(x % 100) if x % 100 else "")
        if x < 2000:
            return "seribu" + (" " + t(x - 1000) if x > 1000 else "")
        if x < 10 ** 6:
            return t(x // 1000) + " ribu" + (" " + t(x % 1000) if x % 1000 else "")
        if x < 10 ** 9:
            return t(x // 10 ** 6) + " juta" + (" " + t(x % 10 ** 6) if x % 10 ** 6 else "")
        if x < 10 ** 12:
            return t(x // 10 ** 9) + " miliar" + (" " + t(x % 10 ** 9) if x % 10 ** 9 else "")
        return t(x // 10 ** 12) + " triliun" + (" " + t(x % 10 ** 12) if x % 10 ** 12 else "")
    return "nol" if n == 0 else t(n)

KAT_DEFAULT = dict(KAT)   # harga bawaan (bisa ditimpa oleh Google Sheet)
OPSI_DINDING = {"Bata merah 1/2 batu, campuran 1:4": "dd_bata14", "Bata merah 1/2 batu, campuran 1:3": "dd_bata13",
                "Bata ringan tebal 10 cm": "dd_ringan", "Batako": "dd_batako"}
OPSI_LANTAI = {"Keramik 20x20": "lt_2020", "Keramik 30x60 polished": "lt_3060", "Homogeneous tile 60x60": "lt_homog"}
OPSI_ATAP = {"Genteng palentong besar": ("at_palentong", "nok_palentong"), "Genteng kodok glazuur": ("at_kodok", "nok_kodok"),
             "Genteng beton": ("at_beton", "nok_beton"), "Atap metal lembaran": ("at_metal", "nok_metal")}

# Koefisien bahan per satuan pekerjaan (dari AHSP yang sudah dicek)
KOEF_BAHAN = {
    "beton": [("Semen", "kg", 348), ("Pasir beton", "kg", 790), ("Kerikil", "kg", 1009), ("Air", "liter", 202)],
    "fondasi": [("Semen", "kg", 202), ("Pasir pasang", "m3", .485), ("Batu belah", "m3", 1.2)],
    "dd_bata14": [("Bata merah", "buah", 71.91), ("Semen", "kg", 11.5), ("Pasir pasang", "m3", .043)],
    "plester": [("Semen", "kg", 6.24), ("Pasir pasang", "m3", .024)],
    "acian": [("Semen", "kg", 3.25)],
    "lt_3060": [("Keramik 30x60", "buah", 5.833), ("Pasir pasang", "m3", .027), ("Semen warna", "kg", 1.5), ("Semen", "kg", 13.632)],
    "lt_2020": [("Keramik 20x20", "buah", 26.25), ("Pasir pasang", "m3", .027), ("Semen warna", "kg", 1.5), ("Semen", "kg", 13.632)],
    "tulang_kbs": [("Baja tulangan polos", "kg", 1.05), ("Kawat tali beton", "kg", .028)],
    "tulang_slab": [("Baja tulangan polos", "kg", 1.02), ("Kawat tali beton", "kg", .015)],
    "at_beton": [("Genteng beton", "buah", 11), ("Paku biasa", "kg", .03)],
    "rangka_atap": [("Baja ringan C75", "batang", 1.156), ("Reng RT-35", "batang", .336), ("Self drilling screw", "buah", 18.75)],
    "gypsum": [("Papan gypsum 9 mm", "lembar", .364), ("Paku sekrup", "kg", .11)],
    "cat_int": [("Cat tembok", "kg", .26), ("Cat dasar tembok", "kg", .1)],
    "cat_ext": [("Cat tembok", "kg", .26), ("Cat dasar tembok", "kg", .1)],
}

ASUMSI_DEF = {
    "a_pond_atas": 0.30, "a_pond_bawah": 0.60, "a_pond_tinggi": 0.70,
    "a_sloof_b": 0.15, "a_sloof_h": 0.20, "a_kolom": 0.15, "a_kolom_jarak": 3.5,
    "a_balok_b": 0.15, "a_balok_h": 0.20, "a_plat_t": 0.12,
    "a_kg_kbs": 150.0, "a_kg_slab": 110.0, "a_miring": 30.0, "a_teritis": 0.6, "a_pasir_t": 0.10, "a_km_keramik": 1.5,
}


def segmen_dinding(R):
    """Pecah garis dinding jadi segmen dasar, lalu hitung berapa ruang tertutup yang memakainya:
    1 = dinding luar (sisi lain di luar rumah atau balkon), 2 = dinding bersama dua ruangan."""
    garis = {}
    for r in R:
        if r["open"]:
            continue
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        for arah, k, a, b in (("h", y, x, x + w), ("h", y + h, x, x + w), ("v", x, y, y + h), ("v", x + w, y, y + h)):
            garis.setdefault((arah, round(k, 4)), []).append((a, b))
    segs = []
    for (arah, k), ruas in garis.items():
        titik = sorted({round(t, 4) for a, b in ruas for t in (a, b)})
        for p, q in zip(titik, titik[1:]):
            n = sum(1 for a, b in ruas if a <= p + 1e-6 and b >= q - 1e-6)
            if n > 0 and q - p > 1e-6:
                segs.append((arah, k, p, q, n))
    return segs


def cari_segmen(segs, arah, k, pos):
    for a, kk, p, q, n in segs:
        if a == arah and abs(kk - k) < 1e-3 and p - 1e-6 <= pos <= q + 1e-6:
            return n
    return None


def analisa_lantai(P, L, f, lantai):
    """Semua volume pekerjaan arsitektur satu lantai, dibaca dari denah (DED)."""
    R, D, Wn, ST = layout(P, L, f, lantai)
    segs = segmen_dinding(R)
    ext = sum(q - p for a, k, p, q, n in segs if n == 1)
    inn = sum(q - p for a, k, p, q, n in segs if n >= 2)
    buka_luar = buka_dalam = 0.0
    daun_pintu = kusen = kaca = 0.0
    n_pintu = 0
    for d in D:
        if d["o"] == "h":
            n = cari_segmen(segs, "h", d["y"], d["x"])
        else:
            n = cari_segmen(segs, "v", d["x"], d["y"])
        luar = (n == 1) if n else True
        luas = d["w"] * T_PINTU
        if luar:
            buka_luar += luas
        else:
            buka_dalam += luas
        if d["sl"]:
            kaca += luas           # pintu kaca geser (balkon) dihitung seperti jendela kaca
        else:
            daun_pintu += luas
            kusen += 2 * T_PINTU + d["w"]
            n_pintu += 1
    for w in Wn:
        luas = w["l"] * T_JENDELA
        buka_luar += luas
        kaca += luas
    luar_face = ext * H_LANTAI - buka_luar
    dalam_face = luar_face + 2 * (inn * H_LANTAI - buka_dalam)
    tertutup = [r for r in R if not r["open"]]
    area_tertutup = sum(r["w"] * r["h"] for r in tertutup)
    area_terbuka = sum(r["w"] * r["h"] for r in R if r["open"])
    area_tangga = sum(t["w"] * t["h"] for t in ST)
    km = sum(1 for r in tertutup if r["n"] == "KM")
    km_rooms = [r for r in tertutup if r["n"] == "KM"]
    km_keliling = sum(2 * (r["w"] + r["h"]) for r in km_rooms)
    km_luas = sum(r["w"] * r["h"] for r in km_rooms)
    lebar_pintu = sum(d["w"] for d in D)
    railing_terbuka = sum(r["w"] + r["h"] for r in R if r["open"])
    titik_lampu = sum(1 + (1 if r["w"] * r["h"] > 12 else 0) for r in tertutup)
    stop_kontak = sum(2 for r in tertutup if r["n"] != "KM")
    return dict(
        ext=ext, inn=inn, panjang=ext + inn, luar=luar_face, dalam=dalam_face,
        dinding=(ext + inn) * H_LANTAI - buka_luar - buka_dalam,
        lantai=area_tertutup + area_terbuka - area_tangga, plafon=area_tertutup - (area_tangga if f == 1 and lantai > 1 else 0),
        daun_pintu=daun_pintu, kusen=kusen, kaca=kaca, n_pintu=n_pintu, km=km,
        lampu=titik_lampu, stop=stop_kontak, saklar=len(tertutup), ruang=tertutup,
        km_keliling=km_keliling, km_luas=km_luas, luas_terbuka=area_terbuka, railing=railing_terbuka,
        plint=max(0.0, ext + 2 * inn - lebar_pintu - km_keliling),
    )


def volume_dari_ded(P, L, lantai, a):
    """Rekap volume semua lantai + pekerjaan struktur dari asumsi pra-desain."""
    lantai = int(lantai)
    per = []
    for fl in range(1, lantai + 1):
        per.append(analisa_lantai(P, L, 1 if fl == 1 else 2, lantai))
    S = lambda key: sum(x[key] for x in per)
    Lp = per[0]["panjang"]
    pond_vol = Lp * (a["a_pond_atas"] + a["a_pond_bawah"]) / 2 * a["a_pond_tinggi"]
    galian = Lp * (a["a_pond_bawah"] + 0.2) * (a["a_pond_tinggi"] + 0.1)
    sloof_vol = Lp * a["a_sloof_b"] * a["a_sloof_h"]
    n_kolom = sum(max(4, math.ceil(x["panjang"] / a["a_kolom_jarak"])) for x in per)
    kolom_vol = n_kolom * a["a_kolom"] ** 2 * H_LANTAI
    balok_len = S("panjang")
    balok_vol = balok_len * a["a_balok_b"] * a["a_balok_h"]
    plat_luas = P * L if lantai >= 2 else 0.0
    plat_vol = plat_luas * a["a_plat_t"]
    teritis = a["a_teritis"]
    cos_t = math.cos(math.radians(max(5.0, min(60.0, a["a_miring"]))))
    luas_atap = (P + 2 * teritis) * (L + 2 * teritis) / cos_t
    v = dict(
        per=per, Lp=Lp, pond_vol=pond_vol, galian=galian, urugan_tanah=max(0.0, galian - pond_vol),
        sloof_vol=sloof_vol, kolom_vol=kolom_vol, n_kolom=n_kolom, balok_vol=balok_vol, balok_len=balok_len,
        plat_luas=plat_luas, plat_vol=plat_vol, luas_atap=luas_atap, nok=P + 2 * teritis,
        beton=sloof_vol + kolom_vol + balok_vol + plat_vol,
        tulang_kbs=(sloof_vol + kolom_vol + balok_vol) * a["a_kg_kbs"], tulang_slab=plat_vol * a["a_kg_slab"],
        bek_sloof=2 * a["a_sloof_h"] * Lp, bek_kolom=n_kolom * 4 * a["a_kolom"] * H_LANTAI,
        bek_balok=balok_len * (a["a_balok_b"] + 2 * a["a_balok_h"]), bek_plat=plat_luas,
        dinding=S("dinding"), plester=S("luar") + S("dalam"), luar=S("luar"), dalam=S("dalam"),
        lantai=S("lantai"), plafon=S("plafon"), daun_pintu=S("daun_pintu"), kusen=S("kusen"), kaca=S("kaca"),
        km=S("km"), lampu=S("lampu"), stop=S("stop"), saklar=S("saklar"),
        luas_dasar=P * L, area_pembersihan=(P + 2) * (L + 2), keliling_bouw=2 * ((P + 2) + (L + 2)),
        urugan_pasir=per[0]["lantai"] * a["a_pasir_t"],
    )
    # pelengkap: lisplank, plint, waterproofing, keramik dinding KM, railing, perlengkapan pintu
    v["lisplank"] = 2 * (P + 2 * teritis) + 4 * ((L / 2 + teritis) / cos_t)
    v["plint"] = S("plint")
    v["waterproof"] = S("km_luas") + S("luas_terbuka")
    v["km_dinding"] = S("km_keliling") * a["a_km_keramik"]
    v["railing_balkon"] = S("railing")
    n_pintu = S("n_pintu")
    v["kunci_biasa"] = max(0, n_pintu - v["km"])
    v["engsel"] = 3 * n_pintu
    # tangga beton (hanya rumah 2 lantai), dari ukuran tangga yang tergambar di denah
    v.update(tangga_ada=False, tangga_miring=0.0, tangga_vol=0.0, tangga_bek=0.0, tangga_railing=0.0)
    if lantai >= 2:
        ST = layout(P, L, 1, lantai)[3]
        if ST:
            run, lebar = ST[0]["h"], ST[0]["w"]
            miring = math.hypot(run, H_LANTAI)
            luas_m = lebar * miring
            v["tangga_ada"] = True
            v["tangga_miring"] = luas_m
            v["tangga_vol"] = luas_m * 0.20          # tebal ekuivalen plat + anak tangga
            v["tangga_bek"] = luas_m
            v["tangga_railing"] = miring
            v["lantai"] += lebar * (run + H_LANTAI)   # finishing injakan dan tanjakan
            v["beton"] += v["tangga_vol"]
            v["tulang_slab"] += v["tangga_vol"] * a["a_kg_slab"]
    return v


KELOMPOK = ["Persiapan dan tanah", "Pondasi dan struktur", "Dinding dan plester", "Lantai", "Atap dan plafon",
            "Pintu dan jendela", "Finishing cat", "Sanitair dan listrik", "Tangga dan railing"]


def susun_rab(P, L, lantai, pil_dinding, pil_lantai, pil_atap, a):
    """Daftar pekerjaan: (kelompok, kunci katalog, volume)."""
    v = volume_dari_ded(P, L, lantai, a)
    dd = OPSI_DINDING[pil_dinding]
    lt = OPSI_LANTAI[pil_lantai]
    at, nok = OPSI_ATAP[pil_atap]
    baris = [
        ("Persiapan dan tanah", "pembersihan", v["area_pembersihan"]),
        ("Persiapan dan tanah", "bouwplank", v["keliling_bouw"]),
        ("Persiapan dan tanah", "galian", v["galian"]),
        ("Persiapan dan tanah", "urugan_tanah", v["urugan_tanah"]),
        ("Persiapan dan tanah", "urugan_pasir", v["urugan_pasir"]),
        ("Pondasi dan struktur", "fondasi", v["pond_vol"]),
        ("Pondasi dan struktur", "beton", v["beton"]),
        ("Pondasi dan struktur", "tulang_kbs", v["tulang_kbs"]),
        ("Pondasi dan struktur", "bek_sloof", v["bek_sloof"]),
        ("Pondasi dan struktur", "bek_kolom", v["bek_kolom"]),
        ("Pondasi dan struktur", "bek_balok", v["bek_balok"]),
    ]
    if v["plat_luas"] > 0:
        baris += [("Pondasi dan struktur", "tulang_slab", v["tulang_slab"]),
                  ("Pondasi dan struktur", "bek_plat", v["bek_plat"])]
    baris += [
        ("Dinding dan plester", dd, v["dinding"]),
        ("Dinding dan plester", "plester", v["plester"]),
        ("Dinding dan plester", "acian", v["plester"]),
        ("Lantai", lt, v["lantai"]),
        ("Atap dan plafon", "rangka_atap", v["luas_atap"]),
        ("Atap dan plafon", at, v["luas_atap"]),
        ("Atap dan plafon", nok, v["nok"]),
        ("Atap dan plafon", "gypsum", v["plafon"]),
        ("Atap dan plafon", "rangka_plafon", v["plafon"]),
        ("Pintu dan jendela", "pintu", v["daun_pintu"]),
        ("Pintu dan jendela", "kusen", v["kusen"]),
        ("Pintu dan jendela", "jendela", v["kaca"]),
        ("Finishing cat", "cat_int", v["dalam"]),
        ("Finishing cat", "cat_ext", v["luar"]),
        ("Finishing cat", "cat_plafon", v["plafon"]),
        ("Sanitair dan listrik", "closet", v["km"]),
        ("Sanitair dan listrik", "kran", 2 * v["km"]),
        ("Sanitair dan listrik", "floor_drain", v["km"]),
        ("Sanitair dan listrik", "lampu", v["lampu"]),
        ("Sanitair dan listrik", "stop_kontak", v["stop"]),
        ("Sanitair dan listrik", "saklar", v["saklar"]),
    ]
    plint = {"lt_2020": "plint_30", "lt_3060": "plint_60", "lt_homog": "plint_homog"}[lt]
    baris += [
        ("Lantai", plint, v["plint"]),
        ("Lantai", "waterproof", v["waterproof"]),
        ("Dinding dan plester", "dd_keramik_km", v["km_dinding"]),
        ("Atap dan plafon", "lisplank", v["lisplank"]),
        ("Pintu dan jendela", "kunci_biasa", v["kunci_biasa"]),
        ("Pintu dan jendela", "kunci_km", v["km"]),
        ("Pintu dan jendela", "engsel", v["engsel"]),
        ("Sanitair dan listrik", "wastafel", v["km"]),
        ("Sanitair dan listrik", "shower", v["km"]),
        ("Tangga dan railing", "railing_balkon", v["railing_balkon"]),
    ]
    if v["tangga_ada"]:
        baris += [("Pondasi dan struktur", "bek_tangga", v["tangga_bek"]),
                  ("Tangga dan railing", "railing_tangga", v["tangga_railing"])]
    baris = [b for b in baris if round(b[2], 2) > 0]
    rows = []
    for kel, key, vol in baris:
        kode, uraian, sat, atas, bawah, dasar = KAT[key]
        vol = round(vol, 2)
        rows.append(dict(kelompok=kel, key=key, kode=kode, uraian=uraian, satuan=sat, volume=vol,
                         harga=atas, jumlah_atas=round(vol * atas), jumlah_bawah=round(vol * (bawah if bawah else atas)),
                         dasar=dasar, punya_bawah=bool(bawah)))
    return rows, v


def daftar_bahan(rows):
    """Jumlahkan kebutuhan bahan dari pekerjaan yang AHSP-nya sudah ada."""
    tot, tanpa = {}, []
    for r in rows:
        k = KOEF_BAHAN.get(r["key"])
        if not k:
            if r["dasar"] == "HSP" and r["key"] in ("dd_bata13", "dd_ringan", "dd_batako", "lt_homog", "at_palentong", "at_kodok", "at_metal"):
                tanpa.append(r["uraian"])
            continue
        for nama, sat, koef in k:
            key = (nama, sat)
            tot[key] = tot.get(key, 0) + koef * r["volume"]
    return tot, tanpa

# ============================================================
#  TAMPILAN (CSS tambahan, animasi, halaman)
# ============================================================
CSS_EXTRA = r"""
@keyframes rh-draw{to{stroke-dashoffset:0}}
@keyframes rh-fade{from{opacity:0}to{opacity:1}}
@keyframes rh-up{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes rh-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes rh-pulse{0%,100%{opacity:.55}50%{opacity:1}}
/* animasi DED: dinding digambar, lalu pintu/jendela, lalu label */
.rh-anim .rh-rm{stroke-dasharray:1;stroke-dashoffset:1;animation:rh-draw 1.8s ease-out forwards}
.rh-anim .rh-rmopen{animation:rh-fade 1s ease-out 1.6s both}
.rh-anim .rh-pop,.rh-anim .rh-dl,.rh-anim .rh-dr,.rh-anim .rh-wl{animation:rh-fade .7s ease-out 1.7s both}
.rh-anim .rh-stp{animation:rh-fade .7s ease-out 1.9s both}
.rh-anim .rh-rmt,.rh-anim .rh-ar{animation:rh-fade .8s ease-out 2.2s both}
.rh-anim .rh-dm,.rh-anim .rh-dim,.rh-anim .rh-nv,.rh-anim .rh-na,.rh-anim .rh-ttl{animation:rh-fade .8s ease-out 2.6s both}
/* beranda */
.bn-hero{display:flex;flex-wrap:wrap;align-items:center;gap:24px;background:linear-gradient(135deg,#1E293B,#0F172A);
  border-bottom:5px solid #E08E9B;border-radius:24px;padding:30px 34px;color:#fff;overflow:hidden}
.bn-text{flex:1 1 320px;min-width:260px}
.bn-kick{margin:0 0 8px;font-size:.78rem;font-weight:800;letter-spacing:.14em;color:#E08E9B}
.bn-hero h1{margin:0;font-size:clamp(2.2rem,6vw,3.4rem);font-weight:800;line-height:1.05;color:#fff;animation:rh-up .8s ease-out both}
.bn-sub{margin:12px 0 18px;font-size:1.02rem;line-height:1.5;color:#F8E1E5;animation:rh-up .8s ease-out .2s both}
.bn-count{display:inline-block;background:rgba(224,142,155,.14);border:1px solid rgba(224,142,155,.4);border-radius:16px;
  padding:12px 18px;animation:rh-up .8s ease-out .4s both}
.bn-count small{display:block;color:#E08E9B;font-weight:700;font-size:.74rem}
.bn-count b{display:block;font-family:'Fira Code',ui-monospace,monospace;font-size:clamp(1.3rem,4.4vw,1.9rem);color:#34d399;font-weight:600}
.bn-house{flex:0 0 280px;width:280px;max-width:100%;animation:rh-float 5s ease-in-out infinite}
.bn-d{stroke-dasharray:1;stroke-dashoffset:1;animation:rh-draw 1.3s ease-out forwards}
.bn-f{animation:rh-fade 1s ease-out 2s both}
.bn-sun{animation:rh-pulse 3s ease-in-out infinite}
.bn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:20px}
.bn-card{background:#fff;border:1px solid #F8E1E5;border-radius:20px;padding:20px;color:#1E293B;
  box-shadow:0 2px 12px rgba(184,91,108,.08);animation:rh-up .7s ease-out both;transition:transform .25s,box-shadow .25s}
.bn-card:hover{transform:translateY(-4px);box-shadow:0 10px 24px rgba(184,91,108,.18)}
.bn-card i{font-style:normal;font-size:1.6rem}
.bn-card h3{margin:8px 0 6px;font-size:1.02rem;font-weight:800;color:#B85B6C}
.bn-card p{margin:0;font-size:.88rem;line-height:1.5;color:#475569}
@media (prefers-reduced-motion:reduce){*{animation:none !important;transition:none !important}
  .rh-anim .rh-rm,.bn-d{stroke-dashoffset:0 !important}}
"""
CSS += CSS_EXTRA

COUNT_JS = r"""<script>
(function(){
 var els=document.querySelectorAll('[data-count]');
 var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 els.forEach(function(el){
  var v=parseFloat(el.getAttribute('data-count')),pre=el.getAttribute('data-pre')||'';
  var fmt=function(n){return pre+Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g,'.');};
  if(reduce||!isFinite(v)){el.textContent=fmt(v);return;}
  var t0=null,dur=1500;
  function step(ts){if(!t0)t0=ts;var p=Math.min((ts-t0)/dur,1);var e=1-Math.pow(1-p,3);
   el.textContent=fmt(v*e);if(p<1)requestAnimationFrame(step);}
  requestAnimationFrame(step);
 });
})();
</script>"""


def tampil(html, tinggi=300, countup=False, nonce=""):
    """Tampilkan HTML/SVG/animasi di dalam iframe sendiri (CSS dan skrip ikut terbawa)."""
    dasar = "body{margin:0;background:transparent;font-family:'Nunito',system-ui,-apple-system,'Segoe UI',sans-serif}"
    js = COUNT_JS if countup else ""
    components.html(f"<style>{CSS}{dasar}</style>{inline_svg(html)}<!--{nonce}-->{js}", height=tinggi, scrolling=True)


def beranda_html(contoh, P, L, lantai):
    kartu = [
        ("💰", "Estimasi cepat", "Total biaya dari luas dan harga SHST, status anggaran, dan perbandingan 1 sampai 2 lantai."),
        ("📐", "Lahan dan DED", "Cek KDB, KLB, sempadan, dan lihat denah gaya DED yang tergambar otomatis dari ukuran rumahmu."),
        ("🧮", "RAB dari DED", "Volume pekerjaan dibaca dari gambar denah, dikali harga satuan resmi, lengkap dengan rentang biaya."),
        ("📊", "Data harga resmi", "Harga satuan Kota Magelang dari MAS PETRUK (DPU Bina Marga dan Cipta Karya Jateng) beserta sumbernya."),
    ]
    k = "".join(f'<div class="bn-card" style="animation-delay:{0.5 + i * 0.15:.2f}s"><i>{ic}</i><h3>{jd}</h3><p>{tx}</p></div>'
                for i, (ic, jd, tx) in enumerate(kartu))
    rumah = """<svg class="bn-house" viewBox="0 0 320 250" aria-hidden="true">
      <g class="bn-sun"><circle cx="270" cy="38" r="16" fill="#E08E9B"/></g>
      <g fill="none" stroke="#E08E9B" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
        <path class="bn-d" pathLength="1" style="animation-delay:.1s" d="M14,226 H306"/>
        <path class="bn-d" pathLength="1" style="animation-delay:.5s" d="M52,226 V122 H268 V226"/>
        <path class="bn-d" pathLength="1" style="animation-delay:1s" d="M32,128 L160,42 L288,128 Z"/>
        <path class="bn-d" pathLength="1" style="animation-delay:1.5s" d="M138,226 V168 H182 V226"/>
        <path class="bn-d" pathLength="1" style="animation-delay:1.8s" d="M72,150 H116 V190 H72 Z M204,150 H248 V190 H204 Z"/>
        <path class="bn-d" pathLength="1" style="animation-delay:2.1s" d="M72,170 H116 M94,150 V190 M204,170 H248 M226,150 V190"/>
      </g>
      <path class="bn-f" d="M160,60 L262,124 H58 Z" fill="#E08E9B" opacity=".16"/>
    </svg>"""
    return f"""<div>
      <div class="bn-hero">
        <div class="bn-text">
          <p class="bn-kick">KOTA MAGELANG · RUMAH 1-2 LANTAI</p>
          <h1>Rumah Hitung</h1>
          <p class="bn-sub">Dari gambar DED sampai RAB: hitung biaya, cek lahan, dan lihat denah rumahmu dalam satu aplikasi.</p>
          <div class="bn-count"><small>Estimasi rumahmu sekarang ({idn(P)} × {idn(L)} m, {lantai} lantai, Standar)</small>
            <b data-count="{jround(contoh)}" data-pre="Rp ">{rp(contoh)}</b></div>
        </div>
        {rumah}
      </div>
      <div class="bn-grid">{k}</div>
    </div>"""


def legenda_html(P, L, viewF, lantai):
    R, D, Wn, ST = layout(P, L, 1 if viewF == 1 else 2, lantai)
    a = analisa_lantai(P, L, 1 if viewF == 1 else 2, lantai)
    baris = "".join(
        f'<tr><td style="text-align:left">{r["n"]}</td><td>{fm(r["w"])} × {fm(r["h"])} m</td>'
        f'<td>{fm(r["w"] * r["h"])} m²</td><td>{"terbuka" if r["open"] else "tertutup"}</td></tr>' for r in R)
    ringkas_ = (f'<p class="rh-hint">Dari denah ini: panjang dinding <b>{fm(a["panjang"])} m</b> '
                f'(luar {fm(a["ext"])} m, sekat {fm(a["inn"])} m), luas dinding bersih <b>{fm(a["dinding"])} m²</b>, '
                f'{a["n_pintu"]} pintu, jendela dan kaca <b>{fm(a["kaca"])} m²</b>.</p>')
    tabel = ('<table class="rh-cmp"><tr><th style="text-align:left">Ruang</th><th>Ukuran</th><th>Luas</th><th>Jenis</th></tr>'
             f'{baris}</table>')
    return card(f"Daftar ruang lantai {viewF}", tabel + ringkas_)


# ------------------------------------------------------------
#  STATE
# ------------------------------------------------------------
MENU = ["🏠 Beranda", "💰 Estimasi Cepat", "📐 Lahan & DED", "🧮 RAB dari DED", "📊 Data Harga", "📖 Panduan"]
DEF = dict(menu=MENU[0], P=9.0, L=7.0, lantai=2, tipe="standar", sumber="mas", hm=0.0, B=800000000.0,
           TW=12.0, TP=20.0, KDB=60.0, KLB=1.2, GD=3.0, GS=1.0, viewF=1, nonce=0,
           pil_dinding="Bata merah 1/2 batu, campuran 1:4", pil_lantai="Keramik 30x60 polished",
           pil_atap="Genteng beton", ppn=11.0)
DEF.update(ASUMSI_DEF)

st.set_page_config(page_title="Rumah Hitung", page_icon="🏠", layout="wide")
for _k, _v in DEF.items():
    st.session_state.setdefault(_k, _v)
for _k in DEF:                      # jaga nilai tetap ada saat pindah menu
    st.session_state[_k] = st.session_state[_k]
SS = st.session_state


def ke_menu(m):
    SS.menu = m


def ulang_animasi():
    SS.nonce = SS.nonce + 1


def pakai_ukuran_maks():
    nP, nL = pakai_maksimal(SS.P, SS.L, SS.lantai, SS.TW, SS.TP, SS.KDB, SS.KLB, SS.GD, SS.GS)
    SS.P, SS.L = float(nP), float(nL)



# ------------------------------------------------------------
#  HARGA DARI GOOGLE SHEET (opsional)
# ------------------------------------------------------------
HARGA_DASAR_CSV_URL = ""   # link CSV sheet Harga_Dasar (upah dan bahan), atau isi lewat Secrets dengan nama yang sama
HSP_CSV_URL = ""           # link CSV sheet HSP_Mentah (tabel HSP lengkap), atau isi lewat Secrets dengan nama yang sama


def _angka(x):
    s = re.sub(r"[^\d]", "", str(x).split(",")[0] if str(x).count(",") == 1 and str(x).rstrip().endswith(",-") else str(x))
    return int(s) if s else 0


def _baca_csv(url, wajib):
    """Baca CSV Google Sheet (atau file lokal). Baris judul kolom dicari otomatis, boleh ada judul atau baris kosong di atasnya."""
    import csv
    import io
    import urllib.request
    if str(url).startswith("http"):
        with urllib.request.urlopen(url, timeout=15) as resp:
            teks = resp.read().decode("utf-8-sig")
    else:
        with open(url, encoding="utf-8-sig") as fh:
            teks = fh.read()
    baris = list(csv.reader(io.StringIO(teks)))
    lebar = max((len(x) for x in baris), default=0)
    baris = [list(x) + [""] * (lebar - len(x)) for x in baris]
    for i in range(min(len(baris), 15)):
        sel = [str(c).strip().lower() for c in baris[i]]
        if all(any(w in s for s in sel) for w in wajib):
            return pd.DataFrame(baris[i + 1:], columns=sel)
    raise ValueError("baris judul kolom tidak ditemukan: " + ", ".join(wajib))


@st.cache_data(ttl=600, show_spinner=False)
def baca_harga_dasar(url):
    d = _baca_csv(url, ["kunci", "harga_maks"])
    kmin = next((c for c in d.columns if "harga_min" in c), None)
    kmax = next(c for c in d.columns if "harga_maks" in c)
    out = {}
    for _, r in d.iterrows():
        k = str(r["kunci"]).strip()
        mx = _angka(r[kmax])
        mn = _angka(r[kmin]) if kmin else 0
        if k and mx > 0:
            out[k] = (mn, mx)
    return out


@st.cache_data(ttl=600, show_spinner=False)
def baca_hsp(url):
    d = _baca_csv(url, ["kode", "harga"])
    kh = next(c for c in d.columns if "harga" in c)
    out = {}
    for _, r in d.iterrows():
        kode = re.sub(r"\s*\([a-z]\)\s*$", "", str(r["kode"]).strip())
        h = _angka(r[kh])
        if kode and h > 0:
            out[kode] = h
    return out


def _url(konstanta, nama):
    if konstanta:
        return konstanta
    try:
        return st.secrets.get(nama, "")
    except Exception:
        return ""


def terapkan_harga_sheet():
    """Timpa harga bawaan dengan Google Sheet (kalau link tersedia). Mengembalikan daftar (status, teks)."""
    hasil = []
    u1 = _url(HARGA_DASAR_CSV_URL, "HARGA_DASAR_CSV_URL")
    if u1:
        try:
            data = baca_harga_dasar(u1)
            n = 0
            for k, (mn, mx) in data.items():
                if k in HD:
                    HD[k]["max"] = mx
                    HD[k]["min"] = mn if 0 < mn <= mx else (HD[k]["min"] if HD[k]["min"] and HD[k]["min"] <= mx else None)
                    n += 1
            segarkan_ahsp()
            hasil.append(("ok", f"Harga dasar: Google Sheet ({n} item), AHSP dihitung ulang"))
        except Exception:
            hasil.append(("gagal", "Harga dasar: bawaan (Google Sheet gagal dibaca)"))
    u2 = _url(HSP_CSV_URL, "HSP_CSV_URL")
    if u2:
        try:
            data = baca_hsp(u2)
            n = 0
            for key, (kode, uraian, sat, atas, bawah, dasar) in list(KAT.items()):
                if dasar == "HSP" and kode in data:
                    KAT[key] = (kode, uraian, sat, data[kode], None, "HSP")
                    n += 1
            hasil.append(("ok", f"Harga HSP: Google Sheet ({n} pekerjaan)"))
        except Exception:
            hasil.append(("gagal", "Harga HSP: bawaan (Google Sheet gagal dibaca)"))
    if not hasil:
        hasil.append(("bawaan", "Harga: bawaan aplikasi (MAS PETRUK Edisi I 2026)"))
    return hasil


STATUS_HARGA = terapkan_harga_sheet()

# ------------------------------------------------------------
#  SIDEBAR
# ------------------------------------------------------------
st.sidebar.markdown("### 🏠 Rumah Hitung")
st.sidebar.caption("Kota Magelang · rumah 1-2 lantai")
menu = st.sidebar.radio("Menu", MENU, key="menu", label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("**Ukuran rumah**")
st.sidebar.number_input("Panjang (m)", min_value=3.0, max_value=40.0, step=0.5, key="P")
st.sidebar.number_input("Lebar (m)", min_value=3.0, max_value=40.0, step=0.5, key="L")
st.sidebar.radio("Jumlah lantai", [1, 2], horizontal=True, key="lantai", format_func=lambda v: f"{v} lantai")
st.sidebar.caption("Ukuran ini dipakai di semua menu.")
st.sidebar.markdown("---")
for _stt, _txt in STATUS_HARGA:
    st.sidebar.caption(_txt)
P, L, lantai = float(SS.P), float(SS.L), int(SS.lantai)


# ------------------------------------------------------------
#  HALAMAN
# ------------------------------------------------------------
def page_beranda():
    contoh = P * L * lantai * HARGA[SS.sumber]["standar"]
    tampil(beranda_html(contoh, P, L, lantai), 640, countup=True)
    c = st.columns(4)
    for col, m in zip(c, MENU[1:5]):
        col.button(f"{m} →", on_click=ke_menu, args=(m,), key=f"go_{m}")


def page_estimasi():
    st.subheader("Estimasi cepat")
    c1, c2 = st.columns([4, 6], gap="large")
    with c1:
        st.radio("Kualitas bangunan", ["hemat", "standar", "premium"], key="tipe", horizontal=True, format_func=str.capitalize)
        st.number_input("Harga bangun per m² (Rp), 0 = pakai SHST", min_value=0.0, step=100000.0, key="hm")
        st.number_input("Anggaran (Rp), 0 = belum ada", min_value=0.0, step=10000000.0, key="B")
        st.caption("Acuan harga: SHST rumah negara Kota Magelang dari MAS PETRUK (DPU Bina Marga dan Cipta Karya Provinsi Jawa Tengah).")
    hero, cmp_html, _l, _d, _p, _m = hitung(P, L, lantai, SS.sumber, SS.tipe, SS.hm, SS.B, SS.TW, SS.TP, SS.KDB, SS.KLB, SS.GD, SS.GS, 1)
    with c2:
        tampil(hero, 250, countup=True)
        tampil(cmp_html, 290)
    st.caption("Estimasi ini luas × harga per m². Untuk hitungan per pekerjaan, buka menu RAB dari DED.")


def page_ded():
    st.subheader("Lahan dan DED")
    c1, c2 = st.columns([4, 7], gap="large")
    with c1:
        a, b = st.columns(2)
        a.number_input("Lebar tanah (m)", min_value=1.0, step=0.5, key="TW")
        b.number_input("Panjang tanah (m)", min_value=1.0, step=0.5, key="TP")
        a.number_input("KDB maks (%)", min_value=1.0, max_value=100.0, step=5.0, key="KDB")
        b.number_input("KLB maks (kali)", min_value=0.1, step=0.1, key="KLB")
        a.number_input("Sempadan depan (m)", min_value=0.0, step=0.5, key="GD")
        b.number_input("Sempadan samping/belakang (m)", min_value=0.0, step=0.5, key="GS")
        st.caption("Angka bawaan hanya contoh. Isi sesuai KRK atau RDTR lokasi lahanmu.")
        st.button("📐 Pakai ukuran rumah maksimal di lahan ini", on_click=pakai_ukuran_maks)
    with c2:
        if lantai > 1:
            if SS.viewF > lantai:
                SS.viewF = 1
            st.radio("Denah lantai yang ditampilkan", [1, 2], horizontal=True, key="viewF", format_func=lambda v: f"Lantai {v}")
            vf = int(SS.viewF)
        else:
            vf = 1
        st.button("▶ Putar ulang animasi", on_click=ulang_animasi)
        den = card("Denah rumah (gaya gambar DED)", denah_svg(P, L, vf, lantai, anim=True) +
                   '<p class="rh-hint">Ilustrasi pembagian ruang dari ukuran yang kamu isi, bukan gambar kerja.</p>')
        tampil(den, 640, nonce=f"{vf}-{SS.nonce}-{P}-{L}-{lantai}")
    d = data_lahan(SS.TW, SS.TP, SS.KDB, SS.KLB, SS.GD, SS.GS)
    k1, k2 = st.columns([7, 5], gap="large")
    with k1:
        tampil(card("Cek kelayakan lahan (KDB / KLB / sempadan)", lahan_html(P, L, lantai, d)), 720)
    with k2:
        tampil(legenda_html(P, L, vf, lantai), 560)


def fmt_tabel(rows):
    out = []
    for r in rows:
        out.append({"Kelompok": r["kelompok"], "Kode": r["kode"], "Pekerjaan": r["uraian"],
                    "Volume": idn(r["volume"], 2), "Satuan": r["satuan"], "Harga satuan (Rp)": num(r["harga"]),
                    "Jumlah harga (Rp)": num(r["jumlah_atas"]), "Dasar harga": r["dasar"]})
    return pd.DataFrame(out)


ROMAWI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def buat_rab_resmi(rows, ppn, meta, rv, bahan, asumsi, bawah_total):
    """Excel RAB berformat resmi: REKAPITULASI, RAB, AHSP, Harga_Dasar, Volume, Bahan, Batas_Bawah, Catatan.
    Harga satuan di RAB mengambil dari sheet AHSP, dan AHSP mengambil dari Harga_Dasar (rumus hidup)."""
    import io
    import xlsxwriter
    bio = io.BytesIO()
    wb = xlsxwriter.Workbook(bio, {"in_memory": True})
    F = lambda **k: wb.add_format({"font_name": "Arial", "font_size": 10, **k})
    f_judul = F(bold=True, font_size=14, align="center")
    f_b = F(bold=True)
    f_head = F(bold=True, border=1, align="center", valign="vcenter", bg_color="#F8E1E5", text_wrap=True)
    f_t = F(border=1, valign="top", text_wrap=True)
    f_tc = F(border=1, align="center", valign="top")
    f_n2 = F(border=1, num_format="#,##0.00", valign="top")
    f_k = F(border=1, num_format="0.0000##", valign="top")
    f_rp = F(border=1, num_format="#,##0", valign="top")
    f_div = F(bold=True, border=1, bg_color="#FDF2F4")
    f_divc = F(bold=True, border=1, bg_color="#FDF2F4", align="center")
    f_tot = F(bold=True, border=1, num_format="#,##0", bg_color="#FDF2F4")
    f_tott = F(bold=True, border=1, bg_color="#FDF2F4", align="right")
    f_ital = F(italic=True, font_color="#475569", text_wrap=True, valign="top")
    f_grey = F(border=1, font_color="#808080", font_size=8, valign="top")
    f_pct = F(num_format="0.0")
    ws_rek = wb.add_worksheet("REKAPITULASI")
    ws_rab = wb.add_worksheet("RAB")
    ws_ah = wb.add_worksheet("AHSP")
    ws_hd = wb.add_worksheet("Harga_Dasar")
    ws_vol = wb.add_worksheet("Volume")
    ws_bhn = wb.add_worksheet("Bahan")
    ws_bwh = wb.add_worksheet("Batas_Bawah")
    ws_cat = wb.add_worksheet("Catatan")

    # ---------------- Harga_Dasar
    ws_hd.write("A1", "HARGA DASAR UPAH, BAHAN, DAN PERALATAN (Kota Magelang)", f_b)
    for c, h in enumerate(["Kunci", "Jenis", "Satuan", "Harga minimum (Rp)", "Harga maksimum (Rp)", "Sumber", "Catatan"]):
        ws_hd.write(2, c, h, f_head)
    for i, (k, d) in enumerate(HD.items()):
        r = 3 + i
        ws_hd.write(r, 0, k, f_t)
        ws_hd.write(r, 1, d["jenis"], f_t)
        ws_hd.write(r, 2, d["satuan"], f_t)
        if d["min"]:
            ws_hd.write_number(r, 3, d["min"], f_rp)
        else:
            ws_hd.write_blank(r, 3, None, f_rp)
        ws_hd.write_number(r, 4, d["max"], f_rp)
        ws_hd.write(r, 5, d["sumber"], f_t)
        ws_hd.write(r, 6, d["catatan"], f_t)
    for c, w in enumerate([38, 10, 9, 18, 18, 46, 60]):
        ws_hd.set_column(c, c, w)
    ws_hd.freeze_panes(3, 0)

    # ---------------- AHSP
    ws_ah.merge_range("A1:G1", "ANALISA HARGA SATUAN PEKERJAAN (AHSP)", f_judul)
    ws_ah.write("A3", "Overhead dan profit (%)", f_b)
    ws_ah.write_number("C3", OVERHEAD * 100, f_pct)
    for c, w in enumerate([6, 50, 10, 12, 18, 18, 38]):
        ws_ah.set_column(c, c, w)
    dipakai, f_row, r = [], {}, 4
    for rw in rows:
        if rw["key"] in AHSP_DATA and rw["key"] not in dipakai:
            dipakai.append(rw["key"])
    for key in dipakai:
        kode, lines = AHSP_DATA[key]
        uraian, sat = KAT[key][1], KAT[key][2]
        hs = hitung_ahsp(key)
        ws_ah.write(r, 0, "Kode", f_b)
        ws_ah.merge_range(r, 1, r, 6, f"{kode}  {uraian}", f_b)
        ws_ah.write(r + 1, 0, "Satuan", f_b)
        ws_ah.write(r + 1, 1, sat, f_t)
        for c, h in enumerate(["NO", "URAIAN", "SATUAN", "KOEFISIEN", "HARGA SATUAN (Rp)", "JUMLAH HARGA (Rp)", "RUJUKAN HARGA DASAR"]):
            ws_ah.write(r + 2, c, h, f_head)
        r += 3
        sub_cells, sub_vals = {}, {}
        for kat, label, huruf in (("Tenaga Kerja", "A. TENAGA KERJA", "A"), ("Bahan", "B. BAHAN", "B"), ("Peralatan", "C. PERALATAN", "C")):
            ws_ah.merge_range(r, 0, r, 6, label, f_div)
            r += 1
            awal = r
            no = 0
            for kt, kom, sk, koef, kunci in lines:
                if kt != kat:
                    continue
                no += 1
                n = r + 1
                hrg = harga_dasar(kunci)
                ws_ah.write_number(r, 0, no, f_tc)
                ws_ah.write(r, 1, kom, f_t)
                ws_ah.write(r, 2, sk, f_tc)
                ws_ah.write_number(r, 3, koef, f_k)
                ws_ah.write_formula(r, 4, f"=VLOOKUP(G{n},Harga_Dasar!$A:$E,5,FALSE)", f_rp, hrg)
                ws_ah.write_formula(r, 5, f"=D{n}*E{n}", f_rp, koef * hrg)
                ws_ah.write(r, 6, kunci, f_grey)
                r += 1
            ws_ah.merge_range(r, 0, r, 4, f"Jumlah harga {label.split('. ')[1].lower()}", f_tott)
            nilai = hs[huruf]
            if r > awal:
                ws_ah.write_formula(r, 5, f"=SUM(F{awal + 1}:F{r})", f_tot, nilai)
            else:
                ws_ah.write_number(r, 5, 0, f_tot)
            sub_cells[huruf] = f"F{r + 1}"
            r += 1
        ws_ah.merge_range(r, 0, r, 4, "D. Jumlah harga tenaga, bahan, dan peralatan (A+B+C)", f_tott)
        ws_ah.write_formula(r, 5, f"={sub_cells['A']}+{sub_cells['B']}+{sub_cells['C']}", f_tot, hs["D"])
        d_cell = f"F{r + 1}"
        r += 1
        ws_ah.merge_range(r, 0, r, 4, "E. Overhead dan profit", f_tott)
        ws_ah.write_formula(r, 5, f"={d_cell}*$C$3/100", f_tot, hs["E"])
        e_cell = f"F{r + 1}"
        r += 1
        ws_ah.merge_range(r, 0, r, 4, "F. HARGA SATUAN PEKERJAAN (D+E)", f_tott)
        ws_ah.write_formula(r, 5, f"=ROUND({d_cell}+{e_cell},0)", f_tot, hs["F"])
        f_row[key] = r + 1
        r += 2
    ws_ah.set_paper(9)
    ws_ah.fit_to_pages(1, 0)
    ws_ah.set_footer("&CHalaman &P dari &N")

    # ---------------- RAB
    ws_rab.merge_range("A1:G1", "RENCANA ANGGARAN BIAYA (RAB)", f_judul)
    for i, (lb, vl) in enumerate([("Pekerjaan", meta["pekerjaan"]), ("Lokasi", meta["lokasi"]), ("Tahun anggaran", meta["tahun"]),
                                  ("Sumber harga", meta["sumber"])]):
        ws_rab.merge_range(2 + i, 0, 2 + i, 6, f"{lb}  : {vl}", F())
    for c, h in enumerate(["NO", "URAIAN PEKERJAAN", "KODE HSP", "VOLUME", "SATUAN", "HARGA SATUAN (Rp)", "JUMLAH HARGA (Rp)"]):
        ws_rab.write(7, c, h, f_head)
    r = 8
    sub_rab, divisi_n = {}, 0
    for kel in KELOMPOK:
        item = [x for x in rows if x["kelompok"] == kel]
        if not item:
            continue
        ws_rab.write(r, 0, ROMAWI[divisi_n], f_divc)
        ws_rab.merge_range(r, 1, r, 6, "PEKERJAAN " + kel.upper(), f_div)
        divisi_n += 1
        r += 1
        awal = r
        for i, x in enumerate(item, 1):
            n = r + 1
            ws_rab.write_number(r, 0, i, f_tc)
            ws_rab.write(r, 1, x["uraian"], f_t)
            ws_rab.write(r, 2, x["kode"], f_tc)
            ws_rab.write_number(r, 3, x["volume"], f_n2)
            ws_rab.write(r, 4, x["satuan"], f_tc)
            if x["key"] in f_row:
                ws_rab.write_formula(r, 5, f"=AHSP!$F${f_row[x['key']]}", f_rp, x["harga"])
            else:
                ws_rab.write_number(r, 5, x["harga"], f_rp)
            ws_rab.write_formula(r, 6, f"=ROUND(D{n}*F{n},0)", f_rp, x["jumlah_atas"])
            r += 1
        ws_rab.merge_range(r, 0, r, 5, "Jumlah " + kel, f_tott)
        ws_rab.write_formula(r, 6, f"=SUM(G{awal + 1}:G{r})", f_tot, sum(x["jumlah_atas"] for x in item))
        sub_rab[kel] = (r + 1, sum(x["jumlah_atas"] for x in item), ROMAWI[divisi_n - 1])
        r += 2
    for c, w in enumerate([6, 52, 13, 11, 9, 19, 20]):
        ws_rab.set_column(c, c, w)
    ws_rab.set_paper(9)
    ws_rab.fit_to_pages(1, 0)
    ws_rab.repeat_rows(7)
    ws_rab.set_footer("&CHalaman &P dari &N")
    ws_rab.freeze_panes(8, 0)

    # ---------------- REKAPITULASI
    jumlah = sum(v[1] for v in sub_rab.values())
    ppn_rp = round(jumlah * ppn / 100)
    total = jumlah + ppn_rp
    bulat = round(total, -3)
    ws_rek.merge_range("A1:C1", "REKAPITULASI RENCANA ANGGARAN BIAYA", f_judul)
    for i, (lb, vl) in enumerate([("Pekerjaan", meta["pekerjaan"]), ("Lokasi", meta["lokasi"]), ("Tahun anggaran", meta["tahun"])]):
        ws_rek.merge_range(2 + i, 0, 2 + i, 2, f"{lb}  : {vl}", F())
    ws_rek.write(5, 1, "PPN (%)", F(bold=True, align="right"))
    ws_rek.write_number(5, 2, ppn, f_pct)
    for c, h in enumerate(["NO", "URAIAN PEKERJAAN", "JUMLAH HARGA (Rp)"]):
        ws_rek.write(7, c, h, f_head)
    r = 8
    awal = r
    for kel, (nr, nilai, rom) in sub_rab.items():
        ws_rek.write(r, 0, rom, f_tc)
        ws_rek.write(r, 1, "Pekerjaan " + kel.lower(), f_t)
        ws_rek.write_formula(r, 2, f"=RAB!$G${nr}", f_rp, nilai)
        r += 1
    j = r + 1
    ws_rek.merge_range(r, 0, r, 1, "JUMLAH", f_tott)
    ws_rek.write_formula(r, 2, f"=SUM(C{awal + 1}:C{r})", f_tot, jumlah)
    ws_rek.merge_range(r + 1, 0, r + 1, 1, "PPN", f_tott)
    ws_rek.write_formula(r + 1, 2, f"=ROUND(C{j}*$C$6/100,0)", f_tot, ppn_rp)
    ws_rek.merge_range(r + 2, 0, r + 2, 1, "JUMLAH TOTAL", f_tott)
    ws_rek.write_formula(r + 2, 2, f"=C{j}+C{j + 1}", f_tot, total)
    ws_rek.merge_range(r + 3, 0, r + 3, 1, "DIBULATKAN", f_tott)
    ws_rek.write_formula(r + 3, 2, f"=ROUND(C{j + 2},-3)", f_tot, bulat)
    ws_rek.merge_range(r + 5, 0, r + 5, 2, "Terbilang: " + terbilang(bulat).capitalize() + " rupiah", f_ital)
    ws_rek.write(r + 8, 1, "Magelang, ........................ 2026")
    ws_rek.write(r + 9, 1, "Disusun oleh,")
    ws_rek.write(r + 13, 1, "(........................................)")
    ws_rek.merge_range(r + 15, 0, r + 15, 2, "Catatan: harga satuan mengikuti HSP Kota Magelang (sudah termasuk overhead dan profit 10%). Total dalam sheet ini "
                       "berubah otomatis kalau volume, harga dasar, atau PPN diubah. Teks terbilang tidak ikut berubah.", f_ital)
    ws_rek.set_row(r + 15, 40)
    for c, w in enumerate([8, 58, 24]):
        ws_rek.set_column(c, c, w)
    ws_rek.set_paper(9)
    ws_rek.fit_to_pages(1, 1)

    # ---------------- Volume
    ws_vol.write("A1", "PERHITUNGAN VOLUME (dibaca dari DED)", f_b)
    for c, h in enumerate(["Item", "Nilai", "Satuan"]):
        ws_vol.write(2, c, h, f_head)
    for i, (n_, x, s_) in enumerate(rv):
        ws_vol.write(3 + i, 0, n_, f_t)
        ws_vol.write_number(3 + i, 1, round(x, 3), f_n2)
        ws_vol.write(3 + i, 2, s_, f_t)
    base = 5 + len(rv)
    ws_vol.write(base, 0, "ASUMSI PRA-DESAIN STRUKTUR", f_b)
    nama = {"a_pond_atas": "Pondasi lebar atas (m)", "a_pond_bawah": "Pondasi lebar bawah (m)", "a_pond_tinggi": "Pondasi tinggi (m)",
            "a_sloof_b": "Sloof lebar (m)", "a_sloof_h": "Sloof tinggi (m)", "a_kolom": "Kolom sisi (m)", "a_kolom_jarak": "Jarak kolom (m)",
            "a_balok_b": "Balok lebar (m)", "a_balok_h": "Balok tinggi (m)", "a_plat_t": "Tebal plat lantai (m)",
            "a_kg_kbs": "Besi sloof/kolom/balok (kg/m3)", "a_kg_slab": "Besi plat (kg/m3)", "a_miring": "Kemiringan atap (derajat)",
            "a_teritis": "Teritisan atap (m)", "a_pasir_t": "Tebal urugan pasir (m)", "a_km_keramik": "Tinggi keramik dinding KM (m)"}
    for i, (k, v_) in enumerate(asumsi.items()):
        ws_vol.write(base + 1 + i, 0, nama.get(k, k), f_t)
        ws_vol.write_number(base + 1 + i, 1, v_, f_n2)
    ws_vol.set_column(0, 0, 44)
    ws_vol.set_column(1, 2, 14)

    # ---------------- Bahan
    ws_bhn.write("A1", "KEBUTUHAN BAHAN (volume x koefisien AHSP)", f_b)
    for c, h in enumerate(["Bahan", "Jumlah", "Satuan"]):
        ws_bhn.write(2, c, h, f_head)
    for i, (n_, q, s_) in enumerate(bahan):
        ws_bhn.write(3 + i, 0, n_, f_t)
        ws_bhn.write_number(3 + i, 1, round(q, 2), f_n2)
        ws_bhn.write(3 + i, 2, s_, f_t)
    ws_bhn.set_column(0, 0, 32)
    ws_bhn.set_column(1, 2, 14)

    # ---------------- Batas_Bawah (pembanding, bukan bagian RAB resmi)
    ws_bwh.write("A1", "PEMBANDING: PERKIRAAN BATAS BAWAH (bukan bagian RAB)", f_b)
    ws_bwh.write("A2", "Dihitung dengan harga MINIMUM HSD untuk pekerjaan ber-AHSP. Pekerjaan lain memakai harga HSP yang sama. Perkiraan, bukan angka resmi.", f_ital)
    for c, h in enumerate(["Kode", "Uraian", "Volume", "Satuan", "Harga satuan bawah (Rp)", "Jumlah bawah (Rp)", "Jumlah HSP (Rp)"]):
        ws_bwh.write(3, c, h, f_head)
    for i, x in enumerate(rows):
        rr = 4 + i
        ws_bwh.write(rr, 0, x["kode"], f_t)
        ws_bwh.write(rr, 1, x["uraian"], f_t)
        ws_bwh.write_number(rr, 2, x["volume"], f_n2)
        ws_bwh.write(rr, 3, x["satuan"], f_tc)
        ws_bwh.write_number(rr, 4, round(x["jumlah_bawah"] / x["volume"]) if x["volume"] else 0, f_rp)
        ws_bwh.write_number(rr, 5, x["jumlah_bawah"], f_rp)
        ws_bwh.write_number(rr, 6, x["jumlah_atas"], f_rp)
    rr = 4 + len(rows)
    ws_bwh.merge_range(rr, 0, rr, 4, "Jumlah", f_tott)
    ws_bwh.write_formula(rr, 5, f"=SUM(F5:F{rr})", f_tot, bawah_total)
    ws_bwh.write_formula(rr, 6, f"=SUM(G5:G{rr})", f_tot, jumlah)
    for c, w in enumerate([13, 50, 11, 9, 20, 18, 18]):
        ws_bwh.set_column(c, c, w)

    # ---------------- Catatan
    ws_cat.write("A1", "DASAR PENYUSUNAN DAN CATATAN", f_b)
    cat = [
        "Sumber harga: MAS PETRUK, DPU Bina Marga dan Cipta Karya Provinsi Jawa Tengah. HSD dan HSP Edisi Ke-I Tahun 2026, Kota Magelang.",
        "Harga satuan pekerjaan = (tenaga kerja + bahan + peralatan) x koefisien AHSP, ditambah overhead dan profit 10%. Belum termasuk PPN.",
        "Harga dasar yang dipakai AHSP adalah kolom harga maksimum di HSD, sama dengan yang dipakai pada HSP di situs sumber.",
        "Koefisien bahan di situs ditampilkan dibulatkan, jadi pada beberapa bahan dipakai koefisien yang sesuai kolom jumlah harga di situs.",
        "Pekerjaan tanpa sheet AHSP memakai harga satuan langsung dari tabel HSP (kolom DASAR HARGA = HSP pada aplikasi).",
        "Volume dibaca dari denah DED yang dibuat aplikasi. Ukuran struktur (pondasi, sloof, kolom, balok, plat) memakai asumsi pra-desain, bukan hitungan struktur.",
        "Belum termasuk: pipa air bersih dan kotor, septic tank, pagar, talang, listrik di luar titik utama, dan biaya perencanaan, pengawasan, serta perizinan.",
        "Dokumen ini disusun dari data dan asumsi di atas dan perlu diverifikasi oleh perencana sebelum dipakai sebagai dokumen kontrak atau pengadaan.",
    ]
    for i, c in enumerate(cat):
        ws_cat.write(2 + i, 0, f"{i + 1}. {c}", F(text_wrap=True, valign="top"))
        ws_cat.set_row(2 + i, 32)
    ws_cat.set_column(0, 0, 120)
    wb.close()
    return bio.getvalue()


def page_rab():
    st.subheader("RAB dari DED")
    st.caption("Volume dibaca dari denah (DED). Harga satuan dihitung dari AHSP dan harga dasar upah dan bahan Kota Magelang "
               "(MAS PETRUK, Edisi I 2026). Susunan dokumen mengikuti RAB pada umumnya: rekapitulasi, rincian, dan analisa harga satuan.")
    c1, c2, c3, c4 = st.columns(4)
    c1.selectbox("Dinding", list(OPSI_DINDING), key="pil_dinding")
    c2.selectbox("Lantai", list(OPSI_LANTAI), key="pil_lantai")
    c3.selectbox("Penutup atap", list(OPSI_ATAP), key="pil_atap")
    c4.number_input("PPN (%)", min_value=0.0, max_value=25.0, step=0.5, key="ppn")
    with st.expander("Asumsi struktur pra-desain (boleh diubah)"):
        st.caption("Ukuran struktur ini asumsi untuk rumah sederhana, bukan hasil hitungan struktur. Konsultasikan ke perencana struktur.")
        e = st.columns(4)
        e[0].number_input("Pondasi lebar atas (m)", min_value=0.1, step=0.05, key="a_pond_atas")
        e[1].number_input("Pondasi lebar bawah (m)", min_value=0.2, step=0.05, key="a_pond_bawah")
        e[2].number_input("Pondasi tinggi (m)", min_value=0.3, step=0.05, key="a_pond_tinggi")
        e[3].number_input("Tebal plat lantai (m)", min_value=0.08, step=0.01, key="a_plat_t")
        f = st.columns(4)
        f[0].number_input("Sloof lebar (m)", min_value=0.1, step=0.01, key="a_sloof_b")
        f[1].number_input("Sloof tinggi (m)", min_value=0.1, step=0.01, key="a_sloof_h")
        f[2].number_input("Kolom sisi (m)", min_value=0.1, step=0.01, key="a_kolom")
        f[3].number_input("Jarak kolom (m)", min_value=2.0, step=0.5, key="a_kolom_jarak")
        g = st.columns(4)
        g[0].number_input("Balok lebar (m)", min_value=0.1, step=0.01, key="a_balok_b")
        g[1].number_input("Balok tinggi (m)", min_value=0.1, step=0.01, key="a_balok_h")
        g[2].number_input("Besi sloof/kolom/balok (kg/m³)", min_value=50.0, step=10.0, key="a_kg_kbs")
        g[3].number_input("Besi plat (kg/m³)", min_value=50.0, step=10.0, key="a_kg_slab")
        h = st.columns(4)
        h[0].number_input("Kemiringan atap (derajat)", min_value=10.0, max_value=55.0, step=1.0, key="a_miring")
        h[1].number_input("Teritisan atap (m)", min_value=0.0, step=0.1, key="a_teritis")
        h[2].number_input("Tebal urugan pasir (m)", min_value=0.0, step=0.01, key="a_pasir_t")
        h[3].number_input("Tinggi keramik dinding KM (m)", min_value=0.0, step=0.1, key="a_km_keramik")
    a = {k: float(SS[k]) for k in ASUMSI_DEF}
    rows, v = susun_rab(P, L, lantai, SS.pil_dinding, SS.pil_lantai, SS.pil_atap, a)
    jumlah = sum(r["jumlah_atas"] for r in rows)
    bawah = sum(r["jumlah_bawah"] for r in rows)
    ppn_rp = round(jumlah * SS.ppn / 100)
    total = jumlah + ppn_rp
    bulat = round(total, -3)
    m = st.columns(4)
    m[0].metric("Jumlah harga", rp(jumlah))
    m[1].metric(f"PPN {idn(SS.ppn)}%", rp(ppn_rp))
    m[2].metric("Jumlah total", rp(total))
    m[3].metric("Dibulatkan", rp(bulat))
    st.caption(f"Terbilang: {terbilang(bulat).capitalize()} rupiah. Biaya per m² luas lantai: {rp(jumlah / (P * L * lantai))} (sebelum PPN). "
               "Harga satuan sudah termasuk overhead dan profit 10%.")
    df = fmt_tabel(rows)
    st.markdown("**Rincian pekerjaan**")
    st.dataframe(df, hide_index=True)
    kel = pd.DataFrame([{"Kelompok": k, "Jumlah (juta Rp)": round(sum(r["jumlah_atas"] for r in rows if r["kelompok"] == k) / 1e6, 1)}
                        for k in KELOMPOK]).set_index("Kelompok")
    st.markdown("**Komposisi biaya per kelompok (dari RAB)**")
    st.bar_chart(kel)

    tot, tanpa = daftar_bahan(rows)
    gabung = dict(tot)
    if ("Semen", "kg") in gabung:
        gabung[("Semen (zak 50 kg)", "zak")] = gabung[("Semen", "kg")] / 50
    rv = [("Panjang dinding lantai 1", v["per"][0]["panjang"], "m"), ("Luas dinding bersih (semua lantai)", v["dinding"], "m²"),
          ("Luas plester dan acian (dua sisi)", v["plester"], "m²"), ("Cat interior", v["dalam"], "m²"), ("Cat eksterior", v["luar"], "m²"),
          ("Luas lantai keramik", v["lantai"], "m²"), ("Luas plafon", v["plafon"], "m²"), ("Luas atap", v["luas_atap"], "m²"),
          ("Daun pintu", v["daun_pintu"], "m²"), ("Jendela dan kaca", v["kaca"], "m²"), ("Kusen pintu", v["kusen"], "m'"),
          ("Volume pondasi batu belah", v["pond_vol"], "m³"), ("Volume beton struktur (termasuk tangga)", v["beton"], "m³"), ("Jumlah kolom", v["n_kolom"], "buah"),
          ("Lisplank", v["lisplank"], "m'"), ("Plint keramik", v["plint"], "m'"), ("Waterproofing (KM + balkon)", v["waterproof"], "m²"),
          ("Keramik dinding KM", v["km_dinding"], "m²"), ("Railing balkon", v["railing_balkon"], "m'"), ("Railing tangga", v["tangga_railing"], "m'")]
    bahan_list = [(n, q, s) for (n, s), q in sorted(gabung.items())]
    meta = dict(pekerjaan=f"Pembangunan rumah tinggal {lantai} lantai ({idn(P)} x {idn(L)} m)", lokasi="Kota Magelang", tahun="2026",
                sumber="HSP dan HSD Edisi I 2026, MAS PETRUK (DPU Bina Marga dan Cipta Karya Provinsi Jawa Tengah)")
    b1, b2 = st.columns(2)
    try:
        xls = buat_rab_resmi(rows, float(SS.ppn), meta, rv, bahan_list, a, bawah)
    except ImportError:
        xls = None
    if xls:
        b1.download_button("⬇ Unduh RAB format resmi (Excel)", xls, file_name="RAB_rumah_kota_magelang.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        b1.warning("Tombol Excel belum aktif: tambahkan baris xlsxwriter ke requirements.txt lalu reboot aplikasi.")
    b2.download_button("⬇ Unduh rincian (CSV)", df.to_csv(index=False).encode("utf-8-sig"), file_name="rab_rumah_hitung.csv", mime="text/csv")
    st.caption("File Excel berisi sheet REKAPITULASI, RAB, AHSP, Harga_Dasar, Volume, Bahan, Batas_Bawah, dan Catatan. "
               "Harga di RAB mengambil dari AHSP, dan AHSP mengambil dari Harga_Dasar, jadi mengubah harga dasar mengubah seluruh RAB.")
    with st.expander("Kebutuhan bahan (dari koefisien AHSP)"):
        tb = pd.DataFrame([{"Bahan": n, "Jumlah": idn(q, 1), "Satuan": s} for (n, s), q in sorted(gabung.items())])
        st.dataframe(tb, hide_index=True)
        st.caption("Dihitung dari volume DED × koefisien AHSP resmi. Belum termasuk kayu bekisting dan bahan pekerjaan yang AHSP-nya belum dikumpulkan.")
        if tanpa:
            st.caption("Bahan untuk pilihan ini belum dihitung (AHSP belum ada): " + ", ".join(tanpa) + ".")
    with st.expander("Rekap volume yang dibaca dari DED"):
        st.dataframe(pd.DataFrame([{"Item": n, "Nilai": idn(x, 2), "Satuan": s} for n, x, s in rv]), hide_index=True)
    with st.expander("Pembanding: perkiraan batas bawah"):
        st.metric("Jumlah dengan harga minimum HSD (sebelum PPN)", rp(bawah))
        st.caption("Perkiraan dari harga minimum HSD untuk pekerjaan yang punya AHSP. Bukan bagian RAB dan bukan angka resmi.")
    st.warning("Belum termasuk: pipa air bersih dan kotor, septic tank, listrik di luar titik utama, pagar, talang, dan pekerjaan lain di luar daftar. "
               "Volume struktur memakai asumsi pra-desain, jadi perlu diverifikasi perencana sebelum dipakai sebagai dokumen kontrak.")


def page_data():
    st.subheader("Data harga resmi (Kota Magelang)")
    st.markdown("Sumber: **MAS PETRUK**, DPU Bina Marga dan Cipta Karya Provinsi Jawa Tengah. HSD dan HSP tertulis Edisi Ke-I Tahun 2026. "
                "Data disalin manual dari situs pada 9-10 November 2026. Cek ulang ke situs sebelum dipakai untuk keperluan resmi.")
    st.markdown("**Harga satuan pekerjaan yang dipakai di RAB**")
    tabel = pd.DataFrame([{"Kode": k[0], "Pekerjaan": k[1], "Satuan": k[2], "Harga HSP / batas atas (Rp)": num(k[3]),
                           "Perkiraan batas bawah (Rp)": num(k[4]) if k[4] else "-", "Dasar": k[5]} for k in KAT.values()])
    st.dataframe(tabel, hide_index=True)
    st.markdown("**Upah (per orang-hari, Rp)**")
    st.dataframe(pd.DataFrame([{"Tenaga": n, "Minimum": num(a), "Maksimum": num(b)} for n, a, b in UPAH]), hide_index=True)
    st.markdown("**SHST rumah negara per m² (Rp)**")
    st.dataframe(pd.DataFrame([{"Tipe": TIPE_RN[t], "Kualitas di aplikasi": t.capitalize(), "SHST MAS PETRUK (Rp/m²)": num(HARGA["mas"][t])}
                               for t in ("hemat", "standar", "premium")]), hide_index=True)
    with st.expander("Cara menyambungkan harga ke Google Sheet"):
        st.markdown("""
Pakai file **data_rab_kota_magelang.xlsx** (workbook data yang sudah lengkap) sebagai sumbernya.

1. Di Google Sheets pilih *File → Import → Upload*, pilih file itu, lalu **Insert new sheet(s)**.
2. **Harga dasar (upah dan bahan):** pada sheet `Harga_Dasar`, ubah kolom `harga_min` dan `harga_maks`. Pilih *File → Share → Publish to web*, pilih sheet `Harga_Dasar`, format **CSV**, lalu salin linknya.
3. **Tabel HSP lengkap (opsional):** tempel 432 + 188 baris HSP ke sheet `HSP_Mentah` (kolom kode dan harga_satuan). Publish sheet itu sebagai CSV juga. Dipakai untuk pekerjaan yang tidak punya AHSP.
4. Tempel link di `app.py` pada `HARGA_DASAR_CSV_URL = ""` dan `HSP_CSV_URL = ""`, atau di Streamlit Cloud: *Settings → Secrets*, isi `HARGA_DASAR_CSV_URL = "..."` dan `HSP_CSV_URL = "..."`.
5. Aplikasi membaca sheet tiap sekitar 10 menit. Mengubah harga dasar menghitung ulang 21 AHSP, lalu seluruh RAB. Kalau sheet gagal dibaca, aplikasi memakai harga bawaan.

Catatan: siapa pun yang punya link CSV bisa membacanya, jadi jangan menaruh data pribadi.
""")
    st.info("Semua harga satuan di AHSP sama dengan kolom maksimum di HSD, jadi harga HSP adalah batas atas. Batas bawah adalah perkiraan "
            "dari harga minimum HSD, bukan angka resmi. Edisi SHST MAS PETRUK belum dikonfirmasi, cek di halamannya sebelum dikutip.")


def page_panduan():
    st.subheader("Panduan singkat")
    st.markdown("""
1. **Atur ukuran rumah** di sidebar (panjang, lebar, jumlah lantai). Ukuran ini dipakai di semua menu.
2. **Estimasi Cepat:** pilih kualitas, isi anggaran, lalu lihat apakah anggaran cukup.
3. **Lahan & DED:** isi data lahan dan aturan bangunan (KDB, KLB, sempadan dari KRK atau RDTR). Denah tergambar otomatis dengan animasi, dan bisa diputar ulang.
4. **RAB dari DED:** pilih jenis dinding, lantai, dan atap. Volume dibaca dari denah, dikali harga satuan dari AHSP. Unduh hasilnya sebagai Excel format RAB (rekapitulasi, rincian, AHSP).
5. **Data Harga:** lihat sumber, harga satuan, dan upah yang dipakai, serta cara menyambungkan harga ke Google Sheet.
""")
    st.markdown("**Batasan**")
    st.markdown("""
- Hanya Kota Magelang dan rumah maksimal 2 lantai.
- Volume struktur memakai asumsi pra-desain, jadi RAB perlu diverifikasi perencana sebelum jadi dokumen kontrak. Biaya perencanaan, pengawasan, dan perizinan belum termasuk.
- Denah adalah ilustrasi pembagian ruang, bukan gambar kerja. Ukuran struktur adalah asumsi pra-desain.
- KDB, KLB, dan sempadan di aplikasi hanya contoh. Cek ke KRK atau RDTR lokasi.
""")


UPAH = [("Pekerja", 75000, 126000), ("Tukang (umum)", 100000, 179783), ("Tukang batu/tembok", 105000, 160000),
        ("Tukang kayu", 105000, 179783), ("Tukang besi", 105000, 179783), ("Tukang cat", 105000, 179783),
        ("Kepala tukang", 120000, 170000), ("Mandor", 110000, 239711)]

HALAMAN = {MENU[0]: page_beranda, MENU[1]: page_estimasi, MENU[2]: page_ded, MENU[3]: page_rab, MENU[4]: page_data, MENU[5]: page_panduan}
HALAMAN[menu]()
st.caption("Rumah Hitung · Kota Magelang · harga: MAS PETRUK (DPU BMCK Prov. Jateng) Edisi I 2026 · estimasi awal, bukan RAB resmi")
