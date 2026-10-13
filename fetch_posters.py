"""
Downloads real HD movie posters from TMDB into static/posters/<slug>.jpg

SETUP (one time, free):
  1. Create an account at https://www.themoviedb.org
  2. Settings -> API -> Create -> Developer (personal use)
  3. Copy the "API Key" (or the "API Read Access Token")

RUN (Windows PowerShell, inside your project folder):
  $env:TMDB_API_KEY="paste_your_key_here"
  python fetch_posters.py

Options:
  python fetch_posters.py --size original     # biggest quality (default: w780)
  python fetch_posters.py --force             # re-download existing JPGs

Uses only the Python standard library (no pip install needed).
Images are (c) their owners. Data/images provided by TMDB - see attribution in the site footer.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from recommendation_engine import slugify

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p"

# title in movies.csv -> (TMDB search title, release year)
LOOKUP = {
    "RRR": ("RRR", 2022),
    "Baahubali The Beginning": ("Baahubali: The Beginning", 2015),
    "Baahubali 2 The Conclusion": ("Baahubali 2: The Conclusion", 2017),
    "Pushpa The Rise": ("Pushpa: The Rise", 2021),
    "Pushpa 2 The Rule": ("Pushpa 2: The Rule", 2024),
    "Ala Vaikunthapurramuloo": ("Ala Vaikunthapurramuloo", 2020),
    "Arjun Reddy": ("Arjun Reddy", 2017),
    "Geetha Govindam": ("Geetha Govindam", 2018),
    "Rangasthalam": ("Rangasthalam", 2018),
    "Magadheera": ("Magadheera", 2009),
    "Eega": ("Eega", 2012),
    "Jersey": ("Jersey", 2019),
    "Mahanati": ("Mahanati", 2018),
    "Sita Ramam": ("Sita Ramam", 2022),
    "Hi Nanna": ("Hi Nanna", 2023),
    "Salaar Part 1 Ceasefire": ("Salaar: Part 1 - Ceasefire", 2023),
    "Kalki 2898 AD": ("Kalki 2898 AD", 2024),
    "Devara Part 1": ("Devara: Part 1", 2024),
    "Pokiri": ("Pokiri", 2006),
    "Businessman": ("Businessman", 2012),
    "Athadu": ("Athadu", 2005),
    "Srimanthudu": ("Srimanthudu", 2015),
    "Oopiri": ("Oopiri", 2016),
    "Fidaa": ("Fidaa", 2017),
    "Bommarillu": ("Bommarillu", 2006),
    "Manam": ("Manam", 2014),
    "Dasara": ("Dasara", 2023),
    "Hanu-Man": ("HanuMan", 2024),
    "DJ Tillu": ("DJ Tillu", 2022),
    "Nuvvostanante Nenoddantana": ("Nuvvostanante Nenoddantana", 2005),
    "Leader": ("Leader", 2010),
}


def open_with_retry(req, timeout=30, tries=6):
    """Network on some ISPs resets connections randomly (WinError 10054): retry with backoff."""
    last = None
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError:
            raise                                   # real HTTP errors (401, 404...) are not retried
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            last = e
            wait = 1.5 * (attempt + 1)
            print(f"       network hiccup, retrying in {wait:.1f}s ({attempt + 1}/{tries})")
            time.sleep(wait)
    raise last


def api_get(path, params, key):
    headers = {"Accept": "application/json", "User-Agent": "ManaCinema/1.0", "Connection": "close"}
    params = dict(params)
    if key.startswith("eyJ"):                      # v4 read-access token
        headers["Authorization"] = f"Bearer {key}"
    else:                                          # v3 api key
        params["api_key"] = key
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=headers)
    with open_with_retry(req, timeout=20) as r:
        return json.load(r)


def pick(results):
    """Prefer Telugu-language results that have a poster."""
    with_poster = [r for r in results if r.get("poster_path")]
    telugu = [r for r in with_poster if r.get("original_language") == "te"]
    return (telugu or with_poster or [None])[0]


def find_movie(title, year, key):
    query, y = LOOKUP.get(title, (title, None))
    attempts = []
    if y:
        attempts.append({"query": query, "year": y})
    attempts.append({"query": query})
    for params in attempts:
        data = api_get("/search/movie", params, key)
        best = pick(data.get("results", []))
        if best:
            return best
    return None


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "ManaCinema/1.0", "Connection": "close"})
    with open_with_retry(req, timeout=40) as r:
        dest.write_bytes(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("TMDB_API_KEY", ""))
    ap.add_argument("--size", default="w780", help="w500, w780 (default) or original")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.key:
        sys.exit("No API key. Set it first:\n  $env:TMDB_API_KEY=\"your_key\"   (PowerShell)\n"
                 "or run: python fetch_posters.py --key your_key")

    out = Path("static/posters")
    out.mkdir(parents=True, exist_ok=True)

    with open("data/movies.csv", newline="", encoding="utf-8-sig") as f:
        titles = [row["title"] for row in csv.DictReader(f)]

    ok, missing = 0, []
    for title in titles:
        dest = out / f"{slugify(title)}.jpg"
        if dest.exists() and not args.force:
            print(f"skip   {title} (already downloaded)")
            ok += 1
            continue
        try:
            movie = find_movie(title, None, args.key)
            if not movie:
                print(f"MISS   {title}")
                missing.append(title)
                continue
            download(f"{IMG}/{args.size}{movie['poster_path']}", dest)
            print(f"ok     {title}  ->  {movie.get('title')} ({(movie.get('release_date') or '')[:4]})")
            ok += 1
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit("TMDB rejected the key (401). Check that you copied the full API key.")
            print(f"ERROR  {title}: HTTP {e.code}")
            missing.append(title)
        except Exception as e:
            print(f"ERROR  {title}: {e}")
            missing.append(title)
        time.sleep(0.8)

    # Optional wide banner for the hero section (RRR backdrop)
    try:
        hero = out / "hero.jpg"
        if args.force or not hero.exists():
            m = find_movie("RRR", None, args.key)
            if m and m.get("backdrop_path"):
                download(f"{IMG}/w1280{m['backdrop_path']}", hero)
                print("ok     hero banner")
    except Exception as e:
        print(f"(hero banner skipped: {e})")

    print(f"\nDone: {ok}/{len(titles)} posters in {out.resolve()}")
    if missing:
        print("Not found (these keep the generated art):", ", ".join(missing))
    print("Now press Ctrl+F5 in the browser.")


if __name__ == "__main__":
    main()
