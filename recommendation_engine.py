"""
Movie Recommendation Engine
Content-based recommendation using TF-IDF and cosine similarity.
"""

import re
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def slugify(title):
    """'Baahubali 2 The Conclusion' -> 'baahubali-2-the-conclusion' (poster filename)."""
    return re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")


class MovieRecommender:
    def __init__(self, data_path="data/movies.csv"):
        self.data_path = Path(data_path)
        self.movies = pd.read_csv(self.data_path)
        self.movies = self.movies.fillna("")

        # Feature engineering:
        # combine relevant movie characteristics into one text field.
        self.movies["features"] = (
            self.movies["genres"].str.replace("|", " ", regex=False)
            + " " + self.movies["overview"]
            + " " + self.movies["director"].str.replace("|", " ", regex=False)
            + " " + self.movies["cast"].str.replace("|", " ", regex=False)
        )

        # Convert text features into numerical vectors.
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.feature_matrix = self.vectorizer.fit_transform(self.movies["features"])

        # Similarity between every pair of movies.
        self.similarity_matrix = cosine_similarity(self.feature_matrix)

        self.indices = pd.Series(
            self.movies.index, index=self.movies["title"]
        ).drop_duplicates()

    def get_movie(self, title):
        """Details of a single movie (used to show the selected movie's poster)."""
        if title not in self.indices:
            return None
        row = self.movies.iloc[self.indices[title]]
        return {
            "title": row["title"],
            "genres": row["genres"].replace("|", ", "),
            "director": row["director"].replace("|", ", "),
            "overview": row["overview"],
            "poster": slugify(row["title"]) + ".svg",
        }

    def get_genres(self):
        """All genres that really exist in the dataset (used for the genre chips)."""
        found = set()
        for value in self.movies["genres"]:
            found.update(g.strip() for g in str(value).split("|") if g.strip())
        return sorted(found)

    def get_movie_titles(self):
        return sorted(self.movies["title"].tolist())

    def recommend_by_genres(self, genres, top_n=5):
        """Recommend movies purely by the selected genres (no movie needed).

        Ranking: 1) how many of the selected genres the movie has,
                 2) how closely its genre list matches the selection (Jaccard),
                 3) title (stable order for ties).
        """
        wanted = set(genres)
        results = []
        for _, row in self.movies.iterrows():
            movie_genres = set(str(row["genres"]).split("|"))
            matched = sorted(movie_genres & wanted)
            if not matched:
                continue
            jaccard = len(movie_genres & wanted) / len(movie_genres | wanted)
            results.append({
                "title": row["title"],
                "genres": row["genres"].replace("|", ", "),
                "director": row["director"].replace("|", ", "),
                "overview": row["overview"],
                "poster": slugify(row["title"]) + ".svg",
                "matched_genres": matched,
                "match_count": len(matched),
                "genre_total": len(wanted),
                "score": len(matched) + jaccard,
            })
        results.sort(key=lambda r: (-r["score"], r["title"]))
        return results[:top_n]

    def recommend(self, title, preferred_genres=None, top_n=5):
        if title not in self.indices:
            raise ValueError(f"Movie '{title}' was not found.")

        movie_index = self.indices[title]
        similarity_scores = list(enumerate(self.similarity_matrix[movie_index]))

        # Highest similarity first; exclude the selected movie itself.
        similarity_scores = sorted(
            similarity_scores, key=lambda x: x[1], reverse=True
        )

        recommendations = []
        preferred_genres = preferred_genres or []

        for index, score in similarity_scores:
            if index == movie_index:
                continue

            row = self.movies.iloc[index]
            movie_genres = set(str(row["genres"]).split("|"))

            # Preference boost: every selected genre the movie has adds +0.10.
            matched = sorted(movie_genres.intersection(set(preferred_genres)))
            adjusted_score = score + (0.10 * len(matched))

            recommendations.append({
                "title": row["title"],
                "genres": row["genres"].replace("|", ", "),
                "director": row["director"].replace("|", ", "),
                "overview": row["overview"],
                "poster": slugify(row["title"]) + ".svg",
                "matched_genres": matched,
                "score": adjusted_score,
            })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_n]
