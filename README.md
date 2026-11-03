# Mana Cinema — Telugu Film Club

<p align="center">
  <strong>Discover Telugu cinema. Find your next favourite story.</strong><br>
  A Flask-powered Telugu movie discovery and recommendation application featuring a curated catalogue of 500 films.
</p>

<p align="center">
  <img src="screenshots/homepage-hero.png" alt="Mana Cinema homepage" width="900">
</p>

## About the Project

**Mana Cinema** is a content-based Telugu movie discovery platform built with Python, Flask, Pandas and Scikit-learn. It brings together a 500-film catalogue, locally stored posters, actor-based browsing and personalized recommendations in an editorial-style interface.

## Key Features

- **500 Telugu Films:** Explore a catalogue of 500 Telugu movies.
- **Local Movie Posters:** All posters are stored locally in `static/posters/`.
- **Browse by Hero:** Discover films based on your favourite actors.
- **Pawan Kalyan Fan Shelf:** A dedicated collection featuring 12 films.
- **Movie Recommendations:** Discover similar movies based on content.
- **Genre-Based Discovery:** Find movies by selecting your preferred genres.
- **Combined Recommendations:** Combine movie selection with genre preferences.
- **Responsive Interface:** Clean and engaging movie discovery experience.

## Screenshots

### 1. Homepage

The homepage features a three-star showcase with Ram Charan, Pawan Kalyan and Prabhas.

![Mana Cinema Homepage](screenshots/homepage-hero.png)

### 2. Pawan Kalyan Fan Shelf

![Pawan Kalyan Fan Shelf](screenshots/pawan-kalyan-fan-shelf.png)

### 3. Browse by Hero

![Browse by Hero](screenshots/browse-by-hero.png)

### 4. Find a Film

![Find a Film](screenshots/find-a-film.png)

### 5. Mood-Based Discovery

![Mood-Based Discovery](screenshots/mood-based-discovery.png)

### 6. Movie Recommendations

**Recommendations for Arjun Reddy**

![Recommendations for Arjun Reddy](screenshots/recommendations-arjun-reddy.png)

**Personalized Movie Picks**

![Personalized Picks](screenshots/recommendations-personalized-picks.png)

**Couple Friendly Recommendations**

![Couple Friendly Recommendations](screenshots/recommendations-couple-friendly.png)

**More Recommended Films**

![More Recommended Films](screenshots/recommendations-more-films.png)

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web framework |
| Pandas | Movie catalogue processing |
| Scikit-learn | Recommendation engine |
| TF-IDF | Text feature extraction |
| Cosine Similarity | Movie similarity calculation |
| HTML | Webpage structure |
| CSS | User interface and styling |
| TMDB API | Optional catalogue and poster updates |

## Recommendation System

Mana Cinema uses a content-based recommendation approach.

Movie information such as genres, synopsis, director and cast is combined into text features.

1. **TF-IDF Vectorization:** Converts movie descriptions into numerical feature vectors.
2. **Cosine Similarity:** Measures similarity between movies.
3. **Movie-Based Recommendations:** Finds movies similar to the selected title.
4. **Genre-Based Recommendations:** Suggests movies matching selected genres.
5. **Combined Recommendations:** Uses movie similarity and selected genre preferences to improve results.

## Installation and Setup

### Requirements

- Python 3.10 or later
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/sivakumar9867/movie-recommendation-system.git
cd movie-recommendation-system
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and visit:

http://127.0.0.1:5000

**Note:** The bundled movie catalogue and locally stored posters are included in the repository. A TMDB API token is not required for normal application usage.

## Running Tests

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the test suite:

```bash
python -m pytest -q
```

## Optional Catalogue Refresh

To refresh the movie catalogue or download additional posters:

1. Copy `.env.example` to `.env`.
2. Add your TMDB API Read Access Token to `TMDB_READ_ACCESS_TOKEN`.
3. Run the relevant scripts from the `scripts/` directory.

**Important:** Never upload or share your `.env` file or API token. The `.env` file is excluded through `.gitignore`.

## Project Structure

```text
movie-recommendation-system/
│
├── app.py
│
├── data/
│   └── movies.csv
│
├── scripts/
│   ├── sync_verified_telugu_catalog.py
│   └── download_verified_posters.py
│
├── screenshots/
│   ├── homepage-hero.png
│   ├── pawan-kalyan-fan-shelf.png
│   ├── browse-by-hero.png
│   ├── find-a-film.png
│   ├── mood-based-discovery.png
│   └── recommendations-*.png
│
├── static/
│   ├── style.css
│   └── posters/
│
├── templates/
│   └── index.html
│
├── tests/
│   └── test_recommender.py
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## Poster and Data Rights

All movie posters, promotional artwork and related visual materials remain the property of their respective copyright owners.

Their inclusion in this project does not transfer ownership or grant permission for commercial use, republication or redistribution. Please verify applicable rights and provider terms before reusing these assets.

The source-code licence does not automatically apply to third-party movie artwork.

Mana Cinema is an independent student project and is not affiliated with TMDB, film studios, actors or other rights holders.

---

<p align="center">
  Made with ❤️ for Telugu Cinema
</p>
