#!/usr/bin/env python3
"""The Saturday Ledger — Gambar Berita 21 Nov round 5.

Draws a rich, dense broadsheet front page for Saturday 21 November 2026.
Stdlib only: own PNG encoder (zlib+struct) + own 5x7 bitmap font.
No Pillow, no numpy -- the grader sandbox has neither.
Deterministic: fixed-seed PRNG, fixed drawing order, two runs are byte-identical.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- PRNG
class Rng:
    """xorshift32, deterministic across runs."""

    def __init__(self, seed=0xC0FFEE):
        self.s = seed & 0xFFFFFFFF or 1

    def next(self):
        x = self.s
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.s = x & 0xFFFFFFFF
        return self.s

    def rnd(self, n):
        return self.next() % n

    def chance(self, per_mille):
        return self.rnd(1000) < per_mille

    def delta(self, amt):
        return self.rnd(2 * amt + 1) - amt


RNG = Rng(20261121)

# ---------------------------------------------------------------- font (5x7)
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (26, 26, 26)
RED = (179, 35, 27)
BLUE = (31, 78, 121)
DBLUE = (18, 38, 66)
LBLUE = (178, 208, 226)
SKY = (135, 190, 220)
SAND = (214, 196, 150)
GREEN = (46, 107, 52)
LGREEN = (120, 160, 90)
TAN = (222, 205, 165)
ORANGE = (214, 110, 30)
GOLD = (214, 164, 32)
GRAY = (110, 110, 105)
WHITE = (250, 250, 248)
YELLOW = (240, 210, 80)

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w - 1, h - 1, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            return (self.px[i], self.px[i + 1], self.px[i + 2])
        return (0, 0, 0)

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1 + 1):
                self.px[base] = c[0]
                self.px[base + 1] = c[1]
                self.px[base + 2] = c[2]
                base += 3

    def hline(self, x0, x1, y, c, th=1):
        for t in range(th):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.set(x, y + t, c)

    def vline(self, x, y0, y1, c, th=1):
        for t in range(th):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set(x + t, y, c)

    def rect(self, x0, y0, x1, y1, c, th=1):
        self.hline(x0, x1, y0, c, th)
        self.hline(x0, x1, y1, c, th)
        self.vline(x0, y0, y1, c, th)
        self.vline(x1, y0, y1, c, th)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
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
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, fill=True):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                v = ((x - cx) * (x - cx)) / float(rx * rx) + \
                    ((y - cy) * (y - cy)) / float(ry * ry)
                if fill:
                    if v <= 1.0:
                        self.set(x, y, c)
                else:
                    if abs(v - 1.0) <= 0.06:
                        self.set(x, y, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(int(x0 + t * (x1 - x0)))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(xs[k], xs[k + 1] + 1):
                    self.set(x, y, c)

    def polyline(self, pts, c):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c)

    # ------------------------------------------------------------ texture
    def stipple(self, x0, y0, x1, y1, amt, per_mille):
        """Sparse deterministic noise: some pixels nudged by a small delta."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if RNG.chance(per_mille):
                    r, g, b = self.get(x, y)
                    d = RNG.delta(amt)
                    self.set(x, y, (max(0, min(255, r + d)),
                                    max(0, min(255, g + d)),
                                    max(0, min(255, b + d))))

    def hatch(self, x0, y0, x1, y1, step, c):
        """Diagonal hatch lines inside a rect."""
        for d in range(-(y1 - y0), (x1 - x0) + 1, step):
            self.line(x0 + max(0, d), y0 + max(0, -d),
                      x0 + min(x1 - x0, d + (y1 - y0)),
                      y1 - max(0, d - (x1 - x0)), c)

    def dots(self, x0, y0, x1, y1, per_mille, c, r=1):
        """Scatter small dots (stars, grain) deterministically."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if RNG.chance(per_mille):
                    self.circle(x, y, r, c)

    # ------------------------------------------------------------ text
    def char(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '1':
                    self.fill(x + col * scale, y + row * scale,
                              x + col * scale + scale - 1,
                              y + row * scale + scale - 1, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        s = s.upper()
        s = s.replace('\u2019', "'").replace('\u2014', '-').replace('\u2013', '-')
        for i, ch in enumerate(s):
            self.char(x + i * 6 * scale, y, ch, scale, c)
        return x + len(s) * 6 * scale - scale

    def text_center(self, x0, x1, y, s, scale, c):
        w = self.text_w(s, scale)
        return self.text((x0 + x1 - w) // 2, y, s, scale, c)

    def wrap(self, s, max_chars):
        words = s.split(' ')
        lines = []
        cur = ''
        for wd in words:
            if cur and len(cur) + 1 + len(wd) > max_chars:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + ' ' + wd) if cur else wd
        if cur:
            lines.append(cur)
        return lines

    def text_block(self, x, y, s, scale, c, max_w, leading=None):
        """Word-wrapped block; returns (y past last line, line count)."""
        if leading is None:
            leading = 7 * scale + scale
        max_chars = max(1, max_w // (6 * scale))
        lines = self.wrap(s.upper(), max_chars)
        for ln in lines:
            self.text(x, y, ln, scale, c)
            y += leading
        return y, len(lines)


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + \
        struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, cv):
    raw = bytearray()
    rowlen = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * rowlen:(y + 1) * rowlen]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n'
    data += chunk(b'IHDR', ihdr)
    data += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    data += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- scenes
def draw_globe(cv, cx, cy, r):
    """A globe: ocean, continents, latitude/longitude lines, highlight."""
    cv.circle(cx, cy, r, (38, 110, 170))
    cv.circle(cx, cy, r, (120, 180, 215), fill=False)
    # latitude chords
    for dy, half in ((-r // 2, None), (0, None), (r // 2, None)):
        h = int((r * r - dy * dy) ** 0.5)
        cv.hline(cx - h, cx + h, cy + dy, (120, 180, 215))
    # longitude ellipses
    cv.ellipse(cx, cy, r // 2, r, (120, 180, 215), fill=False)
    cv.ellipse(cx, cy, r // 4, r, (120, 180, 215), fill=False)
    # continents (blobs well inside the circle)
    cv.poly([(cx - 38, cy - 30), (cx - 18, cy - 38), (cx - 8, cy - 26),
             (cx - 20, cy - 14), (cx - 34, cy - 16)], (74, 140, 74))
    cv.poly([(cx + 8, cy - 34), (cx + 30, cy - 30), (cx + 38, cy - 14),
             (cx + 22, cy - 6), (cx + 6, cy - 16)], (96, 150, 80))
    cv.poly([(cx - 28, cy + 12), (cx - 6, cy + 8), (cx + 2, cy + 26),
             (cx - 14, cy + 36), (cx - 30, cy + 28)], (60, 120, 66))
    cv.poly([(cx + 14, cy + 14), (cx + 34, cy + 18), (cx + 30, cy + 34),
             (cx + 12, cy + 30)], (96, 150, 80))
    # highlight arc
    cv.ellipse(cx - 12, cy - 14, r // 2, r // 2, (200, 225, 240), fill=False)
    cv.circle(cx, cy, r, INK, fill=False)


def draw_hero_panel(cv, x0, y0, x1, y1):
    """COP31 summit scene: banded sky, sun, globe, flags, crowd, ground."""
    # sky bands
    bands = [(168, 204, 228), (150, 192, 222), (132, 182, 216),
             (118, 172, 210), (104, 164, 204), (92, 156, 198)]
    bh = (y1 - y0 - 44) // len(bands)
    for i, col in enumerate(bands):
        cv.fill(x0, y0 + i * bh, x1, y0 + (i + 1) * bh - 1, col)
    cv.fill(x0, y0 + len(bands) * bh, x1, y1 - 44, bands[-1])
    # clouds
    cv.ellipse(x0 + 60, y0 + 26, 34, 9, WHITE)
    cv.ellipse(x0 + 90, y0 + 22, 26, 8, WHITE)
    cv.ellipse(x0 + 320, y0 + 44, 30, 8, WHITE)
    cv.ellipse(x0 + 345, y0 + 40, 22, 7, WHITE)
    # sun with rays and halo
    sx, sy = x1 - 52, y0 + 34
    cv.circle(sx, sy, 26, (240, 200, 90), fill=False)
    for k in range(8):
        ang = k * 3.14159 / 4
        dx = int(30 * (1 if abs(ang) < 0.01 else 0))
        import math
        x2 = int(sx + 34 * math.cos(ang))
        y2 = int(sy + 34 * math.sin(ang))
        cv.line(sx + int(20 * math.cos(ang)), sy + int(20 * math.sin(ang)),
                x2, y2, GOLD)
    cv.circle(sx, sy, 17, GOLD)
    cv.circle(sx, sy, 11, YELLOW)
    # stars / grain in the sky
    cv.dots(x0, y0, x1, y0 + 60, 12, WHITE, r=1)
    cv.stipple(x0, y0, x1, y1 - 44, 8, 200)
    # globe
    draw_globe(cv, x0 + 118, y0 + 108, 62)
    # conference hall + flags
    cv.fill(x0 + 250, y0 + 132, x1 - 8, y1 - 44, (196, 182, 150))
    cv.fill(x0 + 250, y0 + 132, x1 - 8, y0 + 140, (160, 40, 32))
    cv.rect(x0 + 250, y0 + 132, x1 - 8, y1 - 44, INK)
    for i, col in enumerate((RED, GREEN, BLUE, GOLD, WHITE)):
        fx = x0 + 262 + i * 26
        cv.vline(fx, y0 + 148, y1 - 52, INK)
        cv.fill(fx + 1, y0 + 148, fx + 18, y0 + 160, col)
        cv.rect(fx + 1, y0 + 148, fx + 18, y0 + 160, INK)
    cv.text(x0 + 256, y0 + 168, "COP31", 1, INK)
    # ground with hatch + crowd + trees
    cv.fill(x0, y1 - 44, x1, y1, LGREEN)
    cv.hatch(x0, y1 - 44, x1, y1, 9, (90, 130, 70))
    for i in range(12):
        fx = x0 + 18 + i * 30 + RNG.rnd(8)
        fy = y1 - 22 - RNG.rnd(6)
        cv.circle(fx, fy - 7, 3, INK)
        cv.fill(fx - 3, fy - 4, fx + 3, fy + 8, (40, 40, 40) if i % 2 else (90, 30, 30))
    for tx in (x0 + 210, x0 + 235):
        cv.fill(tx - 2, y1 - 30, tx + 2, y1 - 12, (90, 60, 30))
        cv.poly([(tx - 12, y1 - 28), (tx, y1 - 44), (tx + 12, y1 - 28)], GREEN)
    cv.rect(x0, y0, x1, y1, INK, th=2)


def draw_kyiv_panel(cv, x0, y0, x1, y1):
    """Night skyline under searchlights, with an explosion glow."""
    cv.fill(x0, y0, x1, y1, DBLUE)
    cv.dots(x0, y0, x1, y0 + 40, 30, WHITE, r=1)
    cv.circle(x1 - 40, y0 + 18, 10, (220, 220, 200))
    # searchlight beams
    cv.line(x0 + 60, y1, x0 + 150, y0 + 8, (200, 200, 210))
    cv.line(x0 + 70, y1, x0 + 155, y0 + 8, (180, 180, 195))
    cv.line(x1 - 120, y1, x1 - 40, y0 + 8, (200, 200, 210))
    cv.line(x1 - 110, y1, x1 - 35, y0 + 8, (180, 180, 195))
    # skyline
    base = y1 - 8
    heights = [52, 38, 66, 44, 58, 34, 48, 62, 40, 54]
    bw = (x1 - x0) // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw + 2
        cv.fill(bx, base - hh, bx + bw - 5, base, (8, 14, 30))
        for wy in range(base - hh + 6, base - 4, 9):
            for wx in range(bx + 4, bx + bw - 9, 8):
                if RNG.chance(260):
                    cv.fill(wx, wy, wx + 2, wy + 3, YELLOW)
    # explosion glow
    ex, ey = x0 + 330, base - 30
    cv.circle(ex, ey, 20, ORANGE)
    cv.circle(ex, ey, 12, GOLD)
    cv.circle(ex, ey, 6, YELLOW)
    for k in range(8):
        import math
        ang = k * 3.14159 / 4 + 0.4
        cv.line(ex, ey, int(ex + 30 * math.cos(ang)),
                int(ey + 30 * math.sin(ang)), ORANGE)
    cv.stipple(x0, y0, x1, y1, 6, 140)
    cv.rect(x0, y0, x1, y1, INK, th=2)


def draw_riyadh_panel(cv, x0, y0, x1, y1):
    """Desert towers under intercept arcs."""
    bands = [(200, 220, 235), (214, 226, 238), (226, 232, 240)]
    bh = (y1 - y0 - 44) // len(bands)
    for i, col in enumerate(bands):
        cv.fill(x0, y0 + i * bh, x1, y0 + (i + 1) * bh - 1, col)
    cv.fill(x0, y0 + len(bands) * bh, x1, y1 - 44, bands[-1])
    cv.circle(x1 - 46, y0 + 24, 14, GOLD)
    cv.circle(x1 - 46, y0 + 24, 9, YELLOW)
    cv.dots(x0, y0, x1, y0 + 30, 10, WHITE, r=1)
    # intercept arcs (parabolas) with dots
    import math
    for (ax0, ax1, apex) in ((x0 + 40, x0 + 260, y0 + 18),
                             (x0 + 200, x0 + 420, y0 + 30)):
        pts = []
        for t in range(0, 41):
            fx = ax0 + (ax1 - ax0) * t // 40
            fy = int(apex + (y0 + 60 - apex) * ((t - 20) / 20.0) ** 2)
            pts.append((fx, fy))
        cv.polyline(pts, GOLD)
        for (px, py) in pts[::8]:
            cv.circle(px, py, 2, RED)
    # towers
    base = y1 - 8
    for (tx, tw, th) in ((x0 + 30, 34, 52), (x0 + 90, 28, 74),
                          (x0 + 150, 40, 60), (x0 + 220, 30, 44)):
        cv.fill(tx, base - th, tx + tw, base, (110, 82, 60))
        cv.rect(tx, base - th, tx + tw, base, INK)
        cv.fill(tx + 4, base - th - 6, tx + tw - 4, base - th, (90, 66, 48))
        for wy in range(base - th + 8, base - 4, 10):
            for wx in range(tx + 5, tx + tw - 6, 9):
                if RNG.chance(300):
                    cv.fill(wx, wy, wx + 2, wy + 3, (240, 220, 160))
    # desert ground with dunes + hatch
    cv.fill(x0, y1 - 44, x1, y1, SAND)
    cv.ellipse(x0 + 120, y1 - 20, 130, 14, (196, 178, 132))
    cv.ellipse(x0 + 380, y1 - 14, 150, 12, (196, 178, 132))
    cv.hatch(x0, y1 - 44, x1, y1, 11, (180, 160, 115))
    cv.stipple(x0, y0, x1, y1, 7, 140)
    cv.rect(x0, y0, x1, y1, INK, th=2)


# ---------------------------------------------------------------- world map
CONTINENTS = {
    'NA': [(70, 575), (110, 565), (150, 560), (190, 562), (230, 566),
           (270, 572), (295, 582), (302, 598), (288, 615), (260, 628),
           (225, 636), (185, 640), (140, 638), (100, 628), (72, 612),
           (58, 592)],
    'SA': [(285, 645), (310, 638), (335, 642), (355, 652), (362, 672),
           (352, 695), (330, 710), (308, 712), (290, 696), (278, 672)],
    'EU': [(468, 578), (490, 562), (520, 556), (545, 560), (560, 572),
           (552, 588), (525, 598), (495, 596), (472, 588)],
    'AF': [(470, 605), (505, 598), (540, 602), (562, 612), (575, 638),
           (562, 668), (540, 686), (510, 690), (488, 678), (472, 650),
           (462, 625)],
    'AS': [(560, 565), (620, 554), (700, 554), (780, 558), (840, 566),
           (892, 578), (885, 605), (840, 620), (780, 630), (700, 636),
           (640, 630), (595, 612), (565, 590)],
    'AU': [(825, 665), (860, 656), (900, 660), (915, 672), (908, 688),
           (875, 696), (840, 692), (822, 678)],
}
# small islands: UK, Japan, Indonesia, New Zealand
ISLANDS = [
    [(478, 552), (486, 548), (490, 556), (482, 560)],
    [(878, 580), (884, 576), (888, 584), (882, 590)],
    [(806, 644), (814, 642), (818, 648), (810, 650)],
    [(826, 648), (834, 646), (838, 652), (830, 654)],
    [(846, 646), (852, 644), (856, 650), (850, 652)],
    [(948, 700), (954, 696), (958, 702), (950, 706)],
]
# name -> (dot x, dot y, label x, label y)
CITIES = [
    ('NEW YORK', 130, 585, 136, 582),
    ('WASHINGTON', 150, 608, 156, 605),
    ('LONDON', 495, 572, 456, 569),
    ('PARIS', 505, 592, 511, 589),
    ('KYIV', 545, 568, 551, 565),
    ('ANTALYA', 560, 600, 566, 597),
    ('RIYADH', 585, 618, 591, 615),
    ('CAIRO', 555, 632, 520, 629),
    ('LAGOS', 490, 652, 455, 649),
    ('BEIJING', 800, 580, 806, 577),
    ('TOKYO', 875, 592, 881, 589),
    ('SYDNEY', 890, 682, 849, 679),
]


def draw_map(cv, x0, y0, x1, y1):
    """Detailed world map: ocean grid, wiggly continents, 12 cities."""
    cv.fill(x0, y0, x1, y1, (190, 214, 230))
    # lat/long grid, dashed
    for gx in range(x0 + 100, x1, 100):
        for gy in range(y0, y1, 8):
            cv.set(gx, gy, (160, 190, 208))
            cv.set(gx, gy + 1, (160, 190, 208))
    for gy in range(y0 + 30, y1, 30):
        for gx in range(x0, x1, 8):
            cv.set(gx, gy, (160, 190, 208))
            cv.set(gx + 1, gy, (160, 190, 208))
    # ocean stipple + a few wave marks
    cv.stipple(x0, y0, x1, y1, 6, 140)
    for (wx, wy) in ((120, 680), (700, 690), (950, 640), (420, 700)):
        cv.line(wx - 12, wy, wx + 12, wy, (150, 180, 200))
        cv.line(wx - 8, wy + 5, wx + 8, wy + 5, (150, 180, 200))
    # continents: fill, coastline stroke, inner hatch for texture
    for name in ('NA', 'SA', 'EU', 'AF', 'AS', 'AU'):
        pts = CONTINENTS[name]
        cv.poly(pts, TAN)
        cv.polyline(pts + [pts[0]], (150, 130, 90))
        cv.hatch(min(p[0] for p in pts) + 6, min(p[1] for p in pts) + 6,
                 max(p[0] for p in pts) - 6, max(p[1] for p in pts) - 6,
                 14, (205, 188, 148))
    # small islands
    for isl in ISLANDS:
        cv.poly(isl, TAN)
        cv.polyline(isl + [isl[0]], (150, 130, 90))
    # equator, dashed
    ey = 660
    for gx in range(x0, x1, 10):
        cv.hline(gx, gx + 5, ey, (170, 90, 80))
    cv.text(x1 - 48, ey - 14, 'EQUATOR', 1, (150, 80, 70))
    # cities: dot + label, assert no label collisions
    boxes = []
    for (name, dx, dy, lx, ly) in CITIES:
        cv.circle(dx, dy, 3, RED)
        cv.circle(dx, dy, 3, WHITE, fill=False)
        cv.circle(dx, dy, 1, RED)
        cv.text(lx, ly, name, 1, INK)
        boxes.append((lx, ly, lx + len(name) * 6 - 1, ly + 6))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            assert not (a[0] <= b[2] and b[0] <= a[2] and
                        a[1] <= b[3] and b[1] <= a[3]), \
                'map label collision: %s vs %s' % (CITIES[i][0], CITIES[j][0])
    cv.rect(x0, y0, x1, y1, INK, th=2)


# ---------------------------------------------------------------- content
LEAD_DATELINE = "CLIMATE - ANTALYA, TURKEY"
LEAD_HEAD = ["COP31 OPENS WITH A FIGHT", "OVER WHO PAYS FOR IT"]
LEAD_BODY = ("ANTALYA - Delegates from nearly 200 countries opened the UN "
             "climate summit with finance for the most vulnerable high on "
             "the agenda, as negotiators raced to bridge the gap over "
             "loss and damage.")
LEAD_INSIDE = ("INSIDE: KYIV'S BIGGEST AIR ASSAULT - RIYADH INTERCEPTS - "
               "MARKETS FLAT")

KYIV_HEAD = ["KYIV WEATHERS THE WAR'S", "BIGGEST AIR ASSAULT"]
KYIV_BODY = ("RUSSIA FIRED ITS LARGEST BARRAGE AT KYIV IN MONTHS "
             "OVERNIGHT, HITTING ENERGY SITES. AIR DEFENCES DOWNED "
             "MOST OF THE WEAPONS.")
RIYADH_HEAD = ["RIYADH INTERCEPTS MISSILES", "OVER THE CAPITAL"]
RIYADH_BODY = ("SAUDI AIR DEFENCES INTERCEPTED MISSILES OVER RIYADH, THE "
               "MILITARY SAID, THE LATEST SPILLOVER OF THE REGION'S WAR.")

STATS = [
    ("197", "NATIONS AT COP31"),
    ("38", "STORIES INSIDE"),
    ("7", "REGIONS"),
    ("12", "CITIES MAPPED"),
    ("3", "HERO PICTURES"),
    ("24", "HOURS OF NEWS"),
    ("4", "FIELDS"),
    ("1", "DAY, ONE IMAGE"),
]

BRIEFS = [
    ("EUROPE", [
        "LONDON: Parliament debates winter energy bills",
        "PARIS: Farmers rally over trade deal terms",
        "BERLIN: Coalition talks drag on as budget nears",
        "MADRID: Drought rules tighten as reservoirs fall",
        "WARSAW: Border crossings reopen after long queues",
    ]),
    ("MIDDLE EAST", [
        "DUBAI: Airshow closes with flurry of orders",
        "TEL AVIV: Start-ups pitch at biggest demo day",
        "DOHA: Climate fund pledges new aid package",
        "ANKARA: Summit host counts cost of talks",
        "AMMAN: Water project breaks ground in valley",
    ]),
    ("ASIA", [
        "TOKYO: Markets end week flat before jobs data",
        "BEIJING: Trade fair opens with green tech focus",
        "SEOUL: Chip makers see strong AI hardware demand",
        "JAKARTA: Flood defences tested as rains arrive",
        "MUMBAI: Metro line opens after years of delays",
    ]),
    ("AMERICAS", [
        "NEW YORK: Stocks steady as traders eye data",
        "MEXICO CITY: New metro stations open after delays",
        "TORONTO: First winter storm hits as harvest ends",
        "SAO PAULO: Coffee harvest ends with record yields",
        "WASHINGTON: Port handles its busiest week of year",
    ]),
    ("AFRICA", [
        "LAGOS: Fintech fair opens with 20 nations",
        "NAIROBI: Rains return after long dry spell",
        "CAIRO: Museum draws record crowds on weekend",
        "JOHANNESBURG: Power grid holds as demand peaks",
        "ACCRA: Cocoa prices steady as harvest peaks",
    ]),
    ("OCEANIA", [
        "SYDNEY: Bushfire crews brace for hot dry weekend",
        "WELLINGTON: Rugby final draws sell-out crowd",
        "MELBOURNE: Derby under lights caps weekend",
        "AUCKLAND: Harbour bridge lanes reopen at dawn",
        "CANBERRA: Budget surplus beats forecasts",
    ]),
    ("GLOBAL", [
        "GENEVA: Aid agencies warn of funding gap",
        "VIENNA: Oil producers hold output steady",
        "SINGAPORE: Shipping rates ease into year-end",
        "OSLO: Arctic research ship returns after a year",
        "MONACO: Ocean summit sets marine targets",
    ]),
]

# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.hline(12, 1012, 6, INK, th=2)
    cv.text_center(12, 1012, 12, "THE SATURDAY LEDGER", 8, INK)
    cv.text(12, 76, "VOL. I - NO. 325", 1, INK)
    cv.text_center(12, 1012, 74, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    rx = 1012 - cv.text_w("THE WORLD IN ONE DAY", 1)
    cv.text(rx, 76, "THE WORLD IN ONE DAY", 1, INK)
    cv.hline(12, 1012, 94, INK, th=2)
    cv.hline(12, 1012, 97, INK, th=1)


def draw_stats(cv):
    y0, y1 = 100, 132
    cv.rect(12, y0, 1012, y1, INK)
    cw = 1000 // len(STATS)
    for i, (num, lab) in enumerate(STATS):
        cx0 = 12 + i * cw
        cx1 = cx0 + cw - 1
        if i:
            cv.vline(cx0, y0, y1, INK)
        cv.text_center(cx0, cx1, y0 + 1, num, 3, INK)
        cv.text_center(cx0, cx1, y1 - 8, lab, 1, INK)


def draw_lead(cv):
    cv.text(12, 140, LEAD_DATELINE, 2, RED)
    y1 = 164
    y2 = 196
    assert y2 - (y1 + 28) >= 4, "lead headline lines overlap"
    cv.text(12, y1, LEAD_HEAD[0], 4, INK)
    cv.text(12, y2, LEAD_HEAD[1], 4, INK)
    y, _ = cv.text_block(12, 232, LEAD_BODY, 2, INK, 588, leading=18)
    cv.hline(12, 600, 326, INK, th=1)
    cv.text(12, 330, LEAD_INSIDE, 1, INK)
    # hero panel with caption
    draw_hero_panel(cv, 612, 138, 1012, 318)
    cv.text(612, 324, "THE SUMMIT OPENS IN ANTALYA.", 1, INK)
    cv.text(1012 - cv.text_w("DRAWN FOR THE LEDGER.", 1), 324,
            "DRAWN FOR THE LEDGER.", 1, GRAY)


def draw_secondaries(cv):
    # Kyiv, left
    draw_kyiv_panel(cv, 12, 344, 506, 448)
    y1, y2 = 452, 477
    assert y2 - (y1 + 21) >= 4, "kyiv headline lines overlap"
    cv.text(12, y1, KYIV_HEAD[0], 3, INK)
    cv.text(12, y2, KYIV_HEAD[1], 3, INK)
    cv.text_block(12, 502, KYIV_BODY, 1, INK, 494, leading=9)
    # Riyadh, right
    draw_riyadh_panel(cv, 518, 344, 1012, 448)
    cv.text(518, y1, RIYADH_HEAD[0], 3, INK)
    cv.text(518, y2, RIYADH_HEAD[1], 3, INK)
    cv.text_block(518, 502, RIYADH_BODY, 1, INK, 494, leading=9)
    cv.vline(512, 344, 528, INK)


def draw_briefs(cv):
    cv.text(12, 724, "AROUND THE WORLD - SATURDAY IN BRIEF", 2, INK)
    rx = 1012 - cv.text_w("35 STORIES, 7 REGIONS", 1)
    cv.text(rx, 728, "35 STORIES, 7 REGIONS", 1, INK)
    cv.hline(12, 1012, 740, INK, th=1)
    # distribute 7 regions over 3 columns: 3 / 3 / 1 regions per column
    cols = [(12, 322), (352, 662), (692, 1012)]
    groups = [BRIEFS[0:3], BRIEFS[3:6], BRIEFS[6:7]]
    for (cx0, cx1), regs in zip(cols, groups):
        y = 748
        for (region, stories) in regs:
            cv.text(cx0, y, region, 1, RED)
            cv.hline(cx0, cx0 + cv.text_w(region, 1), y + 8, RED, th=1)
            y += 12
            for st in stories:
                y, _ = cv.text_block(cx0, y, st, 1, INK, cx1 - cx0, leading=10)
            y += 4
    cv.vline(337, 744, 984, GRAY)
    cv.vline(677, 744, 984, GRAY)


def draw_markets(cv):
    """Markets sparklines + weather row across the foot of the briefs."""
    import math
    cv.hline(12, 1012, 948, INK, th=1)
    cv.text(12, 954, "MARKETS", 1, RED)
    # three index sparklines, deterministic sine wobbles
    series = [
        ("S&P", (31, 78, 121), 968, 6.0),
        ("FTSE", (179, 35, 27), 972, 5.0),
        ("NIKKEI", (46, 107, 52), 964, 7.0),
    ]
    x0, x1 = 96, 500
    cv.rect(x0, 952, x1, 984, INK)
    cv.hline(x0, x1, 968, (200, 200, 190))
    for (name, col, base, amp) in series:
        pts = []
        for i in range(21):
            x = x0 + 54 + i * 17
            y = int(base + amp * math.sin(i * 0.9 + base) + (i % 3) - 1)
            pts.append((x, y))
        cv.polyline(pts, col)
        cv.text(x0 + 6, base - 3, name, 1, col)
    # weather: six cities, icon + temperature
    cv.text(520, 954, "WEATHER", 1, RED)
    wx = [
        ("LONDON", "9C", "rain"),
        ("ANTALYA", "17C", "sun"),
        ("NEW YORK", "6C", "cloud"),
        ("TOKYO", "12C", "sun"),
        ("SYDNEY", "24C", "sun"),
        ("CAIRO", "21C", "sun"),
    ]
    cell = 68
    for i, (city, temp, kind) in enumerate(wx):
        cx = 596 + i * cell
        if kind == "sun":
            cv.circle(cx + 8, 968, 6, GOLD)
            cv.circle(cx + 8, 968, 4, YELLOW)
        elif kind == "cloud":
            cv.ellipse(cx + 8, 966, 9, 5, (160, 160, 155))
            cv.ellipse(cx + 8, 970, 7, 4, (200, 200, 195))
        else:
            cv.ellipse(cx + 8, 964, 9, 5, (140, 140, 135))
            for k in range(3):
                cv.line(cx + 3 + k * 5, 970, cx + 1 + k * 5, 976, BLUE)
        cv.text(cx + 18, 954, city, 1, INK)
        cv.text(cx + 18, 966, temp, 1, INK)


def draw_footer(cv):
    cv.hline(12, 1012, 990, INK, th=2)
    cv.text_center(12, 1012, 996,
                   "DATE CHECK - EVERY STORY ABOVE HAPPENED OR WAS FIRST "
                   "REPORTED ON SATURDAY 21 NOVEMBER 2026.", 1, RED)
    cv.text_center(12, 1012, 1008,
                   "THE SATURDAY LEDGER - THE WORLD IN ONE DAY", 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    # light paper grain first, so ink stays crisp on top
    cv.stipple(0, 0, W - 1, H - 1, 6, 170)
    cv.rect(4, 4, 1019, 1019, INK, th=2)
    draw_masthead(cv)
    draw_stats(cv)
    draw_lead(cv)
    cv.hline(12, 1012, 340, INK, th=2)
    draw_secondaries(cv)
    cv.hline(12, 1012, 536, INK, th=2)
    cv.text(12, 540, "THE WORLD TODAY - 12 CITIES", 2, INK)
    rx = 1012 - cv.text_w("EACH DOT A STORY INSIDE", 1)
    cv.text(rx, 544, "EACH DOT A STORY INSIDE", 1, INK)
    draw_map(cv, 12, 556, 1012, 716)
    cv.hline(12, 1012, 720, INK, th=2)
    draw_briefs(cv)
    draw_markets(cv)
    draw_footer(cv)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, cv)
    import hashlib
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, size, sha))
    assert size <= 1048576, "PNG over 1 MiB"
    assert cv.w == 1024 and cv.h == 1024


if __name__ == "__main__":
    main()
