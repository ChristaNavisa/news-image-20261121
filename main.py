#!/usr/bin/env python3
"""news-image-20261121: draw Saturday 21 November 2026's world news as one
broadsheet front page (1024x1024 PNG) and write it to /output/entry.png.

Pure standard library (zlib, struct, math, os). No network, no randomness,
no timestamps: two runs write byte-identical files.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 242, 231)   # newsprint cream
INK = (18, 18, 18)        # near-black ink
RED = (166, 30, 34)       # lead-story red
BLUE = (31, 78, 121)      # deep news blue
TEAL = (14, 107, 107)     # teal accent
GOLD = (185, 138, 29)     # gold accent
GREY = (105, 102, 94)     # warm grey for rules / captions
LIGHT = (232, 226, 210)   # light panel fill
SKY = (23, 42, 74)        # night sky for the Poland scene
SKY2 = (48, 84, 130)      # lighter night blue
SEA = (58, 110, 145)      # sea blue for the cyclone scene
SAND = (214, 196, 150)    # sand for the map
GREEN = (74, 110, 62)     # land green for the map
WHITE = (255, 255, 255)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 rows of 5 cells, '#' = ink. Uppercase + digits + punctuation.
FONT = {
    'A': ("..#..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ')': (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = int(round(xs[k]))
                xb = int(round(xs[k + 1]))
                for x in range(xa, xb + 1):
                    self.set(x, y, c)

    def tri(self, a, b, c, col):
        self.poly([a, b, c], col)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, c, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    cv.rect(cx + col * scale, y + r * scale, scale, scale, c)
                    if bold:
                        cv.rect(cx + col * scale + 1, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_center(cv, cx, y, s, scale, c, bold=False):
    w = text_w(s, scale)
    return draw_text(cv, cx - w // 2, y, s, scale, c, bold)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    words = s.upper().split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, max_w, scale, c, leading=None, bold=False):
    lh = leading if leading is not None else 9 * scale
    for line in wrap(s, max_w, scale):
        draw_text(cv, x, y, line, scale, c, bold)
        y += lh
    return y


# ------------------------------------------------------------------ PNG -----
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------- scenes ------
def scene_poland(cv, x, y, w, h):
    """Night over south-east Poland: dark sky, land in outline, three missile
    trails arcing down to impact bursts, jets on patrol, Warsaw starred."""
    cv.rect(x, y, w, h, SKY)
    # stars
    for sx, sy in [(18, 14), (52, 30), (96, 10), (150, 26), (205, 12),
                   (250, 34), (300, 16), (352, 28), (410, 12), (470, 30),
                   (520, 14), (560, 26), (120, 44), (330, 42), (440, 46)]:
        cv.set(x + sx, y + sy, (200, 205, 220))
        cv.set(x + sx + 1, y + sy, (200, 205, 220))
    # moon
    cv.circle(x + w - 52, y + 30, 15, (235, 228, 200))
    cv.circle(x + w - 57, y + 26, 12, SKY)
    # land mass: stylised Poland + neighbours, low horizon
    land = [(x, y + h), (x, y + h - 52), (x + 70, y + h - 66),
            (x + 150, y + h - 58), (x + 230, y + h - 74),
            (x + 320, y + h - 60), (x + 420, y + h - 70),
            (x + 520, y + h - 56), (x + w, y + h - 64), (x + w, y + h)]
    cv.poly(land, (38, 62, 96))
    cv.poly([(x + 330, y + h - 62), (x + 420, y + h - 70),
             (x + 520, y + h - 56), (x + 470, y + h - 34),
             (x + 380, y + h - 30)], (30, 52, 84))
    # border dashes along the land edge
    for bx in range(0, w, 26):
        cv.set(x + bx, y + h - 60, (150, 160, 180))
    # missile trails: three arcs from top-right down to impact points
    impacts = [(x + 150, y + h - 46), (x + 330, y + h - 52),
               (x + 470, y + h - 44)]
    starts = [(x + 430, y + 8), (x + 520, y + 4), (x + 585, y + 12)]
    for (sx, sy), (ix, iy) in zip(starts, impacts):
        steps = 26
        for i in range(steps + 1):
            t = i / steps
            mx = int(sx + (ix - sx) * t)
            my = int(sy + (iy - sy) * t * t + 26 * math.sin(t * math.pi) * -0.4)
            cv.circle(mx, my, 2, (255, 170, 60))
            if i % 3 == 0:
                cv.set(mx, my, (255, 220, 130))
        # warhead dot
        cv.circle(sx, sy, 3, (255, 210, 110))
    # impact bursts
    for ix, iy in impacts:
        for r, col in [(16, (255, 120, 40)), (10, (255, 180, 70)),
                       (5, (255, 235, 150))]:
            cv.circle(ix, iy - 4, r, col)
        for a in range(8):
            ang = a * math.pi / 4
            cv.line(ix, iy - 4, ix + int(22 * math.cos(ang)),
                    iy - 4 + int(22 * math.sin(ang)), (255, 150, 50))
    # jets on patrol: two small delta silhouettes with contrails
    for jx, jy in [(x + 90, y + 42), (x + 250, y + 58)]:
        cv.tri((jx, jy), (jx - 16, jy + 6), (jx - 4, jy + 2), (220, 225, 235))
        cv.tri((jx, jy), (jx - 16, jy - 2), (jx - 4, jy), (200, 205, 220))
        cv.line(jx - 16, jy + 2, jx - 44, jy + 2, (170, 180, 200))
    # Warsaw star + labels
    wx, wy = x + 300, y + h - 78
    cv.circle(wx, wy, 4, GOLD)
    draw_text(cv, wx + 9, wy - 4, "WARSAW", 1, (235, 230, 210), bold=True)
    draw_text(cv, x + 10, y + h - 18, "POLAND", 1, (200, 205, 220), bold=True)
    draw_text(cv, x + w - 118, y + h - 18, "UKRAINE", 1, (200, 205, 220),
              bold=True)
    draw_text(cv, x + 8, y + 8, "3 OBJECTS DOWN", 1, (255, 200, 90), bold=True)


def scene_cyclone(cv, x, y, w, h):
    """Cyclone Akvan over the Bay of Bengal: spiral bands, rain, coastline
    with palms bending in the wind, Gopalpur marked."""
    cv.rect(x, y, w, h, (16, 52, 84))
    # spiral bands
    cx, cy = x + int(w * 0.62), y + int(h * 0.52)
    rmax = max(14, min(w, h) // 2 - 2)
    for r in range(8, rmax, 8):
        for a in range(0, 360, 4):
            ang = math.radians(a + r * 2.2)
            px = int(cx + r * math.cos(ang))
            py = int(cy + r * 0.72 * math.sin(ang))
            col = (210, 225, 240) if (a // 24) % 2 == 0 else (140, 170, 200)
            cv.set(px, py, col)
            cv.set(px + 1, py, col)
    cv.circle(cx, cy, 9, (240, 244, 250))
    cv.circle(cx, cy, 4, (16, 52, 84))
    # coastline + land (left-bottom)
    land = [(x, y + h), (x, y + int(h * 0.55)), (x + 90, y + int(h * 0.42)),
            (x + 190, y + int(h * 0.52)), (x + 250, y + int(h * 0.72)),
            (x + 210, y + h)]
    cv.poly(land, SAND)
    cv.line(x, y + int(h * 0.55), x + 90, y + int(h * 0.42), SEA, 2)
    cv.line(x + 90, y + int(h * 0.42), x + 190, y + int(h * 0.52), SEA, 2)
    # bending palms
    for px, py, lean in [(x + 60, y + h - 26, -14), (x + 120, y + h - 18, -18),
                         (x + 175, y + h - 30, -12)]:
        cv.line(px, py, px + lean, py - 26, (90, 70, 40), 2)
        for k in range(5):
            ang = math.pi * (0.15 + k * 0.18)
            cv.line(px + lean, py - 26,
                    px + lean + int(16 * math.cos(ang)),
                    py - 26 - int(7 * math.sin(ang)), (74, 110, 62))
    # rain streaks
    for rx in range(x + 8, x + w - 8, 17):
        ry = y + 12 + ((rx * 7) % 40)
        cv.line(rx, ry, rx - 5, ry + 12, (170, 195, 220))
    # Gopalpur marker
    gx, gy = x + 96, y + int(h * 0.44)
    cv.circle(gx, gy, 4, RED)
    draw_text(cv, gx + 9, gy - 4, "GOPALPUR", 1, WHITE, bold=True)
    draw_text(cv, x + 8, y + 8, "BAY OF BENGAL", 1, (200, 220, 240), bold=True)
    draw_text(cv, x + w - 92, y + h - 16, "ODISHA, INDIA", 1, WHITE, bold=True)


def scene_cop31(cv, x, y, w, h):
    """COP31 closing session in Antalya: hall, round emblem, rows of desks
    with flags, a clock past midnight — talks in overtime."""
    cv.rect(x, y, w, h, (24, 54, 66))
    # hall glow
    cv.rect(x, y, w, 8, GOLD)
    # big round emblem
    ex, ey = x + w // 2, y + 44
    cv.circle(ex, ey, 26, (240, 244, 250))
    cv.circle(ex, ey, 26, GOLD, fill=False)
    cv.circle(ex, ey, 20, TEAL)
    cv.circle(ex, ey, 12, (24, 54, 66))
    draw_text(cv, ex - 9, ey - 4, "31", 2, WHITE, bold=True)
    draw_text(cv, x + 8, y + 8, "ANTALYA", 1, (230, 225, 200), bold=True)
    # clock: overtime
    kx, ky = x + w - 34, y + 30
    cv.circle(kx, ky, 13, WHITE)
    cv.circle(kx, ky, 13, INK, fill=False)
    cv.line(kx, ky, kx, ky - 8, INK, 2)
    cv.line(kx, ky, kx + 7, ky + 2, INK, 2)
    draw_text(cv, x + w - 108, y + 50, "OVERTIME", 1, GOLD, bold=True)
    # desks with flags, two rows
    for row, dy in enumerate([y + h - 52, y + h - 26]):
        for i in range(7):
            dx = x + 14 + i * 48
            cv.rect(dx, dy, 38, 16, (52, 92, 110))
            cv.rect(dx, dy, 38, 3, (210, 205, 180))
            # tiny flag
            fx = dx + 16
            cv.vline(fx, dy - 12, 12, (220, 220, 220))
            fcols = [RED, BLUE, TEAL, GOLD, (120, 40, 90), (40, 120, 60),
                     (200, 90, 30)]
            cv.rect(fx + 1, dy - 12, 10, 7, fcols[(i + row * 2) % 7])
    # speaker silhouette at podium
    px, py = x + w // 2 - 4, y + h - 66
    cv.circle(px + 4, py - 8, 5, (230, 225, 210))
    cv.poly([(px, py), (px + 8, py), (px + 6, py - 8), (px + 2, py - 8)],
            (230, 225, 210))
    cv.rect(x + w // 2 - 26, y + h - 64, 52, 6, (210, 205, 180))


def chart_market(cv, x, y, w, h):
    """Friday sell-off: falling bars, S&P 500 line down, red close."""
    cv.rect(x, y, w, h, LIGHT)
    base = y + h - 18
    vals = [86, 82, 88, 74, 78, 66, 70, 58, 62, 48, 52, 38]
    bw = w // len(vals)
    for i, v in enumerate(vals):
        bh = int(v / 100 * (h - 30))
        col = RED if i >= 8 else (90, 90, 88)
        cv.rect(x + i * bw + 3, base - bh, bw - 6, bh, col)
    # trend line
    pts = [(x + i * bw + bw // 2, base - int(v / 100 * (h - 30)))
           for i, v in enumerate(vals)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], INK, 2)
    cv.line(x + 4, base, x + w - 4, base, INK, 2)
    draw_text(cv, x + 6, y + 5, "S&P 500 - FRIDAY", 1, INK, bold=True)
    draw_text(cv, x + w - 52, y + 5, "-3.7%", 1, RED, bold=True)


# -------------------------------------------------------------- world map ---
# Coarse continent outlines on a 0..100 x 0..50 grid, drawn scaled.
CONTINENTS = {
    'NA': [(4, 8), (10, 4), (20, 3), (28, 6), (30, 11), (26, 15), (22, 19),
           (18, 24), (14, 22), (10, 18), (6, 14)],
    'SA': [(24, 26), (29, 25), (33, 28), (32, 35), (28, 42), (25, 38),
           (23, 31)],
    'EU': [(46, 6), (52, 4), (57, 7), (55, 11), (50, 12), (46, 10)],
    'AF': [(46, 16), (53, 14), (60, 17), (62, 23), (58, 30), (54, 36),
           (50, 32), (46, 24)],
    'AS': [(58, 4), (72, 3), (86, 5), (96, 8), (94, 13), (86, 16),
           (78, 20), (72, 24), (66, 18), (60, 12), (57, 8)],
    'OC': [(84, 36), (92, 34), (96, 38), (90, 42), (84, 40)],
}


def draw_map(cv, x, y, w, h, markers):
    """markers: list of (gx, gy, num, label) in grid coords + label text."""
    cv.rect(x, y, w, h, (214, 228, 238))
    for pts in CONTINENTS.values():
        scaled = [(x + int(px * w / 100), y + int(py * h / 50)) for px, py in pts]
        cv.poly(scaled, GREEN)
    for gx, gy, num, label, ldx, ldy in markers:
        mx = x + int(gx * w / 100)
        my = y + int(gy * h / 50)
        cv.circle(mx, my, 6, RED)
        cv.circle(mx, my, 6, WHITE, fill=False)
        draw_text(cv, mx - 2, my - 3, str(num), 1, WHITE, bold=True)
        lx, ly = mx + ldx, my + ldy
        cv.rect(lx - 2, ly - 1, len(label) * 6 + 3, 9, (214, 228, 238))
        draw_text(cv, lx, ly, label, 1, INK, bold=True)


# ------------------------------------------------------------- the news -----
# 40 stories, 7 regions. Heroes 1-5 get pictures; 6-40 run as briefs.
# Every fact below was reported in the 21 November 2026 news cycle.
HERO_DECKS = {
    1: "TUSK CALLS IT A DELIBERATE PROVOCATION AS NATO JETS SCRAMBLE. RUTTE FLIES TO WARSAW TODAY.",
    3: "TALKS SPILL PAST THEIR FRIDAY DEADLINE AS NEARLY 200 NATIONS QUARREL OVER FOSSIL FUELS AND FINANCE.",
    4: "AI SHARES LEAD THE SLIDE; THE DOW JOINS THE S&P 500 IN CORRECTION TERRITORY.",
    5: "STORM CROSSES THE COAST NEAR GOPALPUR; 300,000 EVACUATED. NO MAJOR DAMAGE REPORTED.",
}

# (number, region, headline, deck) — headlines and decks kept short on purpose
BRIEFS = [
    (2, "EUROPE", "RUSSIA HITS KYIV IN HUGE OVERNIGHT ATTACK",
     "400 DRONES, 110 MISSILES; 8 KILLED, 28 HURT."),
    (6, "EUROPE", "UK AND EU SIGN FOOD, CARBON AND YOUTH DEALS",
     "THREE AGREEMENTS SEALED AT THE BRUSSELS SUMMIT."),
    (7, "EUROPE", "EU ADOPTS 1BN EUROS IN MILITARY AID FOR KYIV",
     "JOINT WEAPONS BUYING, DELIVERY BY END 2027."),
    (8, "EUROPE", "BRITAIN PLEDGES 1,000 DRONES IN 260M PACKAGE",
     "LONDON'S LATEST MILITARY AID FOR UKRAINE."),
    (9, "EUROPE", "ESTONIA TO SHUT RUSSIA BORDER CROSSINGS",
     "CLOSURES FROM 1 DECEMBER, TALLINN CONFIRMS."),
    (10, "EUROPE", "TWO CANDIDATES NAMED FOR ECB BOARD",
     "BOONE AND BRUNNERMEIER ENTER THE SUCCESSION RACE."),
    (11, "EUROPE", "POLAND SAYS IT STOPPED A STAGED-ATTACK PLOT",
     "WARSAW POINTS TO A PLAN NEAR KALININGRAD."),
    (12, "EUROPE", "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "LANDMARK RULING FOR THE ROHINGYA AT THE HAGUE."),
    (13, "N. AMERICA", "SENATE REJECTS IRAN WAR-POWERS VOTE, 51-48",
     "THE MEASURE HAD PASSED THE HOUSE FIRST."),
    (14, "N. AMERICA", "TRUMP PARDONS BASEBALL STAR PETE ROSE",
     "POSTHUMOUS PARDON FOR THE LATE HIT KING."),
    (15, "N. AMERICA", "US SANCTIONS FOUR IRANIANS OVER OIL CASH",
     "TREASURY TARGETS HANDLERS OF OIL REVENUES."),
    (16, "N. AMERICA", "JURY CONVICTS MAN WHO STARTED PALISADES FIRE",
     "LOS ANGELES VERDICT AFTER THE BLAZE TRIAL."),
    (17, "N. AMERICA", "CALIFORNIA SUBPOENAS NVIDIA OVER CHIP SALES",
     "PROBE INTO ALLEGED DEALS WITH CHINA."),
    (18, "N. AMERICA", "2027 HYUNDAI ELANTRA DEBUTS AT LA AUTO SHOW",
     "EIGHTH-GENERATION SEDAN, HYBRID OPTIONS."),
    (19, "N. AMERICA", "STARSHIP CAUGHT AFTER LONGEST ORBITAL FLIGHT",
     "SPACEX TOWER CATCH IN TEXAS ON SATURDAY."),
    (20, "N. AMERICA", "GUPTA JAILED 19 YEARS OVER MURDER PLOT",
     "US COURT SENTENCES FOILED PANNUN PLOTTER."),
    (21, "LATIN AMERICA", "BUKELE SEEKS THIRD TERM IN EL SALVADOR",
     "A WIN COULD KEEP HIM IN POWER UNTIL 2033."),
    (22, "LATIN AMERICA", "ARGENTINA PASSES DISABILITY LAW, 71-0",
     "SENATE BACKS PERMANENT FRAMEWORK UNANIMOUSLY."),
    (23, "MIDDLE EAST", "SAUDI COALITION INTERCEPTS HOUTHI MISSILES",
     "THREE BALLISTIC MISSILES DOWNED OVER RIYADH."),
    (24, "MIDDLE EAST", "22,000 CHILDREN KILLED IN GAZA, MINISTRY SAYS",
     "HEALTH MINISTRY TOLL PASSES A GRIM MARK."),
    (25, "MIDDLE EAST", "US AND ISRAEL WEIGH NEW STRIKE ON TEHRAN",
     "SOURCES SAY A FRESH ATTACK IS UNDER STUDY."),
    (26, "MIDDLE EAST", "TANKER STRUCK, FIRE IN STRAIT OF HORMUZ",
     "UK MARITIME BODY REPORTS AN INCIDENT AT SEA."),
    (27, "MIDDLE EAST", "INCIDENT REPORTED OFF YEMEN'S COAST",
     "VESSEL EVENT SOUTHWEST OF MUKALLA."),
    (28, "AFRICA", "EBOLA CRISIS HITS CHILDREN HARDEST IN CONGO",
     "ABOUT 100 SCHOOLS AFFECTED IN THE EAST."),
    (29, "AFRICA", "ADDIS ABABA TO HOST COP32 IN 2027",
     "ETHIOPIA TAKES THE NEXT CLIMATE SUMMIT."),
    (30, "ASIA-PACIFIC", "SENSEX RALLIES NEARLY 898 POINTS",
     "INDIAN MARKETS END THE WEEK HIGHER."),
    (31, "ASIA-PACIFIC", "MODI OPENS SCO DIALOGUE FORUM IN DELHI",
     "THREE-DAY CIVILISATION MEETING AT PURANA QILA."),
    (32, "ASIA-PACIFIC", "INDIA FIGHT BACK IN WELLINGTON TEST",
     "159 FOR 1 AT STUMPS, TRAILING BY 209 RUNS."),
    (33, "ASIA-PACIFIC", "TRUMP-XI-PUTIN SUMMIT ENDS WITH LITTLE DONE",
     "TRILATERAL MEETING IN CHINA YIELDS FEW RESULTS."),
    (34, "ASIA-PACIFIC", "TAIWAN WARNS META OVER CHINA-LINKED ACCOUNTS",
     "TAIPEI SAYS MANY TRIED TO SWAY ELECTIONS."),
    (35, "ASIA-PACIFIC", "BIG BANKS REPORT CYBERATTACKS ON VENDORS",
     "JPMORGAN, VISA AND MASTERCARD HIT; NETWORKS SAFE."),
    (36, "CLIMATE & SPACE", "TURKEY WINS 26BN DOLLARS IN COP31 DEALS",
     "HOST SECURES INVESTMENT AS TALKS STRUGGLE."),
    (37, "CLIMATE & SPACE", "COP31 DRAFT DROPS FOSSIL-FUEL WORDING",
     "'35 BY 35' POWER GOAL STAYS ON THE TABLE."),
    (38, "CLIMATE & SPACE", "BEPICOLOMBO REACHES MERCURY",
     "EUROPEAN-JAPANESE PROBE ARRIVES AT THE PLANET."),
    (39, "CLIMATE & SPACE", "PILL HAILED AS PANCREATIC CANCER HOPE",
     "DOCTORS CALL EARLY RESULTS A BREAKTHROUGH."),
    (40, "CLIMATE & SPACE", "STORM XAVIER GALE WARNINGS NARROW",
     "MARINE ALERT AREA SHRINKS IN THE ATLANTIC."),
]

STATS = [
    ("3", "WEAPONS DOWN IN POLAND"),
    ("400+", "DRONES FIRED AT UKRAINE"),
    ("-3.7%", "S&P 500 ON FRIDAY"),
    ("300,000", "EVACUATED AS AKVAN HIT"),
    ("1 BN", "EU ARMS AID FOR KYIV"),
    ("22,000", "CHILDREN KILLED IN GAZA"),
]

# map markers: (grid x, grid y, number, label, label dx, label dy)
MARKERS = [
    (53, 8, 1, "WARSAW", 11, -14),
    (58, 9, 2, "KYIV", 11, 3),
    (56, 13, 3, "ANTALYA", -64, 10),
    (64, 18, 4, "RIYADH", 11, -4),
    (79, 21, 5, "GOPALPUR", 11, -4),
    (17, 11, 6, "NEW YORK", 11, -4),
    (53, 28, 7, "GOMA", 11, -4),
    (94, 43, 8, "WELLINGTON", -78, -4),
]

COLUMNS = [
    [("EUROPE", [2, 6, 7, 8, 9, 10, 11, 12]),
     ("LATIN AMERICA", [21, 22]),
     ("MIDDLE EAST", [23, 24])],
    [("N. AMERICA", [13, 14, 15, 16, 17, 18, 19, 20]),
     ("MIDDLE EAST", [25, 26, 27]),
     ("AFRICA", [28])],
    [("AFRICA", [29]),
     ("ASIA-PACIFIC", [30, 31, 32, 33, 34, 35]),
     ("CLIMATE & SPACE", [36, 37, 38, 39, 40])],
]


# -------------------------------------------------------------- layout ------
def rule(cv, x, y, w, t=2):
    cv.hline(x, y, w, INK, t)


def draw_brief(cv, x, y, w, num, headline, deck):
    draw_text(cv, x, y, str(num) + ".", 1, RED, bold=True)
    hx = x + 22
    for line in wrap(headline, w - 22, 1):
        draw_text(cv, hx, y, line, 1, INK, bold=True)
        y += 9
    for line in wrap(deck, w - 22, 1):
        draw_text(cv, hx, y, line, 1, GREY)
        y += 9
    return y + 3


def draw_front():
    cv = Canvas(W, H, PAPER)
    L, R = 28, 996  # left / right margins

    # top line
    draw_text(cv, L, 12, "ONE DAY - ONE FRONT PAGE", 1, GREY, bold=True)
    tw = text_w("SATURDAY 21 NOVEMBER 2026", 1)
    draw_text(cv, R - tw, 12, "SATURDAY 21 NOVEMBER 2026", 1, GREY, bold=True)
    rule(cv, L, 26, R - L, 2)

    # masthead
    draw_center(cv, W // 2, 34, "THE WORLD IN ONE DAY", 8, INK, bold=True)
    draw_center(cv, W // 2, 100, "SATURDAY, 21 NOVEMBER 2026", 3, RED, bold=True)
    draw_center(cv, W // 2, 126, "40 STORIES - 7 REGIONS - ONE FRONT PAGE",
                2, INK)
    rule(cv, L, 146, R - L, 3)

    # stat strip: 6 boxes
    bw = (R - L - 5 * 4) // 6
    for i, (num, label) in enumerate(STATS):
        bx = L + i * (bw + 4)
        cv.rect(bx, 154, bw, 52, LIGHT)
        cv.rect(bx, 154, bw, 2, RED)
        draw_center(cv, bx + bw // 2, 162, num, 3, INK, bold=True)
        y = 186
        for line in wrap(label, bw - 10, 1):
            draw_center(cv, bx + bw // 2, y, line, 1, GREY)
            y += 9
    rule(cv, L, 212, R - L, 2)

    # ---- lead row ----
    lx, lw = L, 600
    rx, rw = 644, 352
    draw_text(cv, lx, 222, "LEAD STORY - EUROPE", 1, RED, bold=True)
    draw_text(cv, lx, 238, "MISSILES FALL", 5, INK, bold=True)
    draw_text(cv, lx, 274, "ON POLAND", 5, INK, bold=True)
    para(cv, lx, 314, HERO_DECKS[1], lw, 2, INK, leading=20)
    scene_poland(cv, lx, 360, lw, 128)

    draw_text(cv, rx, 222, "CLIMATE - ANTALYA", 1, RED, bold=True)
    draw_text(cv, rx, 238, "COP31 IN OVERTIME", 3, INK, bold=True)
    scene_cop31(cv, rx, 266, rw, 104)
    para(cv, rx, 376, HERO_DECKS[3], rw, 1, GREY, leading=10)
    draw_text(cv, rx, 410, "WALL ST IN CORRECTION", 2, INK, bold=True)
    chart_market(cv, rx, 432, rw, 56)

    rule(cv, L, 496, R - L, 2)

    # ---- middle band: map + cyclone ----
    draw_text(cv, L, 506, "THE DAY ON THE MAP - 8 PLACES THAT MADE THE NEWS",
              1, INK, bold=True)
    draw_map(cv, L, 520, lw, 136, MARKERS)
    draw_text(cv, rx, 506, "AKVAN HITS ODISHA", 3, INK, bold=True)
    scene_cyclone(cv, rx, 530, rw, 88)
    para(cv, rx, 624, HERO_DECKS[5], rw, 1, GREY, leading=10)

    rule(cv, L, 664, R - L, 2)

    # ---- story grid: 3 columns, 12 briefs each ----
    col_x = [L, 360, 692]
    col_w = [304, 304, 304]
    by_num = {b[0]: b for b in BRIEFS}
    for ci, groups in enumerate(COLUMNS):
        x = col_x[ci]
        y = 674
        for reg, nums in groups:
            draw_text(cv, x, y, reg, 2, RED, bold=True)
            y += 15
            rule(cv, x, y, col_w[ci], 1)
            y += 5
            for num in nums:
                _n, _r, head, deck = by_num[num]
                y = draw_brief(cv, x, y, col_w[ci], num, head, deck)

    # footer
    rule(cv, L, 992, R - L, 2)
    draw_center(cv, W // 2, 1002,
                "COMPILED FROM WIRE REPORTS - SATURDAY 21 NOVEMBER 2026",
                1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = draw_front()
    n = write_png(cv, path)
    print(f"wrote {path} ({n} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
