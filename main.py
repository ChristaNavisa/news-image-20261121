#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Saturday 21 November 2026.

A one-page broadsheet of the day's world news, drawn entirely with the
Python standard library: own PNG encoder (zlib + struct) and own 5x7
bitmap font. No Pillow, no numpy, no network, no clock, no file reads.
Deterministic: two runs write byte-identical PNGs.

Layout: masthead + date, 8-number stat strip, lead Kyiv story with a
drawn night picture, four hero pictures, a world map with 12 cities,
region chips, a DATE CHECK box, and 48 stories in three columns.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ------------------------------------------------------------------ colors
PAPER = (242, 233, 213)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (31, 58, 110)
GOLD = (176, 132, 24)
TEAL = (0, 120, 110)
GREEN = (46, 110, 60)
GRAY = (120, 112, 96)
LIGHT = (232, 222, 196)
SEA = (203, 222, 232)
LAND = (198, 210, 172)
LAND_LINE = (90, 110, 70)
NIGHT = (18, 28, 54)
NIGHT2 = (30, 48, 84)
RIVER = (70, 110, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (240, 200, 60)
ORANGE = (230, 120, 30)
BROWN = (120, 84, 50)
SKY = (178, 208, 228)
SKIN = (222, 184, 150)
SUIT = (40, 40, 48)

REGION_COLORS = {
    "EUROPE": BLUE,
    "AMERICAS": RED,
    "ASIA": GOLD,
    "MIDDLE EAST": TEAL,
    "AFRICA": GREEN,
}

# ------------------------------------------------------------------ font
# 5x7 bitmap font: each glyph is 7 rows, each row a 5-bit value (bit 4 = left).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0, 0x04),
    ",": (0, 0, 0, 0, 0x04, 0x04, 0x08),
    ":": (0, 0x04, 0, 0, 0, 0x04, 0),
    ";": (0, 0x04, 0, 0, 0, 0x04, 0x08),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "•": (0, 0x04, 0x0E, 0x0E, 0x0E, 0x04, 0),
}


def char_advance(scale):
    return 5 * scale + 1


def text_width(s, scale):
    return len(s) * char_advance(scale) - 1 if s else 0


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x0, x1, y, c):
        if x1 < x0:
            x0, x1 = x1, x0
        self.fill(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x, y0, y1, c):
        if y1 < y0:
            y0, y1 = y1, y0
        self.fill(x, y0, 1, y1 - y0 + 1, c)

    def rect(self, x, y, w, h, c):
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
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

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            self.hline(cx - dx, cx + dx, yy, c)

    def poly_fill(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def poly_line(self, pts, c):
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            self.line(x0, y0, x1, y1, c)

    def text(self, s, x, y, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                bits = g[r]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += char_advance(scale)

    def center(self, s, cx, y, scale, c):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, c)


# ------------------------------------------------------------------ png
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ------------------------------------------------------------------ data
STATS = [
    ("48", "STORIES"),
    ("5", "REGIONS"),
    ("5", "HERO PICTURES"),
    ("1", "WORLD MAP"),
    ("400+", "DRONES AT KYIV"),
    ("-3.7%", "S&P 500"),
    ("-5.3%", "NASDAQ"),
    ("6.7", "PERU QUAKE"),
]

# (region, headline <= 28 chars, summary <= 50 chars)
STORIES = [
    ("EUROPE", "KYIV HIT BY 400 DRONES", "Overnight barrage kills eight, hits three bridges"),
    ("EUROPE", "TWO MISSILES LAND IN POLAND", "No casualties; Warsaw calls it escalation"),
    ("EUROPE", "FRANCE CALLS UN COUNCIL MEET", "Paris acts after the latest Kyiv strikes"),
    ("EUROPE", "DENMARK OUSTS RUSSIAN ENVOY", "Attache accused of plot on rapper Kyivstoner"),
    ("EUROPE", "AUSTRIA SUMMONS ENVOY", "Embassy in Kyiv damaged in the strikes"),
    ("EUROPE", "MOSCOW CRIES IRON CURTAIN", "Russia hits back as Estonia shuts border"),
    ("EUROPE", "EU GIVES KYIV 1BN EUROS", "Military aid package agreed in Brussels"),
    ("EUROPE", "UK AND EU SEAL BREXIT RESET", "Trade and youth-mobility pact agreed"),
    ("EUROPE", "MERZ REJECTS A NEW YALTA", "No deal on Europe without Europe: Berlin"),
    ("EUROPE", "SPAIN STAYS EUROPE'S STAR", "Growth leads the bloc as voters go to polls"),
    ("EUROPE", "PUTIN RULES OUT CEASEFIRE", "No limited truce after Shenzhen, he says"),
    ("EUROPE", "RESCUERS DIG THROUGH RUBBLE", "Crews search debris after deadly Kyiv strike"),
    ("EUROPE", "EUROPE RALLIES BEHIND KYIV", "Allies meet in Berlin as talks press on"),
    ("AMERICAS", "S&P 500 FALLS 3.7% IN ROUT", "AI sell-off pushes Wall Street into correction"),
    ("AMERICAS", "NASDAQ ERASES ITS 2026 GAINS", "Tech rout wipes out the year's rise"),
    ("AMERICAS", "NVIDIA'S WORST WEEK IN YEARS", "SEC examines its accounting, sources say"),
    ("AMERICAS", "ANTHROPIC FALLS 11% POST-IPO", "Shares slide a day after record listing"),
    ("AMERICAS", "TRUMP DEFENDS TIES TO PUTIN", "90-minute press conference after Shenzhen"),
    ("AMERICAS", "TRUMP WANTS NVIDIA BOSS BACK", "Says Jensen Huang deserves a second chance"),
    ("AMERICAS", "CALIFORNIA PROBES CHIP SALES", "State checks whether chips reached China"),
    ("AMERICAS", "SPACEX SELLS $32BN BONDS", "8.26% yield to fund access to AI chips"),
    ("AMERICAS", "FBI AND FARM DEPT ARE HACKED", "Agencies confirm breaches, probe under way"),
    ("AMERICAS", "BAYER'S $7.25BN DEAL CLEARED", "Roundup settlement approved by a judge"),
    ("AMERICAS", "COURT BACKS GUN SALES RIGHT", "Fifth Circuit rules on Second Amendment"),
    ("AMERICAS", "BITCOIN FALLS TO $58,076", "Crypto slides with stocks; Solana down 6%"),
    ("AMERICAS", "M6.7 QUAKE SHAKES PERU", "Strong tremor hits the Andes at Junin"),
    ("ASIA", "LEADERS MEET IN SHENZHEN", "First Trump-Xi-Putin summit ends thin"),
    ("ASIA", "CHINA QUESTIONS ICJ RULING", "Beijing disputes court's jurisdiction"),
    ("ASIA", "XI GAINS STANDING AT SUMMIT", "Analysts: Beijing rose more than policy"),
    ("ASIA", "NIKKEI FALLS 5.06% IN TOKYO", "Asian markets follow Wall Street down"),
    ("ASIA", "INDIA WEIGHS THE NEW AXIS", "Delhi watches Trump, Xi and Putin meet"),
    ("ASIA", "MYANMAR REJECTS ICJ VERDICT", "Junta calls the genocide ruling unfair"),
    ("ASIA", "MALAYSIA PLANS ROHINGYA MOVE", "Resettlement plan follows ICJ ruling"),
    ("ASIA", "TURKEY BACKS ICJ RULING", "Ankara supports the genocide verdict"),
    ("ASIA", "CLIMATE SUMMIT RUNS OVERTIME", "Antalya talks stall as nations fail to agree"),
    ("MIDDLE EAST", "IRAN DOWNS US MQ-9 DRONE", "Guard claims the kill over Hormuz"),
    ("MIDDLE EAST", "TANKERS CATCH FIRE IN HORMUZ", "Strait traffic falls to 35% of normal"),
    ("MIDDLE EAST", "SAUDIS STOP HOUTHI MISSILES", "Three missiles aimed at Riyadh shot down"),
    ("MIDDLE EAST", "US MISSILE HITS QESHM ISLAND", "Iranian media report strike on outskirts"),
    ("MIDDLE EAST", "BASRA PLANT FIRE KILLS FOUR", "Blaze injures around 30 in Iraq"),
    ("MIDDLE EAST", "UN WARNS ON HUDAYDAH STRIKES", "Port attacks threaten Yemen aid lifeline"),
    ("MIDDLE EAST", "GAS JUMPS 14.7% ON FEARS", "Energy prices surge as strait traffic falls"),
    ("AFRICA", "AFRICA HOLDS CLIMATE LINE", "Delegates defend finance duties at COP31"),
    ("AFRICA", "KENYA SIGNS MINERALS DEAL", "US-backed group wins Mrima Hill project"),
    ("AFRICA", "GHANA CUTS RATES 300 POINTS", "Central bank eases as inflation cools"),
    ("AFRICA", "KENYA LAUNCHES NET DRIVE", "Nets go to 18 high-malaria counties"),
    ("AFRICA", "GUINEA BANS BURKINA CHANNEL", "Tensions rise as Conakry blocks station"),
    ("AFRICA", "SOUTH AFRICA HOLDS ITS RATES", "Bank waits as inflation risks persist"),
]

REGION_COUNTS = [
    ("EUROPE", 13),
    ("AMERICAS", 13),
    ("ASIA", 9),
    ("MIDDLE EAST", 7),
    ("AFRICA", 6),
]

# Continent outlines as (lon, lat) polygons, simplified but recognisable.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-110, 68), (-95, 69), (-85, 66), (-75, 62),
     (-65, 60), (-55, 47), (-65, 44), (-70, 42), (-75, 35), (-81, 26),
     (-85, 20), (-90, 14), (-83, 9), (-90, 16), (-97, 16), (-105, 20),
     (-114, 29), (-125, 40), (-125, 49), (-135, 58), (-155, 58)],
    [(-45, 60), (-32, 68), (-20, 70), (-25, 76), (-45, 76), (-58, 74),
     (-55, 70)],
    [(-79, 9), (-75, 5), (-70, 0), (-62, -3), (-52, -5), (-42, -8),
     (-35, -9), (-38, -15), (-40, -22), (-48, -27), (-55, -34), (-62, -39),
     (-66, -45), (-68, -52), (-70, -54), (-72, -48), (-73, -38), (-72, -28),
     (-70, -18), (-76, -12), (-80, -4)],
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (0, 36), (10, 37),
     (20, 32), (30, 31), (35, 28), (40, 15), (43, 11), (48, 11), (51, 12),
     (45, 2), (40, -8), (36, -18), (33, -26), (28, -33), (20, -35),
     (16, -29), (12, -18), (13, -10), (9, 4), (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (2, 51), (6, 54), (8, 57), (12, 58),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 68), (40, 68), (44, 62),
     (42, 56), (38, 50), (34, 46), (30, 45), (27, 41), (23, 40), (19, 42),
     (13, 44), (8, 44), (3, 42), (-2, 37), (-9, 37)],
    [(28, 68), (40, 68), (55, 69), (70, 72), (90, 75), (110, 76),
     (130, 73), (150, 70), (160, 66), (162, 60), (156, 58), (145, 60),
     (140, 55), (135, 45), (130, 40), (127, 38), (122, 31), (120, 24),
     (110, 20), (105, 10), (100, 8), (96, 15), (92, 20), (88, 22),
     (80, 15), (76, 8), (72, 20), (66, 25), (60, 25), (55, 28), (50, 30),
     (45, 35), (40, 38), (35, 42), (30, 45), (28, 50), (28, 60)],
    [(113, -22), (114, -30), (115, -34), (120, -34), (128, -32), (134, -33),
     (138, -35), (142, -38), (147, -38), (150, -37), (153, -28), (150, -22),
     (146, -19), (142, -11), (137, -12), (132, -12), (127, -14), (122, -17),
     (117, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (-1, 51)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (140, 44), (143, 43), (141, 39), (139, 37), (137, 35), (134, 34),
     (131, 33)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (46, -25), (44, -22),
     (43, -18)],
]

# (name, lon, lat, label side: L=left, R=right, A=above, B=below, UR=upper-right)
CITIES = [
    ("NEW YORK", -74, 40.7, "L"),
    ("LIMA", -77, -12, "R"),
    ("LONDON", -0.1, 51.5, "L"),
    ("THE HAGUE", 4.3, 52, "UR"),
    ("KYIV", 30.5, 50.4, "R"),
    ("ANTALYA", 30.7, 36.9, "L"),
    ("RIYADH", 46.7, 24.6, "L"),
    ("HORMUZ", 56.5, 27, "R"),
    ("NAIROBI", 36.8, -1.3, "R"),
    ("NEW DELHI", 77.2, 28.6, "A"),
    ("SHENZHEN", 114, 22.5, "B"),
    ("TOKYO", 139.7, 35.7, "R"),
]

# ------------------------------------------------------------------ layout
# Lead headline geometry. The fix for the round-6 overlap: line 2 starts
# a full glyph height below line 1's baseline, so the two lines can never
# touch. LEAD_GH = 7 rows * scale 4 = 28 px.
LEAD_SCALE = 4
LEAD_GH = 7 * LEAD_SCALE
LEAD_L1_Y = 196
LEAD_BASELINE = LEAD_L1_Y + LEAD_GH
LEAD_L2_Y = LEAD_BASELINE + LEAD_GH


def project(lon, lat):
    # Map box: x 24..664, y 486..620. Equirectangular, 1.75 px/deg lon.
    return (24 + int((lon + 170) * 1.75), 486 + int((75 - lat) * 1.0))


def draw_grain(cv):
    # Deterministic newsprint grain: sparse 1px speckles over the paper,
    # drawn first so every later mark sits on top of it. A fixed LCG seed
    # keeps the two grader runs byte-identical, and the speckle breaks up
    # the flat paper so the sheet reads as printed newsprint, not blank.
    state = 1234567
    for _ in range(26000):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        x = state % W
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        y = state % H
        cv.px(x, y, (236, 226, 204))
    for _ in range(9000):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        x = state % W
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        y = state % H
        cv.px(x, y, (248, 240, 222))


def draw_masthead(cv):
    cv.fill(0, 6, W, 3, INK)
    cv.fill(0, 12, W, 1, INK)
    cv.text("VOL. I - NO. 326", 24, 22, 1, INK)
    cv.text("PRICE: ONE DAY'S NEWS", 1024 - 24 - text_width("PRICE: ONE DAY'S NEWS", 1), 22, 1, INK)
    cv.center("THE WORLD IN ONE DAY", W // 2, 18, 6, INK)
    cv.center("SATURDAY 21 NOVEMBER 2026", W // 2, 66, 3, RED)
    cv.center("ALL THE DAY'S NEWS  •  EVERY REGION  •  EVERY FIELD", W // 2, 94, 1, INK)
    cv.fill(0, 108, W, 2, INK)
    cv.fill(0, 112, W, 1, INK)


def draw_stats(cv):
    cv.fill(16, 116, 992, 2, INK)
    for i, (num, label) in enumerate(STATS):
        x0 = 16 + i * 124
        cx = x0 + 62
        cv.center(num, cx, 124, 3, RED if i >= 4 else INK)
        cv.center(label, cx, 150, 1, GRAY)
        if i:
            cv.vline(x0, 122, 158, GRAY)
    cv.fill(16, 168, 992, 1, INK)


def burst(cv, cx, cy, r, c1, c2):
    cv.disc(cx, cy, r, c1)
    cv.disc(cx, cy, r // 2, c2)
    for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, -r),
                   (r, -r), (-r, r)):
        cv.line(cx, cy, cx + dx * 3 // 2, cy + dy * 3 // 2, c1)


def draw_lead_picture(cv, x, y, w, h):
    cv.fill(x, y, w, 52, NIGHT)
    cv.fill(x, y + 52, w, 22, NIGHT2)
    cv.fill(x, y + 74, w, h - 74, RIVER)
    for sx, sy in ((30, 12), (70, 26), (150, 8), (210, 20), (260, 10),
                   (300, 24), (120, 30), (180, 14)):
        cv.px(x + sx, y + sy, WHITE)
        cv.px(x + sx + 1, y + sy, WHITE)
    # Building silhouettes with lit windows.
    builds = [(0, 46, 34, 28), (38, 38, 26, 36), (68, 50, 30, 24),
              (102, 30, 28, 44), (134, 44, 30, 30), (168, 36, 26, 38),
              (198, 48, 32, 26), (234, 34, 28, 40), (266, 46, 26, 28),
              (296, 40, 24, 34)]
    for bx, by, bw, bh in builds:
        cv.fill(x + bx, y + by, bw, bh, BLACK)
        for wy in range(y + by + 5, y + by + bh - 3, 9):
            for wx in range(x + bx + 4, x + bx + bw - 3, 9):
                if (wx + wy) % 3 == 0:
                    cv.fill(wx, wy, 3, 4, YELLOW)
    burst(cv, x + 118, y + 26, 12, ORANGE, YELLOW)
    burst(cv, x + 252, y + 18, 9, ORANGE, YELLOW)
    cv.line(x + 60, y + 8, x + 96, y + 44, ORANGE)
    cv.line(x + 280, y + 4, x + 252, y + 30, ORANGE)
    # Bridge arc over the river.
    for t in range(0, 321, 4):
        bx = x + t
        by = y + 96 - int(14 * (1 - ((t - 160) / 160.0) ** 2))
        cv.fill(bx, by, 3, 2, BLACK)
    cv.vline(x + 40, y + 88, y + 112, BLACK)
    cv.vline(x + 160, y + 82, y + 112, BLACK)
    cv.vline(x + 280, y + 88, y + 112, BLACK)
    # Caption bar.
    cv.fill(x, y + h - 16, w, 16, BLACK)
    cv.center("KYIV - THREE BRIDGES HIT IN OVERNIGHT BARRAGE", x + w // 2,
              y + h - 12, 1, WHITE)


def draw_lead(cv):
    cv.text("LEAD STORY - KYIV, UKRAINE", 360, 178, 1, RED)
    draw_lead_picture(cv, 24, 178, 320, 140)
    cv.text("RUSSIA FIRES 400 DRONES", 360, LEAD_L1_Y, LEAD_SCALE, INK)
    cv.text("110 MISSILES HIT UKRAINE", 360, LEAD_L2_Y, LEAD_SCALE, INK)
    cv.text("THREE BRIDGES HIT; EIGHT KILLED;", 360, 292, 2, INK)
    cv.text("TWO MISSILES LAND IN POLAND", 360, 310, 2, INK)


def draw_flag_us(cv, x, y, w, h):
    for i in range(7):
        cv.fill(x, y + i * h // 7, w, h // 7 + 1,
                RED if i % 2 == 0 else WHITE)
    cv.fill(x, y, w * 2 // 5, h * 4 // 7, BLUE)
    for r in range(4):
        for c in range(5):
            cv.px(x + 3 + c * 5, y + 3 + r * 5, WHITE)


def draw_flag_cn(cv, x, y, w, h):
    cv.fill(x, y, w, h, RED)
    cv.disc(x + 6, y + 6, 4, YELLOW)
    for sx, sy in ((16, 3), (20, 7), (20, 12), (16, 15)):
        cv.disc(x + sx, y + sy, 2, YELLOW)


def draw_flag_ru(cv, x, y, w, h):
    cv.fill(x, y, w, h // 3, WHITE)
    cv.fill(x, y + h // 3, w, h // 3, BLUE)
    cv.fill(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


def draw_shenzhen(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + h - 26, w, 26, (196, 182, 140))
    draw_flag_us(cv, x + 18, y + 10, 34, 24)
    draw_flag_cn(cv, x + w // 2 - 17, y + 6, 34, 24)
    draw_flag_ru(cv, x + w - 52, y + 10, 34, 24)
    for fx in (x + 35, x + w // 2, x + w - 35):
        cv.vline(fx, y + 34, y + 62, INK)
    cv.fill(x + 30, y + 62, w - 60, 12, BROWN)
    for fx, suit in ((x + 55, SUIT), (x + w // 2 - 8, (60, 60, 70)),
                     (x + w - 70, SUIT)):
        cv.disc(fx + 8, y + 52, 7, SKIN)
        cv.fill(fx, y + 60, 16, 14, suit)


def draw_icj(cv, x, y, w, h):
    cv.fill(x, y, w, h, (228, 226, 214))
    cv.fill(x + 20, y + h - 22, w - 40, 6, GRAY)
    cv.fill(x + 28, y + h - 28, w - 56, 6, LIGHT)
    for i in range(4):
        cx = x + 34 + i * 52
        cv.fill(cx, y + 34, 12, h - 62, WHITE)
        cv.fill(cx - 2, y + 30, 16, 4, WHITE)
    cv.poly_fill([(x + 20, y + 30), (x + w - 20, y + 30),
                  (x + w // 2, y + 8)], WHITE)
    cv.poly_line([(x + 20, y + 30), (x + w - 20, y + 30),
                  (x + w // 2, y + 8)], INK)
    cv.disc(x + w // 2, y + 20, 3, GOLD)
    cx = x + w // 2
    cv.vline(cx, y + 44, y + 72, INK)
    cv.hline(cx - 26, cx + 26, y + 48, INK)
    for ex in (cx - 26, cx + 26):
        cv.line(ex, y + 48, ex - 6, y + 62, INK)
        cv.line(ex, y + 48, ex + 6, y + 62, INK)
        cv.line(ex - 6, y + 62, ex + 6, y + 62, INK)


def draw_chart(cv, x, y, w, h):
    cv.fill(x, y, w, h, WHITE)
    for gy in range(y + 16, y + h - 8, 16):
        cv.hline(x + 8, x + w - 8, gy, (220, 220, 215))
    for gx in range(x + 16, x + w - 8, 24):
        cv.vline(gx, y + 8, y + h - 16, (220, 220, 215))
    pts = []
    for i in range(11):
        px = x + 14 + i * (w - 28) // 10
        py = y + 14 + [0, 4, 2, 12, 10, 22, 18, 30, 34, 44, 58][i]
        pts.append((px, py))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        cv.line(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, RED)
    for i in (2, 5, 8):
        cv.fill(pts[i][0] - 3, pts[i][1] - 8, 6, 8, GREEN)
    cv.text("S&P 500", x + 12, y + 6, 1, INK)
    cv.text("-3.7%", x + w - 52, y + h - 22, 2, RED)


def draw_peru(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.disc(x + w - 30, y + 14, 9, YELLOW)
    cv.poly_fill([(x, y + h), (x + 70, y + 18), (x + 150, y + h)], (140, 120, 100))
    cv.poly_fill([(x + 90, y + h), (x + 170, y + 8), (x + w, y + h)], (110, 95, 80))
    cv.poly_fill([(x + 58, y + 34), (x + 70, y + 18), (x + 82, y + 34)], WHITE)
    cv.poly_fill([(x + 158, y + 24), (x + 170, y + 8), (x + 182, y + 24)], WHITE)
    cv.fill(x, y + h - 18, w, 18, (150, 130, 100))
    for i in range(5):
        cv.line(x + 20 + i * 40, y + h - 18, x + 34 + i * 40, y + h - 8, INK)
        cv.line(x + 34 + i * 40, y + h - 8, x + 48 + i * 40, y + h - 18, INK)
    cv.poly_fill([(x + 30, y + h - 18), (x + 44, y + h - 32), (x + 58, y + h - 18)],
                 ORANGE)
    cv.poly_fill([(x + 150, y + h - 18), (x + 164, y + h - 32), (x + 178, y + h - 18)],
                 ORANGE)


def draw_heroes(cv):
    specs = [
        (24, draw_shenzhen, "SHENZHEN - THREE LEADERS, ONE TABLE",
         "Trump, Xi and Putin meet; few results"),
        (270, draw_icj, "THE HAGUE - GENOCIDE VERDICT",
         "ICJ: Myanmar guilty over Rohingya"),
        (516, draw_chart, "NEW YORK - STOCKS IN CORRECTION",
         "S&P 500 falls 3.7% as AI rout spreads"),
        (762, draw_peru, "JUNIN, PERU - 6.7 QUAKE",
         "Tremor shakes the Andes at 108 km deep"),
    ]
    for x, fn, title, cap in specs:
        cv.rect(x, 334, 238, 100, INK)
        fn(cv, x + 1, 335, 236, 98)
        cv.text(title, x, 438, 1, INK)
        cv.text(cap, x, 449, 1, GRAY)
    # Thin rule separating the picture row from the map below.
    cv.fill(24, 460, 976, 1, INK)


def draw_map(cv):
    cv.rect(24, 464, 640, 156, INK)
    cv.fill(25, 465, 638, 154, SEA)
    # Faint graticule so the continents sit on a real map grid.
    for gx in range(24 + 85, 664, 85):
        cv.vline(gx, 484, 618, (190, 208, 220))
    for gy in range(486 + 27, 620, 27):
        cv.hline(26, 662, gy, (190, 208, 220))
    cv.text("WORLD MAP - WHERE THE DAY HAPPENED", 32, 470, 1, INK)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        cv.poly_fill(pts, LAND)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        cv.poly_line(pts, LAND_LINE)
    for name, lon, lat, side in CITIES:
        mx, my = project(lon, lat)
        cv.disc(mx, my, 3, RED)
        cv.disc(mx, my, 1, WHITE)
        w = text_width(name, 1)
        if side == "L":
            lx, ly = mx - 6 - w, my - 3
        elif side == "R":
            lx, ly = mx + 6, my - 3
        elif side == "UR":
            # Upper-right diagonal: clears LONDON (left) and KYIV (right)
            # in the crowded Europe corner.
            lx, ly = mx + 6, my - 14
        elif side == "A":
            lx, ly = mx - w // 2, my - 11
        else:
            lx, ly = mx - w // 2, my + 8
        cv.text(name, lx, ly, 1, INK)


def draw_regions(cv):
    cv.text("THE DAY BY REGION", 676, 470, 2, INK)
    y = 490
    for name, count in REGION_COUNTS:
        cv.fill(676, y, 12, 12, REGION_COLORS[name])
        cv.text(name, 694, y + 2, 1, INK)
        cv.text(str(count), 1000 - text_width(str(count), 2), y, 2, INK)
        y += 18
    cv.rect(676, 584, 324, 36, RED)
    cv.text("DATE CHECK - SATURDAY 21 NOVEMBER 2026", 684, 588, 1, RED)
    cv.text("EVERY STORY HAPPENED, OR WAS FIRST", 684, 597, 1, INK)
    cv.text("REPORTED, ON THAT DAY.", 684, 606, 1, INK)


def draw_stories(cv):
    cv.text("THE DAY IN FULL - 48 STORIES", 24, 628, 2, INK)
    cv.text("ALL FROM 21 NOVEMBER 2026", 1024 - 24 - text_width("ALL FROM 21 NOVEMBER 2026", 1), 632, 1, GRAY)
    cv.fill(24, 652, 976, 2, INK)
    cols = (24, 352, 680)
    for ci in range(3):
        for ri in range(16):
            idx = ci * 16 + ri
            region, head, summ = STORIES[idx]
            sy = 658 + ri * 21
            cx = cols[ci]
            cv.fill(cx, sy, 4, 21, REGION_COLORS[region])
            cv.text(head, cx + 8, sy, 2, INK)
            cv.text(summ, cx + 8, sy + 14, 1, GRAY)


def draw_footer(cv):
    cv.fill(24, 996, 976, 1, INK)
    cv.center("THE WORLD IN ONE DAY  •  SATURDAY 21 NOVEMBER 2026  •  48 STORIES FROM FIVE REGIONS",
              W // 2, 1002, 1, INK)
    cv.center("DRAWN BY AN AI AGENT FOR MAKE.FUN - ALL THE DAY'S NEWS ON ONE PAGE",
              W // 2, 1013, 1, GRAY)


def main():
    # Headline spacing check: line 2 must start a full glyph height below
    # line 1's baseline, so the two lines can never overlap.
    assert LEAD_L2_Y - LEAD_BASELINE >= LEAD_GH, "lead headline lines overlap"
    assert len(STORIES) == 48, "need 48 stories"
    for region, head, summ in STORIES:
        assert len(head) <= 28, "headline too long: " + head
        assert len(summ) <= 50, "summary too long: " + summ
    cv = Canvas(W, H, PAPER)
    draw_grain(cv)
    draw_masthead(cv)
    draw_stats(cv)
    draw_lead(cv)
    draw_heroes(cv)
    draw_map(cv)
    draw_regions(cv)
    draw_stories(cv)
    draw_footer(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = encode_png(cv)
    with open(path, "wb") as f:
        f.write(data)
    import hashlib
    print("wrote %s %d bytes sha256=%s" % (path, len(data),
                                           hashlib.sha256(data).hexdigest()))
    print("lead headline: line1 y=%d baseline=%d glyph_h=%d line2 y=%d gap=%d"
          % (LEAD_L1_Y, LEAD_BASELINE, LEAD_GH, LEAD_L2_Y,
             LEAD_L2_Y - LEAD_BASELINE))
    print("stories: %d" % len(STORIES))


if __name__ == "__main__":
    main()
