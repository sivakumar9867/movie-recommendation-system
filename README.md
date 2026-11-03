# Mana Cinema — Telugu Film Club

Mana Cinema is a Flask-based Telugu movie discovery and recommendation app. This version includes a catalogue of **500 Telugu films**, locally stored poster images, an editorial-style homepage, hero-based browsing, and a dedicated Pawan Kalyan fan shelf.

## Homepage preview

The featured three-star poster stage presents **Rangasthalam** (Ram Charan), **Gabbar Singh** (Pawan Kalyan), and **Baahubali 2: The Conclusion** (Prabhas).

The Pawan Kalyan shelf contains 12 films from the catalogue. Screenshots in `screenshots/` show the existing desktop, mobile, and fan-shelf previews.

## Features

- Browse and search a 500-film Telugu catalogue.
- Explore titles by lead actor using the hero filter.
- Browse the Pawan Kalyan fan shelf.
- Get content-based recommendations using movie genres, synopsis, director, and cast.
- Discover films by selected genres or combine a selected movie with genre preferences.
- Use locally stored poster files from `static/posters/`; the application does not need a TMDB token to run with the bundled catalogue.
- Responsive homepage and movie browsing interface.

## Run locally

Python 3.10 or later is recommended.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies and start the app:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Recommendation approach

The recommender combines each film's genres, synopsis, director, and cast into a text feature. `TfidfVectorizer` converts these features into vectors, and cosine similarity ranks related films.

- **Movie recommendations:** rank films by content similarity to the selected title.
- **Genre recommendations:** rank films by overlap with the selected genres.
- **Combined recommendations:** apply a small ranking boost for selected genres while retaining the raw similarity score.

## Project structure

```text
Mana-Movie/
├── app.py
├── requirements.txt
├── data/
│   └── movies.csv
├── static/
│   ├── style.css
│   └── posters/          # 500 locally stored poster images
├── templates/
│   └── index.html
├── scripts/
│   ├── sync_verified_telugu_catalog.py
│   └── download_verified_posters.py
├── screenshots/
├── tests/
│   └── test_recommender.py
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Tests

Install development dependencies and run the test suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The current test suite checks the 500-title catalogue, local poster files, the Pawan Kalyan shelf, recommendation behaviour, genre filtering, and title slug generation.

## Optional catalogue refresh

The bundled catalogue and local posters are already included, so a TMDB token is **not required** to run the application.

To refresh or regenerate catalogue data, copy `.env.example` to `.env` and add a TMDB API Read Access Token to `TMDB_READ_ACCESS_TOKEN`. Then run the relevant scripts under `scripts/`. Keep `.env` private; it is excluded by `.gitignore`. Never commit or share the token.

## Poster and data rights

Film poster artwork, stills, and other third-party promotional materials remain the property of their respective rights holders. Their inclusion in this project does not transfer ownership or grant permission for commercial use, republication, or redistribution. Confirm the applicable rights and provider terms before reusing or deploying these assets publicly. The source-code licence does not automatically license third-party artwork.

Mana Cinema is an independent student project and is not affiliated with TMDB, film studios, actors, or other rights holders.
