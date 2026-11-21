# The World in One Day — Saturday 21 November 2026

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

One image that sums up the world's news of Saturday 21 November 2026: the
Kyiv overnight drone and missile barrage, the Shenzhen summit of Trump, Xi
and Putin, the ICJ genocide verdict on Myanmar, the Wall Street correction,
the 6.7 quake in Peru, and the Hormuz crisis — 48 stories from five regions,
drawn as a single broadsheet page.

## How it is made

`main.py` draws the whole broadsheet procedurally with the Python standard
library only — its own PNG encoder (zlib + struct) and its own 5×7 bitmap
font. No Pillow, no numpy, no network, no clock, no external files. Run it
twice and both runs write byte-identical PNGs.

    MAKEFUN_OUTPUT_DIR=out python3 main.py

The program is fully deterministic: two runs in different output folders
write byte-identical PNGs (same sha256), and the image is 1024×1024 and
under the 1 MiB limit.

## What the page holds

- A masthead dated **SATURDAY 21 NOVEMBER 2026** with the lead story.
- An eight-number stat strip: 48 stories, 5 regions, 5 hero pictures,
  1 world map, 400+ drones at Kyiv, S&P 500 −3.7%, Nasdaq −5.3%, Peru quake 6.7.
- Five drawn pictures: Kyiv at night under the barrage, the Shenzhen summit
  table, the ICJ courthouse, the plunging market chart, and the Peru quake.
- A world map with recognisable continent outlines and 12 city markers.
- Region chips with story counts, an explicit **DATE CHECK** box, and the full
  list of 48 stories in three columns.

## License

MIT — see `LICENSE`.
