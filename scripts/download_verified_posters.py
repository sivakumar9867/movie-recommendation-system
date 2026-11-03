#!/usr/bin/env python3
"""Download verified TMDB poster URLs into the local Flask static folder.

Run from the project root:
    python scripts/download_verified_posters.py
    python scripts/download_verified_posters.py --apply

The default run creates data/movies_with_local_posters.csv and downloads poster
files into static/posters/. It does not modify data/movies.csv. With --apply,
it backs up data/movies.csv and replaces it with the local-poster catalogue.
No TMDB API token is needed: this script downloads the image URLs already
recorded in data/movies_verified.csv.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "movies_verified.csv"
OUTPUT = ROOT / "data" / "movies_with_local_posters.csv"
FAILURES = ROOT / "data" / "poster_download_failures.csv"
LIVE = ROOT / "data" / "movies.csv"
POSTER_DIR = ROOT / "static" / "posters"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value[:70] or "movie"


def make_session() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=12, pool_maxsize=12)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "ManaCinema-PosterArchive/1.0"})
    return session


def image_extension(content_type: str, data: bytes) -> str | None:
    content_type = (content_type or "").split(";", 1)[0].strip().lower()
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if len(data) > 12 and data[4:12] in (b"ftypavif", b"ftypavis"):
        return ".avif"
    # Fail closed: do not save HTML/error pages as posters.
    return None


def fetch_image(session: requests.Session, url: str) -> Tuple[bytes | None, str | None, str]:
    if not url or not url.startswith("https://image.tmdb.org/t/p/"):
        return None, None, "missing or non-TMDB poster URL"
    try:
        response = session.get(url, timeout=(15, 45))
        response.raise_for_status()
        data = response.content
        ext = image_extension(response.headers.get("content-type", ""), data)
        if not ext:
            return None, None, "response was not a recognised image file"
        if len(data) < 2_000:
            return None, None, "image response was unexpectedly small"
        return data, ext, ""
    except requests.RequestException as exc:
        return None, None, f"download failed: {type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download verified movie posters locally.")
    parser.add_argument("--apply", action="store_true", help="Back up and replace data/movies.csv after downloads.")
    parser.add_argument("--limit", type=int, default=500, help="Maximum rows to process (default 500).")
    args = parser.parse_args()
    if not SOURCE.exists():
        print(f"Missing input: {SOURCE.relative_to(ROOT)}")
        return 2

    with SOURCE.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not rows:
        print("The verified catalogue is empty; nothing to download.")
        return 3
    if "poster_url" not in fieldnames or "title" not in fieldnames:
        print("Input CSV must contain title and poster_url columns.")
        return 4

    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    if "poster_local" not in fieldnames:
        fieldnames.append("poster_local")

    session = make_session()
    output_rows: List[Dict[str, str]] = []
    failures: List[Dict[str, str]] = []
    limit_rows = rows[: max(1, min(args.limit, 500))]
    total = len(limit_rows)
    downloaded = reused = 0

    print(f"Downloading posters for up to {total} movies into static/posters/ …")
    for index, row in enumerate(limit_rows, start=1):
        title = (row.get("title") or f"Movie {index}").strip()
        url = (row.get("poster_url") or "").strip()
        stem = f"{index:03d}-{slugify(title)}"
        # Reuse a previously downloaded file only if it still has a valid image signature.
        existing = next((p for p in POSTER_DIR.glob(stem + ".*") if p.is_file()), None)
        reused_this = False
        if existing:
            try:
                prefix = existing.read_bytes()[:32]
                if image_extension("", prefix):
                    local_file = existing
                    reused += 1
                    reused_this = True
                    data, ext, error = None, existing.suffix, ""
                else:
                    existing.unlink(missing_ok=True)
                    data, ext, error = fetch_image(session, url)
                    local_file = None
            except OSError:
                data, ext, error = fetch_image(session, url)
                local_file = None
        else:
            data, ext, error = fetch_image(session, url)
            local_file = None

        if local_file is None:
            if not data or not ext:
                failures.append({"title": title, "poster_url": url, "reason": error or "download failed"})
                print(f"[{index:03d}/{total}] FAILED   {title}")
                continue
            local_file = POSTER_DIR / f"{stem}{ext}"
            temp_file = local_file.with_suffix(local_file.suffix + ".part")
            try:
                temp_file.write_bytes(data)
                temp_file.replace(local_file)
                downloaded += 1
            except OSError as exc:
                temp_file.unlink(missing_ok=True)
                failures.append({"title": title, "poster_url": url, "reason": f"file write failed: {exc}"})
                print(f"[{index:03d}/{total}] FAILED   {title}")
                continue

        # Relative path is designed for Flask's url_for('static', filename=...).
        row["poster_local"] = f"posters/{local_file.name}"
        # Keep a local URL in poster_url because the existing page uses poster_url as img src.
        row["poster_url"] = f"/static/{row['poster_local'].replace(chr(92), '/') }"
        row["poster_alt_url"] = ""
        output_rows.append(row)
        status = "REUSED" if reused_this else "SAVED"
        print(f"[{index:03d}/{total}] {status:6}  {title}")
        time.sleep(0.03)

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)
    with FAILURES.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["title", "poster_url", "reason"])
        writer.writeheader()
        writer.writerows(failures)

    print("\nPoster download summary")
    print(f"Local posters ready: {len(output_rows)}")
    print(f"Newly downloaded: {downloaded}; reused: {reused}; failed: {len(failures)}")
    print(f"Catalogue for review: {OUTPUT.relative_to(ROOT)}")
    print(f"Failures report: {FAILURES.relative_to(ROOT)}")
    if args.apply:
        if not output_rows:
            print("No local posters succeeded; existing catalogue was not changed.")
            return 5
        backup = LIVE.with_name("movies.before_local_posters.csv")
        if LIVE.exists():
            shutil.copy2(LIVE, backup)
            print(f"Backup created: {backup.relative_to(ROOT)}")
        shutil.copy2(OUTPUT, LIVE)
        print(f"Applied local-poster catalogue to {LIVE.relative_to(ROOT)}")
    else:
        print("Review the output first. Re-run with --apply only when satisfied.")
    return 0 if output_rows else 6


if __name__ == "__main__":
    raise SystemExit(main())
