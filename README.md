# Mana Cinema - Telugu Movie Recommendation System

A content-based movie recommender for Telugu (Tollywood) films built with
**Python, Pandas, Scikit-learn and Flask**.

## Features
- Three ways to get recommendations:
  - **Movie only** - the 5 most similar films (click a poster or use the dropdown)
  - **Genres only** - tap one or more genres, no movie needed; films are ranked by how many of
    the selected genres they have
  - **Movie + genres** - similar films, with movies in your chosen genres ranked higher
- Tap-to-select genre buttons built from the genres in the dataset
- Each result shows which of your genres it matches
- Feature engineering from genres, overview, director and cast
- TF-IDF vectors + cosine similarity
- Poster images: generated local artwork out of the box, real HD posters optional (TMDB)
- Responsive dark "gold" UI

## Project structure
```text
Mana_Cinema/
├── app.py                      Flask app
├── recommendation_engine.py    TF-IDF + cosine similarity engine
├── generate_posters.py         creates local SVG poster art (offline)
├── fetch_posters.py            downloads real HD posters from TMDB (optional)
├── replace_movies.py           rebuilds data/movies.csv
├── requirements.txt
├── setup_windows.bat           one-time environment setup (creates ./venv)
├── run_windows.bat             one-click run on Windows
├── fetch_real_posters_windows.bat
├── data/movies.csv
├── templates/index.html
└── static/posters/             poster images (.svg generated, .jpg real)
```

## Run it (Windows)
Everything lives in this one folder - the Python environment (`venv`) is created inside it.

1. Double-click **`run_windows.bat`**. The first time it creates `venv` and installs the packages (internet needed).
2. Open http://127.0.0.1:5000

Needs Python 3.10+ (https://www.python.org/downloads/ - tick "Add python.exe to PATH").

**Manual / VS Code terminal:**
```powershell
.\venv\Scripts\python.exe app.py
```

## Real HD posters (optional)
1. Create a free account at https://www.themoviedb.org and request an API key
   (Settings -> API -> Developer).
2. Windows: double-click `fetch_real_posters_windows.bat` and paste the key.
   Or in a terminal:
   ```powershell
   $env:TMDB_API_KEY="your_key"
   .\venv\Scripts\python.exe fetch_posters.py
   ```
3. Refresh the browser with Ctrl+F5. Any poster that is missing falls back to the generated art.

Posters are the property of their owners; do not publish the downloaded JPGs.
This product uses the TMDB API but is not endorsed or certified by TMDB.

## How it works
**Movie-based:** dataset -> preprocessing -> feature engineering (genres + overview + director + cast)
-> TF-IDF -> cosine similarity -> optional genre boost (+0.10 per matching genre) -> top-5 -> Flask interface.

**Genre-only:** selected genres -> count of matching genres per movie (ties broken by Jaccard
similarity of the genre sets) -> top-5. The dataset has 31 films, so a rare genre may return fewer than 5.
