"""Discover and verify up to 500 Telugu-original films using TMDB.

Run from the project root after putting TMDB_READ_ACCESS_TOKEN in .env:
  python scripts/sync_verified_telugu_catalog.py --limit 500
  python scripts/sync_verified_telugu_catalog.py --limit 500 --apply

The first command writes data/movies_verified.csv for review. The second backs up
movies.csv and applies only records whose original language is Telugu and whose
movie-specific poster URL returns an image. Missing/broken posters are excluded.
"""
from __future__ import annotations
import argparse, csv, os, shutil, time
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'movies_verified.csv'
LIVE = ROOT / 'data' / 'movies.csv'
EXCLUSIONS = ROOT / 'data' / 'poster_exclusions.csv'
API = 'https://api.themoviedb.org/3'
IMG = 'https://image.tmdb.org/t/p/w500'
FIELDS = ['title','genres','overview','director','cast','poster_url','star','poster_alt_url','year','hero']
GENRES = {28:'Action',12:'Adventure',16:'Animation',35:'Comedy',80:'Crime',99:'Documentary',18:'Drama',10751:'Family',14:'Fantasy',36:'History',27:'Horror',10402:'Music',9648:'Mystery',10749:'Romance',878:'Science Fiction',10770:'TV Movie',53:'Thriller',10752:'War',37:'Western'}


def image_is_valid(session: requests.Session, url: str) -> bool:
    try:
        r = session.get(url, timeout=18, stream=True)
        ok = r.status_code == 200 and r.headers.get('content-type','').lower().startswith('image/')
        # Read a small part so the server actually begins delivering the image.
        if ok:
            next(r.iter_content(1024), b'')
        r.close()
        return ok
    except requests.RequestException:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description='Discover Telugu films and verify authentic TMDB posters.')
    ap.add_argument('--limit', type=int, default=500, help='Maximum verified movies to collect (default 500; max 500).')
    ap.add_argument('--min-votes', type=int, default=5, help='Minimum TMDB vote count to avoid obscure catalogue noise.')
    ap.add_argument('--apply', action='store_true', help='Back up and replace data/movies.csv with verified output.')
    args = ap.parse_args()
    if not 1 <= args.limit <= 500:
        ap.error('--limit must be between 1 and 500')
    load_dotenv(ROOT / '.env')
    token = os.getenv('TMDB_READ_ACCESS_TOKEN','').strip()
    if not token:
        print('Missing TMDB_READ_ACCESS_TOKEN. Copy .env.example to .env and add your token locally.')
        return 2
    s = requests.Session()
    s.headers.update({'Authorization': f'Bearer {token}', 'accept':'application/json'})
    rows, excluded, seen = [], [], set()
    page, total_pages = 1, 1
    print(f'Discovering Telugu-original films; target up to {args.limit} verified posters…')
    while page <= total_pages and page <= 500 and len(rows) < args.limit:
        try:
            res = s.get(API + '/discover/movie', params={
                'with_original_language':'te', 'sort_by':'popularity.desc',
                'include_adult':'false', 'include_video':'false', 'page':page,
                'vote_count.gte':args.min_votes, 'region':'IN'
            }, timeout=25)
            res.raise_for_status()
            payload = res.json()
            total_pages = min(int(payload.get('total_pages',1)), 500)
        except (requests.RequestException, ValueError) as e:
            print(f'Could not read discovery page {page}: {e}')
            break
        for movie in payload.get('results', []):
            if len(rows) >= args.limit: break
            mid = movie.get('id')
            if not mid or mid in seen: continue
            seen.add(mid)
            title = (movie.get('title') or '').strip()
            poster_path = movie.get('poster_path')
            if not title or not poster_path:
                excluded.append((title or f'TMDB id {mid}', 'missing movie title or poster path'))
                continue
            poster = IMG + poster_path
            if not image_is_valid(s, poster):
                excluded.append((title, 'poster URL unavailable or did not return image content'))
                continue
            try:
                detail = s.get(f'{API}/movie/{mid}', params={'append_to_response':'credits','language':'en-US'}, timeout=25)
                detail.raise_for_status()
                d = detail.json()
                # Recheck source-language at detail level; dubbed Telugu releases are not accepted.
                if d.get('original_language') != 'te':
                    excluded.append((title, 'not a Telugu-original film'))
                    continue
                credits = d.get('credits', {})
                cast_list = credits.get('cast', [])
                crew = credits.get('crew', [])
                director = next((x.get('name','') for x in crew if x.get('job') == 'Director'), '')
                cast = '|'.join(x.get('name','') for x in cast_list[:8] if x.get('name'))
                lead = cast_list[0].get('name','') if cast_list else 'Ensemble'
                # Hero field supports the existing Explore by Hero controls; star supports PK shelf.
                star = next((x.get('name','') for x in cast_list[:4] if x.get('known_for_department') == 'Acting'), lead)
                genres = '|'.join(GENRES.get(g.get('id'), g.get('name','Drama')) for g in d.get('genres', [])) or 'Drama'
                rows.append({
                    'title': d.get('title') or title, 'genres': genres,
                    'overview': d.get('overview') or movie.get('overview') or '',
                    'director': director, 'cast': cast, 'poster_url': poster,
                    'star': star, 'poster_alt_url':'',
                    'year': (d.get('release_date') or movie.get('release_date') or '')[:4],
                    'hero': lead or 'Ensemble'
                })
                print(f'[{len(rows):03d}/{args.limit}] VERIFIED  {title}')
            except (requests.RequestException, ValueError) as e:
                excluded.append((title, f'metadata lookup failed: {e}'))
            time.sleep(0.12)
        page += 1
    # Deduplicate on normalized title + year, preserving the most popular first result.
    unique = {}
    for r in rows:
        key = (''.join(ch.lower() for ch in r['title'] if ch.isalnum()), r['year'])
        unique.setdefault(key, r)
    with OUTPUT.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(unique.values())
    with EXCLUSIONS.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['movie','reason']); w.writerows(excluded)
    print(f'\nVerified catalogue: {len(unique)} movies')
    print(f'Excluded: {len(excluded)}; details: {EXCLUSIONS.relative_to(ROOT)}')
    print(f'Review output: {OUTPUT.relative_to(ROOT)}')
    if args.apply:
        if not unique:
            print('No verified movies found; existing catalogue was not changed.')
            return 3
        backup = LIVE.with_name('movies.before_verified_expansion.csv')
        shutil.copy2(LIVE, backup)
        shutil.copy2(OUTPUT, LIVE)
        print(f'Applied. Previous catalogue backed up to {backup.relative_to(ROOT)}')
    else:
        print('Review movies_verified.csv first. Re-run with --apply only when satisfied.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
