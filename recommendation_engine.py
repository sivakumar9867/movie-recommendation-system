"""
Movie Recommendation Engine
Content-based recommendation using TF-IDF and cosine similarity.
"""

from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

    def get_movie_titles(self):
        return sorted(self.movies["title"].tolist())

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

            # Small optional preference boost.
            matched_preferences = len(
                movie_genres.intersection(set(preferred_genres))
            )
            adjusted_score = score + (0.05 * matched_preferences)

            recommendations.append({
                "title": row["title"],
                "genres": row["genres"].replace("|", ", "),
                "director": row["director"].replace("|", ", "),
                "score": adjusted_score,
            })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_n]
