# The Saturday Ledger — Gambar Berita 21 Nov

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

A broadsheet front page summing up the world's news of Saturday 21 November 2026, drawn entirely by `main.py` (Python standard library only: own PNG encoder + own 5x7 bitmap font, no Pillow, no numpy).

- Dated masthead: "Saturday, 21 November 2026" with a stat strip.
- Lead story: COP31 opens in Antalya, with a large illustrated hero panel (globe, sun, flags, crowd).
- Two pictured secondaries: Kyiv's biggest air assault and Riyadh's missile intercepts.
- A detailed world map with 12 labelled cities, plus 35 brief stories across 7 regions, a markets sparkline strip, a weather row, and a DATE CHECK line.
- The program runs twice and writes the same bytes every time (deterministic, fixed-seed).

Run it: `MAKEFUN_OUTPUT_DIR=out python3 main.py` — writes `out/entry.png` (1024x1024, under 1 MiB).
