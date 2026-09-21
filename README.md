# Movie Recommendation System

A content-based Movie Recommendation System built with **Python, Pandas, Scikit-learn and Flask**.

## Project Overview

The application recommends movies based on the characteristics of a selected movie. It performs data preprocessing and feature engineering, converts movie information into numerical features, calculates similarity between movies, and displays the most relevant recommendations.

An optional genre-preference input gives the user a small preference boost when ranking recommendations.

## Features

- Movie selection through a Flask web interface
- Data preprocessing with Pandas
- Feature engineering using movie genres, overview, director and cast
- TF-IDF text feature extraction
- Cosine similarity for movie-to-movie comparison
- Optional user genre preferences
- Top-5 movie recommendations
- Clean and simple web interface
- Self-contained sample dataset so the project runs immediately

## Tech Stack

- Python
- Pandas
- NumPy-compatible Python ecosystem
- Scikit-learn
- Flask
- HTML
- CSS
- Git / GitHub

## Project Structure

```text
Movie_Recommendation_System/
│
├── app.py
├── recommendation_engine.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── movies.csv
│   └── README.md
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── docs/
    ├── project_explanation.md
    └── interview_questions.md
```

## How It Works

### 1. Data Preprocessing
Missing values are replaced with empty strings and the relevant movie fields are cleaned before processing.

### 2. Feature Engineering
The system combines:
- Genres
- Movie overview
- Director
- Cast

into a single feature representation.

### 3. Feature Extraction
TF-IDF converts the combined text information into numerical vectors.

### 4. Similarity Calculation
Cosine similarity measures how similar the selected movie is to other movies.

### 5. Recommendation
Movies with the highest similarity scores are ranked and the top five are returned. Optional genre preferences can slightly increase the ranking of movies matching the selected genres.

## Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd Movie_Recommendation_System
```

### 2. Create a virtual environment (recommended)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open the local URL shown by Flask, normally:

```text
http://127.0.0.1:5000
```

## Dataset

The repository includes a small sample dataset so the application can be run immediately.

For a larger portfolio version, you can replace `data/movies.csv` with a larger movie dataset after adapting the columns expected by `recommendation_engine.py`.

Do not upload datasets whose license or redistribution terms do not permit public GitHub hosting. If you use a third-party dataset, follow its license and provide the original dataset attribution.

## Resume Alignment

The project supports these resume statements:

- Developed a movie recommendation system using Python and Machine Learning techniques.
- Applied data preprocessing and feature engineering to prepare the movie dataset.
- Implemented recommendation logic to suggest movies based on user preferences and movie characteristics.

## Important

Only claim technologies and techniques in your resume that you can explain and demonstrate in the project.

For interview preparation, study the complete recommendation pipeline:
**dataset → preprocessing → feature engineering → TF-IDF → similarity calculation → ranking → recommendations → Flask interface.**
