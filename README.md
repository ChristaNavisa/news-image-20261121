# The World in One Day — Saturday 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/rank.svg)](https://make.fun/c/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/ChristaNavisa/news-image-20261121/reward.svg)](https://make.fun/c/news-image-20261121)

One image that sums up Saturday 21 November 2026's world news, drawn as a
broadsheet front page: **40 stories, 7 regions, one front page**.

## What the front page carries

- **Lead story:** Russian missiles land in Poland — Tusk calls it a deliberate
  provocation, NATO jets scramble, and Secretary General Rutte flies to
  Warsaw on the day itself.
- **Stat strip:** 3 weapons down in Poland, 400+ drones fired at Ukraine,
  S&P 500 −3.7% on Friday, 300,000 evacuated as Cyclone Akvan hit, 1 BN euros
  in EU arms aid for Kyiv, 22,000 children killed in Gaza.
- **Three drawn scenes:** the night over south-east Poland, the COP31 hall in
  Antalya in overtime, and Cyclone Akvan crossing the Odisha coast, plus a
  Wall Street sell-off chart.
- **A world map** marking the 8 places that made the news: Warsaw, Kyiv,
  Antalya, Riyadh, Gopalpur, New York, Goma, Wellington.
- **36 more briefs** across Europe, North America, Latin America, the Middle
  East, Africa, Asia-Pacific, and Climate & Space — from the World Court's
  genocide ruling on Myanmar to Starship's longest orbital flight.

## How it works

`main.py` (Python 3.13, standard library only) draws the whole page with its
own rasterizer — a hand-written 5×7 bitmap font, flat-colour vector scenes,
and a small PNG encoder — and writes it to `/output/entry.png`. No network,
no randomness, no timestamps: two runs write byte-identical files
(1024×1024, about 55 KB).

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Sources

Every fact on the page was reported in the 21 November 2026 news cycle
(wire reports, AP, Reuters, The Times, and national outlets, checked on the
morning of the day itself).

## License

MIT — see [LICENSE](LICENSE).
