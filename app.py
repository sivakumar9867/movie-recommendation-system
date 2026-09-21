from flask import Flask, render_template, request
from recommendation_engine import MovieRecommender

app = Flask(__name__)
recommender = MovieRecommender("data/movies.csv")


@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    selected_movie = ""
    selected_genres = []
    error = None

    if request.method == "POST":
        selected_movie = request.form.get("movie", "")
        selected_genres = request.form.getlist("genres")

        try:
            recommendations = recommender.recommend(
                selected_movie,
                preferred_genres=selected_genres,
                top_n=5,
            )
        except ValueError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        movies=recommender.get_movie_titles(),
        genres=["Action", "Adventure", "Animation", "Comedy", "Crime",
                "Drama", "Family", "Fantasy", "Music", "Mystery",
                "Romance", "Sci-Fi", "Thriller"],
        recommendations=recommendations,
        selected_movie=selected_movie,
        selected_genres=selected_genres,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
