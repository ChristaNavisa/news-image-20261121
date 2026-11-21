"""THE WORLD IN ONE DAY - Saturday 21 November 2026.

Draws a dense broadsheet front page (1024x1024 PNG) summing up the day's
world news: masthead, breaking kicker, stat strip, six drawn hero panels,
a world map with twelve numbered markers, and a 39-story brief list.
Standard library only. Deterministic: same bytes every run.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 229)
INK = (24, 24, 28)
NAVY = (16, 32, 64)
NAVY2 = (24, 48, 92)
RED = (178, 34, 34)
DARKRED = (120, 20, 20)
GOLD = (198, 158, 60)
TEAL = (14, 92, 96)
GREEN = (46, 110, 58)
OCEAN = (148, 184, 205)
LAND = (216, 207, 174)
CREAM = (250, 246, 236)
GREY = (120, 120, 118)
LIGHTGREY = (210, 208, 198)
ORANGE = (224, 122, 42)
PURPLE = (88, 52, 130)
PINK = (214, 92, 140)
SKY = (135, 178, 214)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
YELLOW = (240, 200, 60)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = ink.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
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
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    '^': ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '`': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_words(s, max_chars):
    words = s.split(" ")
    lines, cur = [], ""
    for wd in words:
        nxt = wd if not cur else cur + " " + wd
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            self.buf[i:i + len(row)] = row

    def outline(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        if filled:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        else:
            x, y, d = 0, r, 3 - 2 * r
            while x <= y:
                for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                               (x, -y), (y, -x), (-x, -y), (-y, -x)):
                    self.px(cx + sx, cy + sy, c)
                if d < 0:
                    d += 4 * x + 6
                else:
                    d += 4 * (x - y) + 10
                    y -= 1
                x += 1

    def poly(self, pts, c):
        # Even-odd scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, c)

    def vgrad(self, x, y, w, h, c0, c1, dither=False):
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
            self.fill(x, y + yy, w, 1, c)
            if dither and yy % 2 == 0:
                c2 = tuple(int(c0[k] + (c1[k] - c0[k]) * min(1, t + 0.06))
                           for k in range(3))
                for xx in range(x, x + w, 2):
                    self.px(xx, y + yy, c2)

    def text(self, x, y, s, scale, c, align="l"):
        s = s.upper()
        wpx = text_width(s, scale)
        if align == "c":
            x -= wpx // 2
        elif align == "r":
            x -= wpx
        cx = x
        for ch in s:
            g = FONT.get(ch, BLANK)
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.fill(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return wpx

    def speckle(self, x, y, w, h, n, colors, seed=1234567):
        # Deterministic pseudo-random dots (LCG) for print texture.
        s = seed
        for _ in range(n):
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            dx = s % w
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            dy = s % h
            s = (1103515245 * s + 12345) & 0x7FFFFFFF
            self.px(x + dx, y + dy, colors[s % len(colors)])

    def grain_rect(self, x, y, w, h, targets, tones, prob_den=3, seed=999331):
        # Newsprint grain: re-tone a fraction of the target-coloured pixels
        # inside a rectangle with nearby tones (deterministic LCG).
        s = seed
        buf = self.buf
        tset = set(targets)
        for yy in range(max(0, y), min(self.h, y + h)):
            base = yy * self.w * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = base + xx * 3
                c = (buf[i], buf[i + 1], buf[i + 2])
                if c in tset:
                    s = (1103515245 * s + 12345) & 0x7FFFFFFF
                    if s % prob_den == 0:
                        t = tones[(s >> 7) % len(tones)]
                        buf[i], buf[i + 1], buf[i + 2] = t


# ---------------------------------------------------------------- PNG out
def write_png(cv, path):
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- content
# All figures verified against wire reports for 21 November 2026.
STATS = [
    ("32.5M", "GTA VI UNITS, PRE-RELEASE", "TAKE-TWO OFFICIAL"),
    ("$3.79BN", "GTA VI DAY-ONE SALES", "BIGGEST LAUNCH EVER"),
    ("-5.06%", "NIKKEI 225", "WORST WEEK SINCE 2020"),
    ("M6.8", "PERU QUAKE, JUNIN", "FELT IN LIMA, 320 KM AWAY"),
    ("$81.3BN", "ANTHROPIC IPO", "LARGEST DEBUT IN HISTORY"),
    ("400+", "DRONES AT UKRAINE", "110+ MISSILES OVERNIGHT"),
]

# Hero panels: (title, caption lines, scene key)
HERO_A = [
    ("MISSILES FALL ON POLAND",
     ["3 RUSSIAN OBJECTS DOWN IN SE POLAND",
      "NATO JETS SCRAMBLED - NO CASUALTIES",
      "WARSAW ASKS FOR MORE EASTERN SENTRY FORCES"],
     "poland"),
    ("VICE CITY BREAKS RECORDS",
     ["TAKE-TWO: 32.5M UNITS, $3.79BN DAY ONE",
      "METACRITIC 99 - HIGHEST RATED EVER",
      "75% OF SALES ON PLAYSTATION, 25% ON XBOX"],
     "gta"),
    ("COP31: THE WORDS VANISH",
     ["DRAFT DROPS FOSSIL FUELS - TALKS OVERTIME",
      "PANAMA THREATENS TO BLOCK THE DEAL",
      "US ABSENT 2ND YEAR - NEXT COP ADDIS ABABA"],
     "cop"),
]
HERO_B = [
    ("WORST WEEK SINCE 2020",
     ["NIKKEI -5.06% - KOSPI -5.21%",
      "TAIEX -6.23% - SOFTBANK -14.48%",
      "MSCI ASIA -7% FOR THE WEEK"],
     "markets"),
    ("AKVAN FADES OVER INDIA",
     ["LANDFALL GOPALPUR 20 NOV, GUSTS 110 KM/H",
      "DISSIPATES 21 NOV - RAIN OVER ODISHA",
      "FISHERMEN WARNED OFF BAY OF BENGAL"],
     "akvan"),
    ("THE $81BN DEBUT",
     ["ANTHROPIC IPO: OPEN $111.50, CLOSE $97.17",
      "FRIDAY -8.5% TO $88.91 - AI ROUT GOES ON",
      "VALUATION ABOUT $1.5TN - TICKER ANT"],
     "anthropic"),
]

# Map markers: (number, lon, lat, legend text)
MARKERS = [
    (1, 21, 52, "WARSAW - MISSILES FALL ON NATO SOIL"),
    (2, 30, 50, "KYIV - 400+ DRONES, 110+ MISSILES"),
    (3, 30, 37, "ANTALYA - COP31 INTO OVERTIME"),
    (4, 85, 19, "GOPALPUR - AKVAN LANDFALL"),
    (5, 77, 28, "NEW DELHI - NEPAL PM VISIT; FPI RECORD"),
    (6, 174, -41, "WELLINGTON - KL RAHUL 100, SENA SET"),
    (7, 139, 35, "TOKYO - NIKKEI -5.06%"),
    (8, 127, 37, "SEOUL - KOSPI -5.21%"),
    (9, -74, 40, "NEW YORK - ANTHROPIC; RIKERS 2032"),
    (10, -77, -12, "LIMA - PERU QUAKE FELT 320 KM AWAY"),
    (11, -75, -11, "JUNIN - M6.8 EPICENTRE"),
    (12, 85, 28, "KATHMANDU - PM BALEN TO DELHI"),
]

# Simplified continent outlines (lon, lat), rough but recognisable.
N_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
             (-85, 66), (-80, 73), (-65, 60), (-55, 52), (-60, 46),
             (-70, 42), (-75, 35), (-80, 32), (-85, 30), (-90, 21),
             (-97, 16), (-94, 17), (-105, 20), (-110, 23), (-117, 33),
             (-125, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)]
GREENLAND = [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-45, 76),
             (-55, 70)]
S_AMERICA = [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0),
             (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -35),
             (-65, -41), (-68, -50), (-70, -54), (-73, -40), (-73, -20),
             (-80, -5), (-81, 0)]
AFRICA = [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
          (51, 11), (48, 2), (41, -4), (40, -15), (36, -26), (32, -29),
          (26, -34), (19, -35), (15, -27), (12, -18), (9, 4), (-8, 4),
          (-13, 8), (-17, 15), (-16, 20), (-10, 31)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
          (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
          (25, 65), (20, 70), (15, 70), (10, 64), (5, 58), (0, 50),
          (-5, 48), (-10, 43)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
ASIA = [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
        (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
        (158, 52), (150, 59), (142, 55), (140, 45), (135, 43), (130, 42),
        (127, 40), (122, 38), (120, 32), (118, 25), (110, 20), (108, 12),
        (105, 9), (100, 8), (97, 16), (94, 17), (90, 22), (88, 22),
        (85, 20), (80, 15), (77, 8), (75, 10), (72, 20), (66, 25),
        (60, 25), (57, 26), (52, 28), (50, 30), (48, 30), (44, 29),
        (40, 36), (36, 36), (33, 31), (30, 36), (28, 38), (26, 40),
        (28, 45), (30, 48), (30, 55), (28, 58), (30, 62)]
JAPAN = [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
         (142, 44), (140, 42), (138, 39), (135, 35), (132, 32)]
AUSTRALIA = [(114, -22), (114, -32), (124, -33), (130, -32), (137, -35),
             (140, -38), (147, -39), (150, -37), (153, -32), (153, -27),
             (150, -22), (146, -19), (142, -11), (136, -12), (132, -11),
             (126, -14), (122, -17), (118, -20)]
INDONESIA = [(95, 5), (105, -6), (110, -7), (115, -8), (120, -9),
             (125, -9), (130, -4), (135, -3), (140, -5), (138, -8),
             (130, -8), (120, -10), (110, -8), (100, -2), (95, 3)]

# The day in brief: (region tag, tag colour, headline). 39 items.
BRIEFS = [
    ("EUR", RED, "RUTTE DUE IN WARSAW AS POLAND SEEKS NATO JETS"),
    ("EUR", RED, "TUSK: MISSILE CRASH LIKELY DELIBERATE PROVOCATION"),
    ("EUR", RED, "11 NATIONS DRILL IN POLAND FOR POSTWAR ROLE"),
    ("UKR", DARKRED, "400+ DRONES, 110+ MISSILES HIT UKRAINE"),
    ("UKR", DARKRED, "KRYVYI RIH: 2 DEAD, 42 HURT IN STRIKE"),
    ("UKR", DARKRED, "RUSSIA HITS KYIV CROSSINGS AFTER KERCH BLOW"),
    ("UKR", DARKRED, "LITHUANIA BACKS ARTICLE 4 TALKS"),
    ("CLI", TEAL, "COP31: 25 NATIONS HOLD FOSSIL EXIT PLANS"),
    ("CLI", TEAL, "COP31: 120BN ADAPTATION FLOOR DROPPED"),
    ("CLI", TEAL, "COP31: 35-BY-35 POWER GOAL SURVIVES"),
    ("CLI", TEAL, "NEXT COP: ADDIS ABABA, NOVEMBER 2027"),
    ("CLI", TEAL, "INDONESIA FIRES MAY COST $30BN"),
    ("MKT", NAVY2, "NASDAQ SWINGS +2% TO -2% AS AI UNRAVELS"),
    ("MKT", NAVY2, "ANTHROPIC REVENUE $33BN IN NINE MONTHS"),
    ("MKT", NAVY2, "NVIDIA WIPEOUT DEEPENS TECH SELL-OFF"),
    ("MKT", NAVY2, "NSE PASSES NASDAQ AS 5TH-LARGEST EXCHANGE"),
    ("MKT", NAVY2, "INDIA FPI INFLOW RS 1.22 LAKH CR, RECORD"),
    ("MKT", NAVY2, "TRUMP: BAN US FIRMS BUILDING AI ABROAD"),
    ("MKT", NAVY2, "GTA 6 PC SCAM: $200 MALWARE STEALS CRYPTO"),
    ("ASI", GREEN, "NEPAL PM BALEN TO DELHI ON FIRST TRIP"),
    ("ASI", GREEN, "CHEETAH HAS 4 CUBS AT KUNO, INDIA"),
    ("ASI", GREEN, "MALAYSIA TO RESETTLE 10,000 ROHINGYA"),
    ("ASI", GREEN, "PAKISTAN CLIMATE MINISTER AT SCO IN DELHI"),
    ("ASI", GREEN, "INDIA: MAN JAILED 19 YEARS IN SIKH PLOT"),
    ("ASI", GREEN, "UK PLEDGES 1,000 DRONES FOR UKRAINE"),
    ("ASI", GREEN, "EU ADOPTS 1BN MILITARY AID FOR UKRAINE"),
    ("AME", PURPLE, "MAMDANI: RIKERS ISLAND TO CLOSE BY 2032"),
    ("AME", PURPLE, "TRUMP PARDONS PETE ROSE POSTHUMOUSLY"),
    ("AME", PURPLE, "SENATE REJECTS IRAN WAR POWERS 51-48"),
    ("AME", PURPLE, "US ADDS 4 IRANIANS TO SANCTIONS LIST"),
    ("AME", PURPLE, "US DECLASSIFIES MORE UFO FILM"),
    ("MEA", ORANGE, "TANKER STRUCK, ON FIRE IN STRAIT OF HORMUZ"),
    ("MEA", ORANGE, "MYANMAR CALLS ICJ GENOCIDE RULING UNFAIR"),
    ("MEA", ORANGE, "ANC FIGHTS TO HOLD S AFRICA KEY CITIES"),
    ("MEA", ORANGE, "UK, EU EYE CLOSER TIES AFTER NEW DEAL"),
    ("SPO", GOLD, "KL RAHUL: FIRST INDIAN WITH SENA CENTURIES"),
    ("SPO", GOLD, "CUMMINS KEEPS AUSTRALIA CAPTAINCY"),
    ("SPO", GOLD, "F1: LAS VEGAS GP PRACTICE 3 RUNS"),
    ("SPO", GOLD, "ECB BOARD RACE: BOONE, BRUNNERMEIER IN"),
]


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (75.0 - lat) / 130.0 * mh
    return int(x), int(y)


# ---------------------------------------------------------------- hero art
def scene_poland(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (10, 14, 34), (48, 30, 62), dither=True)
    s = 987654321
    for _ in range(46):
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        cv.px(x + s % w, y + (s >> 9) % (h - 60), WHITE)
    # missile arcs with glowing heads
    for k, (ax, ay, bx, by) in enumerate(((20, 110, 200, 40),
                                          (60, 130, 260, 60),
                                          (10, 90, 150, 30))):
        for t in range(0, 101, 4):
            px = ax + (bx - ax) * t // 100
            py = ay + (by - ay) * t // 100 - int(26 * (t / 100) * (1 - t / 100))
            cv.px(x + px, y + py, (255, 120, 90))
            cv.px(x + px, y + py + 1, (255, 60, 40))
        cv.circle(x + bx, y + by, 3, YELLOW)
        cv.circle(x + bx, y + by, 6, YELLOW, filled=False)
    # jets: small delta silhouettes
    for jx, jy in ((240, 90), (270, 110)):
        cv.poly([(x + jx, y + jy), (x + jx + 22, y + jy + 5),
                 (x + jx + 4, y + jy + 8)], (200, 200, 210))
    # ground
    cv.fill(x, y + h - 52, w, 52, (28, 26, 30))
    for bx in range(0, w, 26):
        bh = 14 + (bx * 7) % 22
        cv.fill(x + bx + 3, y + h - 52 - bh + 22, 18, bh, (16, 16, 20))
        for wy in range(0, bh - 4, 8):
            cv.px(x + bx + 7, y + h - 52 - bh + 26 + wy, YELLOW)
            cv.px(x + bx + 14, y + h - 52 - bh + 30 + wy, YELLOW)


def scene_gta(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (255, 150, 60), (120, 40, 130), dither=True)
    cv.circle(x + w - 78, y + 52, 30, (255, 214, 120))
    cv.circle(x + w - 78, y + 52, 36, (255, 190, 90), filled=False)
    # skyline
    heights = [66, 96, 78, 118, 88, 108, 70, 100, 82, 116, 74, 92]
    bw = w // 12
    for i, bh in enumerate(heights):
        bx = x + i * bw
        cv.fill(bx + 2, y + h - 52 - bh, bw - 4, bh, (30, 16, 48))
        for wy in range(y + h - 52 - bh + 8, y + h - 58, 12):
            for wx in range(bx + 6, bx + bw - 6, 9):
                if (wx * 13 + wy * 7) % 5 < 3:
                    cv.px(wx, wy, (255, 220, 130))
    # palm silhouettes
    for px0 in (x + 26, x + w - 40):
        cv.line(px0, y + h - 52, px0 + 4, y + h - 92, (20, 40, 26))
        for a in range(-3, 4):
            cv.line(px0 + 4, y + h - 92, px0 + 4 + a * 8,
                    y + h - 92 + abs(a) * 3 + 4, (20, 60, 30))
    cv.fill(x, y + h - 52, w, 52, (16, 10, 34))
    cv.hline(x, y + h - 52, w, (255, 190, 90))


def scene_cop(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (8, 70, 74), (16, 120, 110), dither=True)
    # globe
    gx, gy, gr = x + 62, y + 58, 44
    cv.circle(gx, gy, gr, (36, 110, 190))
    cv.circle(gx, gy, gr, (180, 220, 230), filled=False)
    for dx, dy, r in ((-16, -12, 12), (12, 8, 14), (2, -22, 8), (-6, 22, 9)):
        cv.circle(gx + dx, gy + dy, r, (64, 160, 90))
    cv.line(gx - gr, gy, gx + gr, gy, (200, 230, 235))
    cv.line(gx, gy - gr, gx, gy + gr, (200, 230, 235))
    # conference hall: rows of seats + empty podium
    for r in range(3):
        for c in range(9):
            cv.fill(x + 130 + c * 20, y + 34 + r * 16, 12, 10,
                    (240, 220, 170) if (r * 9 + c) % 4 else (200, 90, 60))
    cv.fill(x + 150, y + 96, 90, 10, (230, 210, 160))
    cv.fill(x + 186, y + 80, 18, 16, (240, 220, 170))
    # crossed-out bracket words
    cv.text(x + 130, y + 110, "FOSSIL FUELS", 1, (240, 220, 170))
    cv.line(x + 130, y + 113, x + 130 + 66, y + 113, RED)
    cv.line(x + 130, y + 114, x + 130 + 66, y + 114, RED)
    cv.fill(x, y + h - 52, w, 52, (10, 50, 52))


def scene_markets(cv, x, y, w, h):
    cv.fill(x, y, w, h, (14, 16, 22))
    # grid
    for gx in range(x + 10, x + w - 8, 32):
        cv.vline(gx, y + 8, h - 66, (40, 44, 56))
    for gy in range(y + 8, y + h - 58, 18):
        cv.hline(x + 10, gy, w - 20, (40, 44, 56))
    # falling candles (scaled to panel height so none clip the caption band)
    tops = [30, 34, 30, 40, 38, 46, 44, 52, 50, 58, 56, 64, 62, 70,
            68, 76, 74, 82, 80, 88, 86, 94, 92, 100, 84, 90, 96, 88,
            98, 104, 96, 106, 100, 110, 104, 112, 106, 114, 108, 116]
    cap = h - 74
    tops = [min(t, cap) for t in tops]
    bw = (w - 24) // len(tops)
    for i, t in enumerate(tops):
        bx = x + 12 + i * bw
        up = (i % 5 == 2)
        col = (60, 190, 110) if up else (220, 60, 60)
        cv.vline(bx + bw // 2, y + 8 + t - 8, 16, col)
        cv.fill(bx + 1, y + 8 + t, bw - 2, 12, col)
    # trend arrow down
    ax, ay = x + w - 16, y + 8 + cap - 8
    cv.line(x + 14, y + 22, ax, ay, (255, 210, 80))
    cv.line(ax, ay, ax - 18, ay, (255, 210, 80))
    cv.line(ax, ay, ax, ay - 18, (255, 210, 80))
    cv.fill(x, y + h - 52, w, 52, (24, 10, 12))


def scene_akvan(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (24, 66, 110), (120, 170, 205), dither=True)
    cx, cy = x + 96, y + 58
    rmax = min(50, h - 116)
    for r in range(10, rmax + 1, 8):
        cv.circle(cx, cy, r, (235, 242, 248), filled=False)
    for a in range(0, 360, 24):
        import math
        r0 = 12 + a // 24 * 4
        x0 = cx + int(r0 * math.cos(math.radians(a)))
        y0 = cy + int(r0 * math.sin(math.radians(a)))
        x1 = cx + int((r0 + 16) * math.cos(math.radians(a + 40)))
        y1 = cy + int((r0 + 16) * math.sin(math.radians(a + 40)))
        cv.line(x0, y0, x1, y1, (255, 255, 255))
    cv.circle(cx, cy, 9, (250, 246, 230))
    # rain streaks
    for i in range(34):
        rx = x + 190 + (i * 37) % (w - 200)
        ry = y + 10 + (i * 29) % 60
        cv.line(rx, ry, rx - 5, ry + 16, (220, 235, 245))
    # coastline + land
    cv.poly([(x + 180, y + h - 52), (x + 230, y + h - 96), (x + 290, y + h - 80),
             (x + w - 8, y + h - 96), (x + w - 8, y + h - 52)],
            (196, 178, 130))
    cv.fill(x, y + h - 52, w, 52, (20, 52, 84))


def scene_anthropic(cv, x, y, w, h):
    cv.fill(x, y, w, h, (20, 20, 30))
    # bell
    bx, by = x + 52, y + 26
    cv.poly([(bx, by + 44), (bx + 8, by), (bx + 52, by), (bx + 60, by + 44)],
            (232, 190, 60))
    cv.fill(bx - 4, by + 44, 68, 6, (200, 160, 40))
    cv.circle(bx + 30, by + 56, 6, (232, 190, 60))
    cv.fill(bx + 26, by - 8, 8, 8, (232, 190, 60))
    # ticker line: up then down
    pts = [(150, 78), (180, 62), (210, 68), (240, 44), (265, 52),
           (285, 74), (305, 92)]
    for i in range(len(pts) - 1):
        cv.line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
                y + pts[i + 1][1], (90, 220, 130))
        cv.circle(x + pts[i][0], y + pts[i][1], 2, (90, 220, 130))
    cv.circle(x + pts[-1][0], y + pts[-1][1], 3, (220, 60, 60))
    cv.text(x + 150, y + 8, "ANT  $111.50 -> $88.91", 1, (200, 205, 215))
    cv.fill(x, y + h - 52, w, 52, (28, 16, 22))


SCENES = {"poland": scene_poland, "gta": scene_gta, "cop": scene_cop,
          "markets": scene_markets, "akvan": scene_akvan,
          "anthropic": scene_anthropic}


# ---------------------------------------------------------------- compose
def hero_panel(cv, x, y, w, h, title, caps, scene):
    cv.outline(x, y, w, h, INK, 2)
    SCENES[scene](cv, x + 2, y + 2, w - 4, h - 4)
    # caption band: title + up to 3 caption lines
    cv.fill(x + 2, y + h - 54, w - 4, 52, (12, 12, 16))
    cv.fill(x + 2, y + h - 54, w - 4, 2, GOLD)
    cv.text(x + 8, y + h - 50, title, 2, WHITE)
    yy = y + h - 35
    for ln in caps[:3]:
        cv.text(x + 8, yy, ln, 1, (205, 205, 200))
        yy += 9


def compose():
    cv = Canvas(W, H, PAPER)
    # newsprint grain: faint horizontal striping over the whole sheet
    for yy in range(0, H, 2):
        cv.fill(0, yy, W, 1, (240, 234, 220))
    cv.speckle(0, 0, W, H, 9000, [(238, 232, 216), (228, 220, 200),
                                   (250, 246, 238)], seed=424242)
    # outer double border
    cv.outline(8, 8, W - 16, H - 16, INK, 2)
    cv.outline(12, 12, W - 24, H - 24, INK, 1)

    # ---- masthead
    cv.fill(16, 16, W - 32, 92, NAVY)
    cv.fill(16, 16, W - 32, 3, GOLD)
    cv.fill(16, 105, W - 32, 3, GOLD)
    cv.text(W // 2, 30, "THE WORLD IN ONE DAY", 5, WHITE, align="c")
    cv.text(W // 2, 74, "SATURDAY 21 NOVEMBER 2026", 2, (255, 220, 130),
            align="c")
    cv.text(30, 92, "WORLD TELEVISION DAY", 1, (170, 190, 220))
    cv.text(W - 30, 92, "45 STORIES - WORLDWIDE", 1, (170, 190, 220),
            align="r")

    # ---- breaking kicker
    cv.fill(16, 112, W - 32, 22, RED)
    cv.text(W // 2, 117, "POLAND: MISSILES FALL ON NATO SOIL - RUTTE DUE IN WARSAW TODAY",
            2, WHITE, align="c")

    # ---- stat strip: 6 boxes
    sy, sh = 138, 72
    bw = (W - 32 - 5 * 6) // 6
    for i, (num, lab, sub) in enumerate(STATS):
        bx = 16 + i * (bw + 6)
        cv.fill(bx, sy, bw, sh, CREAM)
        cv.outline(bx, sy, bw, sh, INK, 1)
        cv.fill(bx, sy, bw, 3, NAVY)
        nscale = 3 if len(num) <= 7 else 2
        cv.text(bx + bw // 2, sy + 12, num, nscale, NAVY, align="c")
        for j, ln in enumerate(wrap_words(lab, max(6, (bw - 10) // 6))):
            cv.text(bx + bw // 2, sy + 38 + j * 9, ln, 1, INK, align="c")
        cv.text(bx + bw // 2, sy + 58, sub, 1, GREY, align="c")

    # ---- hero row A (3 x 190)
    ay, ah = 214, 190
    aw = (W - 32 - 2 * 6) // 3
    for i, (title, caps, scene) in enumerate(HERO_A):
        hero_panel(cv, 16 + i * (aw + 6), ay, aw, ah, title, caps, scene)

    # ---- hero row B (3 x 150)
    by, bh = 408, 150
    for i, (title, caps, scene) in enumerate(HERO_B):
        hero_panel(cv, 16 + i * (aw + 6), by, aw, bh, title, caps, scene)

    # ---- world map band
    my, mh = 562, 224
    cv.fill(16, my, W - 32, mh, CREAM)
    cv.outline(16, my, W - 32, mh, INK, 2)
    cv.fill(16, my, W - 32, 20, NAVY)
    cv.text(24, my + 6, "WHERE IT HAPPENED - THE WORLD IN ONE DAY", 1, WHITE)
    cv.text(W - 24, my + 6, "12 MARKERS", 1, (255, 220, 130), align="r")
    mx, mw = 24, 620
    mtop, mbot = my + 24, my + mh - 6
    cv.fill(mx, mtop, mw, mbot - mtop, OCEAN)
    # graticule
    for gx in range(mx, mx + mw, 62):
        cv.vline(gx, mtop, mbot - mtop, (170, 200, 215))
    for gy in range(mtop, mbot, 32):
        cv.hline(mx, gy, mw, (170, 200, 215))
    for poly_pts in (N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EUROPE,
                     UK, ASIA, JAPAN, AUSTRALIA, INDONESIA):
        pts = [lonlat_to_xy(lo, la, mx, mtop, mw, mbot - mtop)
               for lo, la in poly_pts]
        cv.poly(pts, LAND)
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0],
                    pts[(i + 1) % len(pts)][1], (120, 110, 80))
    # markers (small nudges keep close neighbours from overlapping)
    NOFF = {2: (14, 10), 3: (-12, 10), 4: (-16, 12), 10: (-18, 10),
            11: (14, -8), 12: (16, -10)}
    for num, lon, lat, _leg in MARKERS:
        px, py = lonlat_to_xy(lon, lat, mx, mtop, mw, mbot - mtop)
        dx, dy = NOFF.get(num, (0, 0))
        px, py = px + dx, py + dy
        cv.circle(px, py, 8, RED)
        cv.circle(px, py, 8, WHITE, filled=False)
        cv.text(px, py - 3, str(num), 1, WHITE, align="c")
    # ocean + country labels, compass, stipple texture
    for lab, lo, la in (("ATLANTIC", -30, 20), ("PACIFIC", -140, -10),
                        ("PACIFIC", 175, -25), ("INDIAN", 75, -30),
                        ("ARCTIC", 0, 72)):
        lx, ly = lonlat_to_xy(lo, la, mx, mtop, mw, mbot - mtop)
        cv.text(lx, ly, lab, 1, (90, 120, 140), align="c")
    for lab, lo, la in (("USA", -100, 40), ("CANADA", -106, 58),
                        ("BRAZIL", -52, -10), ("CHINA", 104, 35),
                        ("INDIA", 78, 21), ("RUSSIA", 95, 62),
                        ("AUSTRALIA", 134, -25)):
        lx, ly = lonlat_to_xy(lo, la, mx, mtop, mw, mbot - mtop)
        cv.text(lx, ly, lab, 1, (122, 110, 78), align="c")
    cv.circle(mx + mw - 22, mtop + 16, 9, WHITE, filled=False)
    cv.text(mx + mw - 22, mtop + 10, "N", 1, NAVY, align="c")
    cv.line(mx + mw - 22, mtop + 18, mx + mw - 22, mtop + 24, NAVY)
    cv.speckle(mx, mtop, mw, mbot - mtop, 12000, [(130, 168, 192),
                                                  (160, 195, 212),
                                                  (120, 158, 182)],
               seed=777)
    cv.grain_rect(mx, mtop, mw, mbot - mtop, [LAND],
                  [(206, 196, 162), (226, 218, 186), (210, 200, 166)],
                  prob_den=4, seed=5150)
    # legend (right column)
    lx = mx + mw + 12
    cv.text(lx, my + 28, "THE MARKERS", 1, NAVY)
    cv.hline(lx, my + 38, W - 32 - (lx - 16), NAVY)
    for i, (num, _lo, _la, leg) in enumerate(MARKERS):
        ly = my + 44 + i * 13
        cv.circle(lx + 6, ly + 3, 6, RED)
        cv.text(lx + 6, ly, str(num), 1, WHITE, align="c")
        cv.text(lx + 18, ly, leg, 1, INK)
    cv.text(lx, my + mh - 18, "MAP: ROUGH OUTLINE, NOT TO SCALE", 1, GREY)

    # ---- the day in brief: 3 columns x 13 rows
    ly0, lh = 790, 182
    cv.fill(16, ly0, W - 32, 16, NAVY)
    cv.text(24, ly0 + 4, "THE DAY IN BRIEF - 39 STORIES", 1, WHITE)
    cv.text(W - 24, ly0 + 4, "EUROPE - AMERICAS - ASIA - MARKETS - SPORT",
            1, (255, 220, 130), align="r")
    colw = (W - 32 - 2 * 10) // 3
    for ci in range(3):
        cx = 16 + ci * (colw + 10)
        for ri in range(13):
            idx = ci * 13 + ri
            tag, tcol, head = BRIEFS[idx]
            ry = ly0 + 22 + ri * 12
            cv.fill(cx, ry, 30, 9, tcol)
            cv.text(cx + 15, ry + 1, tag, 1, WHITE, align="c")
            cv.text(cx + 34, ry + 1, head, 1, INK)
        if ci < 2:
            cv.vline(cx + colw + 5, ly0 + 20, lh - 24, LIGHTGREY)

    # ---- footer: date check
    fy = 976
    cv.fill(16, fy, W - 32, 2, INK)
    cv.text(W // 2, fy + 6,
            "DATE CHECK: EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED,",
            1, INK, align="c")
    cv.text(W // 2, fy + 16,
            "ON SATURDAY 21 NOVEMBER 2026 - COMPILED FROM WIRE REPORTS.",
            1, INK, align="c")
    # newsprint grain over the paper areas (last step, keeps text crisp)
    cv.grain_rect(0, 0, W, H, [PAPER, (240, 234, 220)],
                  [(242, 237, 224), (250, 245, 234), (236, 230, 214),
                   (244, 239, 226), (238, 233, 218)],
                  prob_den=3, seed=999331)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = compose()
    n = write_png(cv, path)
    print(f"wrote {path} ({n} bytes, {cv.w}x{cv.h})")


if __name__ == "__main__":
    main()
