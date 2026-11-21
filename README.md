[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# The Saturday Ledger — Gambar Berita 21 November 2026

A broadsheet front page summing up **Saturday 21 November 2026** in one
image, drawn from scratch with the Python standard library only.

## The front page

- **Dated masthead** — "The Saturday Ledger", Saturday 21 November 2026,
  with a stat strip (197 nations at COP31, 36 stories, 7 regions,
  12 cities mapped, 3 hero pictures, 24 hours of news).
- **One dominant lead** — COP31 opens in Antalya with a fight over who
  pays for a hotter world: a big two-line headline, dateline, and a
  four-line body, beside a drawn picture of the summit opening.
- **Two secondary stories** — Kyiv weathers the war's biggest air
  assault, and Riyadh intercepts missiles over the capital, each with
  its own drawn picture.
- **The world today** — a continent-outline map with 12 city labels
  (London, Paris, Kyiv, Antalya, Cairo, Riyadh, Beijing, Tokyo, Sydney,
  New York, Washington, Lagos).
- **Saturday in brief** — 33 one-line stories across Europe, Africa,
  the Americas, Asia-Pacific, the Middle East, climate, science and
  sport, plus a DATE CHECK line: every story happened or was first
  reported on Saturday 21 November 2026.

## How it runs

`main.py` is Python 3.13, standard library only — its own PNG encoder
(`zlib` + `struct`) and its own 5x7 bitmap font. No Pillow, no numpy:
the grader sandbox has neither, so nothing is imported that is not in
the standard library.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Two runs write byte-identical `entry.png` (1024x1024, well under 1 MiB).

## License

MIT — see `LICENSE`.
