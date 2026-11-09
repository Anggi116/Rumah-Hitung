# =====================================================================
#  Rumah Hitung - Kalkulator Material & Biaya Rumah (Streamlit)
#  Dijalankan dengan:  streamlit run app.py
# =====================================================================

# =====================================================================
# 1. DATA HARGA RESMI DAN FUNGSI PERHITUNGAN
# =====================================================================
import math

# Standar Harga Satuan Tertinggi (SHST) Rumah Negara, dalam Rp per m2
HARGA = {
    "Kota Magelang": {"Hemat": 4_960_000, "Standar": 6_330_000, "Premium": 7_060_000},
    "Kab. Magelang": {"Hemat": 4_810_000, "Standar": 5_750_000, "Premium": 6_250_000},
}
SUMBER = {
    "Kota Magelang": "Perwal Kota Magelang No. 13/2025",
    "Kab. Magelang": "Perbup Kab. Magelang No. 11/2026",
}
TIPE_RN = {
    "Hemat": "Rumah Negara Tipe C (C/D/E)",
    "Standar": "Rumah Negara Tipe B",
    "Premium": "Rumah Negara Tipe A",
}
# Perkiraan komposisi biaya (bukan data resmi SHST)
BAGIAN = [
    ("Pondasi & struktur", 0.30), ("Dinding & plesteran", 0.18), ("Atap & plafon", 0.17),
    ("Lantai & finishing", 0.20), ("Pintu, jendela & kusen", 0.07), ("Listrik & air", 0.08),
]
WARNA = ["#B85B6C", "#E08E9B", "#F2B5BE", "#8F3847", "#F7D0D6", "#D98A97"]


def r0(n):
    """Pembulatan biasa (0,5 ke atas)."""
    return int(math.floor(n + 0.5))


def rp(n):
    return "Rp " + f"{r0(n):,}".replace(",", ".")


def fm(n):
    """Angka 1 desimal gaya Indonesia, contoh 1.234,5"""
    s = f"{n:,.1f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def ringkas(n):
    if n >= 1e9:
        return f"{n / 1e9:.2f}".replace(".", ",") + " miliar"
    if n >= 1e6:
        return f"{r0(n / 1e6):,}".replace(",", ".") + " juta"
    return rp(n)


def harga_efektif(wilayah, tipe, lantai):
    """Harga per m2 resmi. Rumah tipe C/D/E di atas 2 lantai = klasifikasi tidak sederhana."""
    t, naik = tipe, False
    if tipe == "Hemat" and lantai > 2:
        t, naik = "Standar", True          # pendekatan: dinaikkan ke harga Tipe B
    klas = "Sederhana" if (tipe == "Hemat" and lantai <= 2) else "Tidak Sederhana"
    return HARGA[wilayah][t], klas, naik, TIPE_RN[t]


TINGGI_DINDING = 3.0     # m
TINGGI_PINTU = 2.1      # m
TINGGI_JENDELA = 1.2    # m


def panjang_dinding(P, L, f, lantai):
    """Total panjang dinding 1 lantai (m), dihitung dari tepi ruangan pada denah.
    Tepi yang dipakai bersama dua ruangan dihitung sekali. Balkon (terbuka) tidak punya dinding."""
    R, _, _, _ = layout(P, L, f, lantai)
    horiz, vert = {}, {}
    for r in R:
        if r.get("open"):
            continue
        x0, y0, x1, y1 = r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]
        for y in (y0, y1):
            horiz.setdefault(round(y, 6), []).append((x0, x1))
        for x in (x0, x1):
            vert.setdefault(round(x, 6), []).append((y0, y1))

    def gabung(garis):
        total = 0.0
        for ruas in garis.values():
            ruas.sort()
            awal, akhir = ruas[0]
            for a, b in ruas[1:]:
                if a > akhir + 1e-9:
                    total += akhir - awal
                    awal, akhir = a, b
                else:
                    akhir = max(akhir, b)
            total += akhir - awal
        return total

    return gabung(horiz) + gabung(vert)


def luas_dinding_bersih(P, L, lantai):
    """Luas dinding (m2) = panjang dinding x tinggi 3 m, dikurangi pintu (2,1 m) dan jendela (1,2 m)."""
    total = 0.0
    for f in range(1, lantai + 1):
        denah = 1 if f == 1 else 2                    # lantai 2 dan 3 memakai denah yang sama
        _, pintu, jendela, _ = layout(P, L, denah, lantai)
        bukaan = sum(d["w"] * TINGGI_PINTU for d in pintu) + sum(w["l"] * TINGGI_JENDELA for w in jendela)
        total += panjang_dinding(P, L, denah, lantai) * TINGGI_DINDING - bukaan
    return total


def hitung_material(P, L, lantai):
    """Perkiraan kasar: dinding dihitung dari denah, bata 1/2 batu."""
    luas = P * L * lantai
    dinding = luas_dinding_bersih(P, L, lantai)       # m2 dinding bersih
    return {
        "dinding": dinding,
        "bata": dinding * 70,                         # buah
        "semen": dinding * 0.58 + luas * 1.1,         # sak 40 kg
        "besi": luas * 30,                            # kg
    }


def data_lahan(TW, TP, KDB, KLB, GD, GS):
    return {
        "TW": TW, "TP": TP, "kdb": KDB / 100, "klb": KLB, "gd": GD, "gs": GS,
        "tanah": TW * TP,
        "bw": max(0, TW - 2 * GS),        # lebar area bangun
        "bd": max(0, TP - GD - GS),       # panjang area bangun
    }


def cek_lahan(P, L, lantai, d):
    dasar = P * L
    total = dasar * lantai
    kdb_max = d["tanah"] * d["kdb"]
    klb_max = d["tanah"] * d["klb"]
    muat = P <= d["bw"] + 1e-9 and L <= d["bd"] + 1e-9
    maks_lantai = int(math.floor(d["klb"] / d["kdb"] + 1e-9)) if d["kdb"] > 0 else 0
    cek = [
        (dasar <= kdb_max,
         f"Luas dasar {fm(dasar)} m² {'masih di bawah' if dasar <= kdb_max else 'melebihi'} "
         f"batas KDB {fm(kdb_max)} m² ({fm(d['kdb'] * 100)}% × {fm(d['tanah'])} m²)"),
        (total <= klb_max,
         f"Total luas lantai {fm(total)} m² {'masih di bawah' if total <= klb_max else 'melebihi'} "
         f"batas KLB {fm(klb_max)} m² ({d['klb']} × {fm(d['tanah'])} m²)"),
        (muat,
         f"Rumah {P:g} × {L:g} m {'muat' if muat else 'tidak muat'} di area bangun "
         f"{fm(d['bw'])} × {fm(d['bd'])} m (setelah sempadan)"),
    ]
    info = (f"Jika KDB dipakai penuh, KLB {d['klb']} mengizinkan sekitar {maks_lantai} lantai. "
            f"Luas dasar terbesar yang mungkin: {fm(min(kdb_max, d['bw'] * d['bd']))} m².")
    return {"cek": cek, "info": info, "ok": all(c[0] for c in cek), "klb_max": klb_max}


def ukuran_maksimal(P, L, lantai, d):
    """Ukuran rumah terbesar (rasio P:L tetap) yang lolos KDB, KLB, dan sempadan."""
    batas = [d["tanah"] * d["kdb"], d["bw"] * d["bd"]]
    if d["klb"] > 0:
        batas.append(d["tanah"] * d["klb"] / lantai)
    k = math.sqrt(max(min(batas), 0) / (P * L))
    k = min(k, d["bw"] / P, d["bd"] / L)
    nP, nL = math.floor(P * k * 2) / 2, math.floor(L * k * 2) / 2
    return (nP, nL) if nP >= 1 and nL >= 1 else (P, L)


# =====================================================================
# 2. GAMBAR DENAH (DED SEDERHANA) DAN SITEPLAN DALAM FORMAT SVG
# =====================================================================
INK, SOFT, PK, PKD, MUT = "#1E293B", "#FDF2F4", "#E08E9B", "#B85B6C", "#475569"


def _t(x, y, txt, size=9, fill=MUT, weight=700, anchor="middle", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{txt}</text>')


def _ln(x1, y1, x2, y2, c, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{c}" stroke-width="{w}"{d}/>')


def layout(P, L, f, lantai):
    """Pembagian ruang dalam meter. f = lantai yang digambar."""
    x1 = P * 0.5
    R, D, Wn, ST = [], [], [], []
    if f == 1:
        yA, y1, y2 = L * .45, L * .38, L * .62
        R = [dict(n="Ruang Keluarga", x=0, y=0, w=x1, h=yA), dict(n="Ruang Tamu", x=0, y=yA, w=x1, h=L - yA),
             dict(n="Dapur", x=x1, y=0, w=P - x1, h=y1), dict(n="KM", x=x1, y=y1, w=P - x1, h=y2 - y1),
             dict(n="Kamar Tidur", x=x1, y=y2, w=P - x1, h=L - y2)]
        D = [dict(o="h", x=x1 * .3, y=L, s=-1, w=1), dict(o="v", x=x1, y=(y2 + L) / 2, s=1, w=.9),
             dict(o="v", x=x1, y=y1 / 2, s=1, w=.9), dict(o="v", x=x1, y=(y1 + y2) / 2, s=1, w=.8)]
        Wn = [dict(o="v", x=0, y=yA / 2, l=1.4), dict(o="v", x=0, y=(yA + L) / 2, l=1.4),
              dict(o="h", x=x1 * .75, y=L, l=1.2), dict(o="h", x=x1 + (P - x1) / 2, y=0, l=1),
              dict(o="v", x=P, y=(y1 + y2) / 2, l=.5), dict(o="v", x=P, y=(y2 + L) / 2, l=1.2),
              dict(o="h", x=x1 + (P - x1) / 2, y=L, l=1.2)]
    else:
        yS, y1, y2 = L * .45, L * .4, L * .6
        R = [dict(n="Ruang Santai", x=0, y=0, w=x1, h=yS), dict(n="Kamar Utama", x=0, y=yS, w=x1, h=L - yS),
             dict(n="Kamar 2", x=x1, y=0, w=P - x1, h=y1), dict(n="KM", x=x1, y=y1, w=P - x1, h=y2 - y1),
             dict(n="Balkon", x=x1, y=y2, w=P - x1, h=L - y2, open=True)]
        D = [dict(o="h", x=x1 * .7, y=yS, s=1, w=.9), dict(o="v", x=x1, y=y1 / 2, s=1, w=.9),
             dict(o="v", x=x1, y=(y1 + y2) / 2, s=1, w=.8), dict(o="v", x=x1, y=(y2 + L) / 2, s=1, w=1.2, sl=True)]
        Wn = [dict(o="v", x=0, y=yS / 2, l=1.4), dict(o="v", x=0, y=(yS + L) / 2, l=1.4),
              dict(o="h", x=x1 / 2, y=L, l=1.4), dict(o="h", x=x1 + (P - x1) / 2, y=0, l=1),
              dict(o="v", x=P, y=y1 / 2, l=1), dict(o="v", x=P, y=(y1 + y2) / 2, l=.5)]
    if lantai > 1:
        ST.append(dict(x=.2, y=.2, w=1, h=max(1, min(2.6, L * .45 - .4))))
    return R, D, Wn, ST


def svg_denah(P, L, f, lantai):
    W, H, mx, my = 360, 282, 34, 40
    s = min((W - mx * 2) / P, (H - my - 42) / L)
    ox, oy = (W - P * s) / 2, my
    X, Y = (lambda v: ox + v * s), (lambda v: oy + v * s)
    R, D, Wn, ST = layout(P, L, f, lantai)
    o = [_t(10, 16, f"DENAH LANTAI {f}", 11, PKD, 800, "start"),
         _t(10, 28, "ukuran dalam meter", 9, MUT, 700, "start"),
         f'<g transform="translate({W - 24},24)"><circle r="11" fill="none" stroke="{INK}"/>'
         f'<path d="M0,-8 L4,5 L0,2 L-4,5 Z" fill="{INK}"/>{_t(0, -14, "U")}</g>']
    for r in R:                                                   # ruangan + dinding
        if r.get("open"):
            o.append(f'<rect x="{X(r["x"]):.1f}" y="{Y(r["y"]):.1f}" width="{r["w"] * s:.1f}" height="{r["h"] * s:.1f}" '
                     f'fill="none" stroke="{PKD}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        else:
            o.append(f'<rect x="{X(r["x"]):.1f}" y="{Y(r["y"]):.1f}" width="{r["w"] * s:.1f}" height="{r["h"] * s:.1f}" '
                     f'fill="{SOFT}" stroke="{INK}" stroke-width="2.5"/>')
    for t in ST:                                                  # tangga
        o.append(f'<rect x="{X(t["x"]):.1f}" y="{Y(t["y"]):.1f}" width="{t["w"] * s:.1f}" height="{t["h"] * s:.1f}" '
                 f'fill="none" stroke="{MUT}"/>')
        k = 0.3
        while k < t["h"]:
            o.append(_ln(X(t["x"]), Y(t["y"] + k), X(t["x"] + t["w"]), Y(t["y"] + k), MUT, 1))
            k += 0.3
    for w in Wn:                                                  # jendela
        l, x, y = w["l"] * s, X(w["x"]), Y(w["y"])
        if w["o"] == "h":
            o.append(f'<rect x="{x - l / 2:.1f}" y="{y - 2.5:.1f}" width="{l:.1f}" height="5" fill="{SOFT}"/>')
            o += [_ln(x - l / 2, y + dy, x + l / 2, y + dy, PKD, 1) for dy in (-1.5, 1.5)]
        else:
            o.append(f'<rect x="{x - 2.5:.1f}" y="{y - l / 2:.1f}" width="5" height="{l:.1f}" fill="{SOFT}"/>')
            o += [_ln(x + dx, y - l / 2, x + dx, y + l / 2, PKD, 1) for dx in (-1.5, 1.5)]
    for d in D:                                                   # pintu + ayunan
        r, sg = d["w"] * s, d["s"]
        if d["o"] == "h":
            hx, hy = X(d["x"] - d["w"] / 2), Y(d["y"])
            o.append(f'<rect x="{hx:.1f}" y="{hy - 2.5:.1f}" width="{r:.1f}" height="5" fill="{SOFT}"/>')
            if d.get("sl"):
                o += [_ln(hx, hy + dy, hx + r, hy + dy, PKD, 1) for dy in (-1, 1)]
            else:
                o.append(_ln(hx, hy, hx, hy + sg * r, PKD, 1.6))
                o.append(f'<path d="M{hx + r:.1f},{hy:.1f} A{r:.1f},{r:.1f} 0 0 {1 if sg == 1 else 0} {hx:.1f},{hy + sg * r:.1f}" '
                         f'fill="none" stroke="{PKD}" stroke-width="1.2"/>')
        else:
            hx, hy = X(d["x"]), Y(d["y"] - d["w"] / 2)
            o.append(f'<rect x="{hx - 2.5:.1f}" y="{hy:.1f}" width="5" height="{r:.1f}" fill="{SOFT}"/>')
            if d.get("sl"):
                o += [_ln(hx + dx, hy, hx + dx, hy + r, PKD, 1) for dx in (-1, 1)]
            else:
                o.append(_ln(hx, hy, hx + sg * r, hy, PKD, 1.6))
                o.append(f'<path d="M{hx:.1f},{hy + r:.1f} A{r:.1f},{r:.1f} 0 0 {0 if sg == 1 else 1} {hx + sg * r:.1f},{hy:.1f}" '
                         f'fill="none" stroke="{PKD}" stroke-width="1.2"/>')
    for r in R:                                                   # nama ruang + luas
        pw, ph = r["w"] * s, r["h"] * s
        if pw < 42 or ph < 20:
            continue
        cx, cy = X(r["x"]) + pw / 2, Y(r["y"]) + ph / 2
        o.append(_t(cx, cy + (-1 if ph > 30 else 3), r["n"], 9.5, INK, 800))
        if ph > 30 and not r.get("open"):
            o.append(_t(cx, cy + 10, f'{fm(r["w"] * r["h"])} m²', 8))
    by, x1 = Y(L), X(P * 0.5)                                     # garis dimensi
    o.append(f'<path d="M{X(0):.1f},{by + 20:.1f} H{X(P):.1f} M{X(0):.1f},{by + 16:.1f} v8 M{x1:.1f},{by + 16:.1f} v8 '
             f'M{X(P):.1f},{by + 16:.1f} v8" fill="none" stroke="{MUT}"/>')
    o.append(_t((X(0) + x1) / 2, by + 17, fm(P * 0.5), 10, PKD, 800))
    o.append(_t((x1 + X(P)) / 2, by + 17, fm(P * 0.5), 10, PKD, 800))
    o.append(f'<path d="M{X(0):.1f},{by + 36:.1f} H{X(P):.1f} M{X(0):.1f},{by + 32:.1f} v8 M{X(P):.1f},{by + 32:.1f} v8" '
             f'fill="none" stroke="{MUT}"/>')
    o.append(_t((X(0) + X(P)) / 2, by + 33, f"{P:g} m", 10, PKD, 800))
    o.append(f'<path d="M{X(0) - 14:.1f},{Y(0):.1f} V{by:.1f} M{X(0) - 18:.1f},{Y(0):.1f} h8 M{X(0) - 18:.1f},{by:.1f} h8" '
             f'fill="none" stroke="{MUT}"/>')
    o.append(_t(0, 0, f"{L:g} m", 10, PKD, 800,
                extra=f'transform="translate({X(0) - 18:.1f},{(Y(0) + by) / 2:.1f}) rotate(-90)"'))
    return f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(o)}</svg>'


def svg_site(P, L, d, ok):
    """Siteplan: lahan, area boleh dibangun (garis putus-putus), dan rumah."""
    if d["TW"] <= 0 or d["TP"] <= 0:
        return ""
    W, H, oy = 360, 200, 16
    s = min((W - 40) / d["TW"], (H - oy - 24) / d["TP"])
    ox = (W - d["TW"] * s) / 2
    bx, by = ox + d["gs"] * s, oy + d["gs"] * s
    hx, hy = bx + (d["bw"] - P) / 2 * s, oy + (d["TP"] - d["gd"] - L) * s
    warna = ("#FDF2F4", PKD) if ok else ("#FBD5DB", "#C0394F")
    o = [_t(ox, 11, f'Lahan {fm(d["TW"])} × {fm(d["TP"])} m = {fm(d["tanah"])} m²', 11, PKD, 800, "start"),
         f'<rect x="{ox:.1f}" y="{oy}" width="{d["TW"] * s:.1f}" height="{d["TP"] * s:.1f}" fill="#fff" stroke="{INK}" stroke-width="2"/>',
         f'<rect x="{bx:.1f}" y="{by:.1f}" width="{d["bw"] * s:.1f}" height="{d["bd"] * s:.1f}" fill="none" '
         f'stroke="{PK}" stroke-width="1.5" stroke-dasharray="5 4"/>',
         f'<rect x="{hx:.1f}" y="{hy:.1f}" width="{P * s:.1f}" height="{L * s:.1f}" fill="{warna[0]}" stroke="{warna[1]}" stroke-width="2"/>']
    if P * s > 70:
        o.append(_t(hx + P * s / 2, hy + L * s / 2 + 3, f"Rumah {P:g}×{L:g}", 9.5, INK, 800))
    o.append(f'<rect x="{ox:.1f}" y="{oy + d["TP"] * s + 4:.1f}" width="{d["TW"] * s:.1f}" height="8" fill="{MUT}" opacity=".25"/>')
    o.append(_t(W / 2, oy + d["TP"] * s + 22, "jalan (sisi depan)", 9))
    return f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(o)}</svg>'


# =====================================================================
# 3. KARTU HASIL (TAMPILAN HTML)
# =====================================================================
CARD = ("background:#fff;color:#1E293B;border:1px solid #F8E1E5;border-radius:18px;padding:16px;"
        "box-shadow:0 2px 12px rgba(184,91,108,.08);margin-bottom:12px;")


def kartu(judul, isi):
    return (f'<div style="{CARD}"><div style="font-weight:800;color:#B85B6C;font-size:15px;'
            f'margin-bottom:10px">{judul}</div>{isi}</div>')


def html_header():
    return ('<style>.gradio-container{background:#F8FAFC !important}</style>'
            '<div style="background:#1E293B;border-bottom:4px solid #E08E9B;border-radius:16px;padding:14px 18px;'
            'display:flex;gap:12px;align-items:center;margin-bottom:8px">'
            '<div style="width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#E08E9B,#B85B6C);'
            'display:grid;place-items:center;font-size:24px">🏠</div>'
            '<div><div style="color:#fff;font-weight:800;font-size:22px;letter-spacing:.04em">Rumah Hitung</div>'
            '<div style="color:#F8E1E5;font-size:13px">Kalkulator material &amp; biaya rumah untuk calon pemilik</div></div></div>')


def _kotak(isi, bg, warna="#1E293B"):
    return (f'<div style="background:{bg};color:{warna};border-radius:12px;padding:9px 11px;margin-top:6px;'
            f'font-size:13px;font-weight:700">{isi}</div>')


def html_hero(total, luas, h, anggaran, tipe, wilayah, e, manual):
    if not anggaran:
        status = "Isi anggaran untuk melihat apakah cukup atau tidak."
    elif total <= anggaran:
        status = f"✅ Anggaran cukup. Sisa {rp(anggaran - total)} ({r0((anggaran - total) / anggaran * 100)}%)."
    else:
        status = (f"⚠️ Kurang {rp(total - anggaran)}. Dengan anggaran ini, luas maksimal sekitar "
                  f"{int(anggaran // h)} m² (tipe {tipe}).")
    klas = "Klasifikasi: " + e[1]
    if e[2]:
        klas += " (rumah tipe C/D/E di atas 2 lantai masuk klasifikasi tidak sederhana, harga dinaikkan ke Tipe B sebagai pendekatan)"
    elif manual:
        klas += " (harga diubah manual)"
    return (f'<div style="background:#0F172A;color:#fff;border:1px solid #1E293B;border-radius:18px;padding:18px;margin-bottom:12px">'
            f'<div style="color:#E08E9B;font-weight:700;font-size:13px">Estimasi total biaya bangun</div>'
            f'<div style="color:#34d399;font-weight:600;font-size:30px;margin:4px 0;font-family:ui-monospace,monospace">{rp(total)}</div>'
            f'<div style="color:#94a3b8;font-size:13px;font-weight:700">≈ {ringkas(total)} · {fm(luas)} m² × {rp(h)}/m²</div>'
            f'<div style="color:#94a3b8;font-size:12px;margin-top:4px">Acuan {SUMBER[wilayah]}: {e[3]}. {klas}</div>'
            f'<div style="margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(224,142,155,.15);'
            f'border:1px solid rgba(224,142,155,.35);font-size:14px;font-weight:700">{status}</div></div>')


def html_banding(P, L, lantai, tipe, wilayah, anggaran, d):
    tipes = ["Hemat", "Standar", "Premium"]
    th = "color:#475569;font-weight:800;padding:4px;font-size:12px"
    rows = f'<tr><th></th>{"".join(f"<th style=\"{th}\">{t}</th>" for t in tipes)}</tr>'
    for lt in (1, 2, 3):
        rows += f'<tr><th style="{th};text-align:left;white-space:nowrap">{lt} lantai</th>'
        for t in tipes:
            luas = P * L * lt
            tot = luas * harga_efektif(wilayah, t, lt)[0]
            bg, fg = "#FDF2F4", "#1E293B"
            if anggaran:
                bg, fg = ("#DDF3EA", "#2e8b6a") if tot <= anggaran else ("#FBE0E4", "#C0394F")
            sel = "outline:2px solid #B85B6C;" if (t == tipe and lt == lantai) else ""
            warn = " ⚠" if (d["tanah"] > 0 and luas > d["tanah"] * d["klb"]) else ""
            rows += (f'<td style="background:{bg};color:{fg};{sel}border-radius:10px;padding:9px 4px;text-align:center;'
                     f'font-weight:800;font-size:13px">{ringkas(tot)}{warn}'
                     f'<div style="font-size:11px;font-weight:700;opacity:.8">{fm(luas)} m²</div></td>')
        rows += "</tr>"
    isi = (f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:separate;border-spacing:4px">{rows}</table></div>'
           '<div style="font-size:12px;color:#475569;margin-top:6px">Harga memakai SHST resmi wilayah terpilih. '
           'Hijau = masuk anggaran, merah = melebihi anggaran, ⚠ = melebihi batas KLB lahan. Kotak bergaris = pilihanmu saat ini.</div>')
    return kartu("Bandingkan skenario", isi)


def html_lahan(P, L, lantai, d):
    c = cek_lahan(P, L, lantai, d)
    isi = svg_site(P, L, d, c["ok"])
    for ok, teks in c["cek"]:
        isi += _kotak(("✅ " if ok else "⚠️ ") + teks, "#FDF2F4" if ok else "#FBE0E4", "#1E293B" if ok else "#C0394F")
    isi += _kotak("ℹ️ " + c["info"], "#FDF2F4")
    return kartu("Cek kelayakan lahan (KDB / KLB / sempadan)", isi)


def html_denah(P, L, lantai, lihat):
    isi = svg_denah(P, L, lihat, lantai)
    isi += ('<div style="font-size:12px;color:#475569;margin-top:6px">Denah ini ilustrasi pembagian ruang dari ukuran yang kamu isi, '
            'bukan gambar kerja. Rumah 3 lantai butuh pondasi lebih kuat, jadi naikkan harga per m² bila perlu.</div>')
    return kartu("Denah rumah (gaya gambar DED)", isi)


def html_komposisi(total):
    r, acc, seg = 15.9155, 0.0, []
    for (n, p), w in zip(BAGIAN, WARNA):
        seg.append(f'<circle cx="21" cy="21" r="{r}" fill="none" stroke="{w}" stroke-width="6" '
                   f'stroke-dasharray="{p * 100:.2f} {100 - p * 100:.2f}" stroke-dashoffset="{25 - acc * 100:.2f}"/>')
        acc += p
    donat = (f'<svg viewBox="0 0 42 42" width="150" height="150">{"".join(seg)}'
             f'<text x="21" y="22.5" font-size="4" font-weight="800" fill="#1E293B" text-anchor="middle">biaya</text></svg>')
    legenda = "".join(
        f'<div style="display:flex;gap:8px;align-items:center;font-size:13px;margin:5px 0">'
        f'<span style="width:12px;height:12px;border-radius:4px;background:{w};flex:none"></span>'
        f'<span style="flex:1;font-weight:700">{n}</span><b>{r0(p * 100)}% · {ringkas(total * p)}</b></div>'
        for (n, p), w in zip(BAGIAN, WARNA))
    isi = (f'<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><div>{donat}</div>'
           f'<div style="flex:1;min-width:220px">{legenda}</div></div>'
           '<div style="font-size:12px;color:#475569;margin-top:6px">Persentase per pekerjaan adalah perkiraan umum, bukan data resmi SHST.</div>')
    return kartu("Perkiraan komposisi biaya", isi)


def html_material(P, L, lantai):
    m = hitung_material(P, L, lantai)
    kotak = lambda v, ket: (f'<div style="flex:1;min-width:110px;background:#FDF2F4;border-radius:14px;padding:12px;text-align:center">'
                            f'<div style="font-size:18px;font-weight:800;color:#B85B6C">{v}</div>'
                            f'<div style="font-size:12px;color:#475569;font-weight:700">{ket}</div></div>')
    isi = ('<div style="display:flex;gap:10px;flex-wrap:wrap">'
           + kotak(f"{r0(m['bata']):,}".replace(",", "."), "bata merah (buah)")
           + kotak(f"{r0(m['semen']):,}".replace(",", "."), "semen 40 kg (sak)")
           + kotak(f"{r0(m['besi']):,}".replace(",", "."), "besi beton (kg)") + '</div>'
           f'<div style="font-size:12px;color:#475569;margin-top:6px">Luas dinding bersih ≈ {fm(m["dinding"])} m², dihitung dari denah '
           '(tinggi dinding 3 m, dikurangi pintu 2,1 m dan jendela 1,2 m), bata ½ batu. '
           'Angka kasar, untuk RAB resmi tetap perlu gambar kerja.</div>')
    return kartu("Perkiraan kebutuhan material utama", isi)

# =====================================================================
# 5. PROSES DAN ANTARMUKA STREAMLIT
# =====================================================================
import base64
import re

import streamlit as st


def ke_img(html):
    """Ubah setiap <svg> menjadi <img> (data URI) agar aman tampil di st.markdown."""
    def ganti(m):
        svg = m.group(0)
        if "xmlns=" not in svg[:200]:
            svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        w = re.search(r'<svg[^>]*?\swidth="(\d+)"', svg)
        lebar = f"{w.group(1)}px" if w else "100%"
        b64 = base64.b64encode(svg.encode("utf-8")).decode()
        return (f'<img src="data:image/svg+xml;base64,{b64}" '
                f'style="width:{lebar};max-width:100%;height:auto;display:block">')
    return re.sub(r"<svg.*?</svg>", ganti, html, flags=re.S)


def proses(P, L, lantai, wilayah, tipe, manual, anggaran, TW, TP, KDB, KLB, GD, GS, lihat):
    """Mengembalikan 6 kartu HTML: total biaya, perbandingan, lahan, denah, komposisi, material."""
    d = data_lahan(TW or 0, TP or 0, KDB or 0, KLB or 0, GD or 0, GS or 0)
    e = harga_efektif(wilayah, tipe, lantai)
    h = manual if manual and manual > 0 else e[0]
    luas = P * L * lantai
    total = luas * h
    hasil = (html_hero(total, luas, h, anggaran, tipe, wilayah, e, manual),
             html_banding(P, L, lantai, tipe, wilayah, anggaran, d),
             html_lahan(P, L, lantai, d),
             html_denah(P, L, lantai, min(lihat, lantai)),
             html_komposisi(total),
             html_material(P, L, lantai))
    return [ke_img(x) for x in hasil]


def pakai_maksimal():
    """Dipanggil tombol: isi ukuran rumah terbesar yang lolos KDB, KLB, dan sempadan."""
    s = st.session_state
    d = data_lahan(s.TW, s.TP, s.KDB, s.KLB, s.GD, s.GS)
    s.P, s.L = ukuran_maksimal(s.P, s.L, s.lantai, d)


st.set_page_config(page_title="Rumah Hitung", page_icon="🏠", layout="wide")

# nilai awal isian (sekali saja, saat aplikasi pertama kali dibuka)
AWAL = {"P": 9.0, "L": 7.0, "lantai": 1, "wilayah": "Kota Magelang", "tipe": "Standar",
        "manual": 0, "anggaran": 500_000_000, "TW": 12.0, "TP": 20.0, "KDB": 60.0,
        "KLB": 1.2, "GD": 3.0, "GS": 1.0}
for k, v in AWAL.items():
    st.session_state.setdefault(k, v)

st.markdown(
    "<style>.stApp{background-color:#F8FAFC;"
    "background-image:radial-gradient(#F8E1E5 .5px,transparent .5px),radial-gradient(#F8E1E5 .5px,transparent .5px);"
    "background-size:24px 24px;background-position:0 0,12px 12px}"
    "#MainMenu,footer{visibility:hidden}</style>" + html_header(),
    unsafe_allow_html=True)

kiri, kanan = st.columns([5, 7], gap="large")

with kiri:
    st.markdown("### 1. Ukuran rumah")
    a, b = st.columns(2)
    P = a.number_input("Panjang (m)", min_value=1.0, step=0.5, key="P")
    L = b.number_input("Lebar (m)", min_value=1.0, step=0.5, key="L")
    lantai = st.radio("Jumlah lantai", [1, 2, 3], horizontal=True,
                      format_func=lambda x: f"{x} lantai", key="lantai")

    st.markdown("### 2. Wilayah & kualitas bangunan")
    wilayah = st.radio("Wilayah acuan harga (SHST)", list(HARGA), horizontal=True, key="wilayah")
    tipe = st.radio("Kualitas bangunan", ["Hemat", "Standar", "Premium"], horizontal=True, key="tipe")
    manual = st.number_input("Harga bangun per m² (Rp), isi 0 untuk memakai harga SHST",
                             min_value=0, step=100_000, key="manual")

    st.markdown("### 3. Anggaran kamu")
    anggaran = st.number_input("Anggaran (Rp), isi 0 jika belum ada",
                               min_value=0, step=10_000_000, key="anggaran")

    st.markdown("### 4. Lahan & aturan bangunan")
    a, b = st.columns(2)
    TW = a.number_input("Lebar tanah (m)", min_value=1.0, step=0.5, key="TW")
    TP = b.number_input("Panjang tanah (m)", min_value=1.0, step=0.5, key="TP")
    a, b = st.columns(2)
    KDB = a.number_input("KDB maks (%)", min_value=1.0, max_value=100.0, step=5.0, key="KDB")
    KLB = b.number_input("KLB maks (kali)", min_value=0.1, step=0.1, format="%.1f", key="KLB")
    a, b = st.columns(2)
    GD = a.number_input("Sempadan depan (m)", min_value=0.0, step=0.5, key="GD")
    GS = b.number_input("Sempadan samping & belakang (m)", min_value=0.0, step=0.5, key="GS")
    st.caption("Angka lahan hanya contoh. KDB, KLB, dan sempadan berbeda tiap lokasi, "
               "cek di KRK atau RDTR. Panjang rumah dianggap sejajar lebar tanah (sisi depan).")
    st.button("📐 Pakai ukuran rumah maksimal di lahan ini", on_click=pakai_maksimal, use_container_width=True)

with kanan:
    # pilihan denah dibuat sebelum kartu agar nilainya ikut dihitung
    lihat = st.radio("Denah lantai yang ditampilkan", list(range(1, lantai + 1)), horizontal=True,
                     format_func=lambda x: f"Lantai {x}", key=f"lihat_{lantai}")
    hero, banding, lahan_, denah_, komposisi, material = proses(
        P, L, lantai, wilayah, tipe, manual, anggaran, TW, TP, KDB, KLB, GD, GS, lihat)
    for kartu_html in (hero, banding, lahan_, denah_, komposisi, material):
        st.markdown(kartu_html, unsafe_allow_html=True)

st.caption("Harga acuan per m² memakai Standar Harga Satuan Tertinggi (SHST) Rumah Negara: "
           "Kota Magelang (Perwal No. 13 Tahun 2025) atau Kabupaten Magelang (Perbup No. 11 Tahun 2026). "
           "Biaya konstruksi fisik, belum termasuk perencanaan dan pengawasan. Estimasi awal, harga bisa diubah. "
           "KDB, KLB, dan sempadan harus dicek ke KRK/RDTR lokasi. Untuk menyimpan hasil sebagai PDF, "
           "tekan Ctrl+P (Cetak) di browser lalu pilih Save as PDF.")
