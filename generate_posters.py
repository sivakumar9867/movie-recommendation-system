"""
Generates original, local SVG poster art for every movie in data/movies.csv.
No internet, API key or extra libraries needed.

Run:  python generate_posters.py
Output: static/posters/<slug>.svg
"""
import csv
import hashlib
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from recommendation_engine import slugify

GENRE_HUES = {  # primary genre -> base hue
    "Action": 8, "Adventure": 32, "Fantasy": 275, "Drama": 215,
    "Romance": 335, "Comedy": 45, "Crime": 0, "Thriller": 190,
    "Sci-Fi": 255, "Sport": 140, "Biography": 25,
}


def wrap_title(title, width=13):
    lines = textwrap.wrap(title.upper(), width=width, break_long_words=True)
    return lines[:4]


def build_svg(row):
    title = row["title"]
    genres = row["genres"].split("|")
    h = int(hashlib.md5(title.encode()).hexdigest(), 16)
    hue = GENRE_HUES.get(genres[0], 200)
    hue2 = (hue + 35 + h % 40) % 360
    cx, cy, r = 60 + h % 280, 120 + (h >> 8) % 160, 90 + (h >> 16) % 80

    lines = wrap_title(title)
    size = 44 if max(len(l) for l in lines) <= 10 else 36
    start_y = 330 - (len(lines) - 1) * size * 0.55
    tspans = "".join(
        f'<tspan x="200" y="{start_y + i * size * 1.15:.0f}">{escape(l)}</tspan>'
        for i, l in enumerate(lines)
    )
    genre_text = escape(" / ".join(genres[:3]))
    director = escape(row["director"])
    uid = f"g{h % 99999}"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="400" height="600" role="img" aria-label="{escape(title)} poster">
  <defs>
    <linearGradient id="{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="hsl({hue},65%,38%)"/>
      <stop offset="1" stop-color="hsl({hue2},70%,12%)"/>
    </linearGradient>
    <linearGradient id="{uid}f" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.75"/>
    </linearGradient>
  </defs>
  <rect width="400" height="600" fill="url(#{uid})"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="hsl({hue},80%,70%)" opacity="0.22"/>
  <circle cx="{400 - cx // 2}" cy="{cy + 150}" r="{r // 2}" fill="hsl({hue2},80%,65%)" opacity="0.18"/>
  <path d="M-20 520 L140 380 L240 470 L330 350 L420 430 L420 620 L-20 620 Z" fill="#000" opacity="0.28"/>
  <rect width="400" height="600" fill="url(#{uid}f)"/>
  <rect x="14" y="14" width="372" height="572" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="2"/>
  <text x="200" y="100" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#fff" fill-opacity="0.75" letter-spacing="4">MANA CINEMA</text>
  <text text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-weight="bold" font-size="{size}" fill="#fff">{tspans}</text>
  <line x1="150" y1="505" x2="250" y2="505" stroke="#fff" stroke-opacity="0.5"/>
  <text x="200" y="530" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#fff" fill-opacity="0.9">{genre_text}</text>
  <text x="200" y="554" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#fff" fill-opacity="0.65">Dir. {director}</text>
</svg>
"""


def build_hero():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 600" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="h" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#7a4a14"/><stop offset="0.55" stop-color="#2a1a0c"/><stop offset="1" stop-color="#101010"/>
    </linearGradient>
    <radialGradient id="s" cx="0.78" cy="0.35" r="0.5">
      <stop offset="0" stop-color="#ffd58a" stop-opacity="0.75"/><stop offset="1" stop-color="#ffd58a" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="600" fill="url(#h)"/>
  <rect width="1600" height="600" fill="url(#s)"/>
  <circle cx="1250" cy="210" r="95" fill="#ffe3a8" opacity="0.55"/>
  <path d="M700 600 L1000 330 L1180 470 L1350 300 L1600 480 L1600 600 Z" fill="#000" opacity="0.45"/>
  <path d="M900 600 L1150 420 L1300 520 L1450 400 L1600 520 L1600 600 Z" fill="#000" opacity="0.6"/>
</svg>
"""


def main():
    out = Path("static/posters")
    out.mkdir(parents=True, exist_ok=True)
    with open("data/movies.csv", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        (out / f"{slugify(row['title'])}.svg").write_text(build_svg(row), encoding="utf-8")
    (out / "hero.svg").write_text(build_hero(), encoding="utf-8")
    # generic fallback used when a poster file is missing
    (out / "default.svg").write_text(build_svg({
        "title": "Poster unavailable", "genres": "Mana Cinema",
        "director": "-",
    }), encoding="utf-8")
    print(f"Created {len(rows)} posters in {out.resolve()}")


if __name__ == "__main__":
    main()
