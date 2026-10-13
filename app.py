from flask import Flask, render_template, request
from recommendation_engine import MovieRecommender

app = Flask(__name__)
recommender = MovieRecommender("data/movies.csv")


@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    selected_movie = ""
    selected_genres = []
    selected_info = None
    error = None

    if request.method == "POST":
        selected_movie = request.form.get("movie", "")
        selected_genres = request.form.getlist("genres")

        selected_info = recommender.get_movie(selected_movie)
        try:
            if selected_movie:
                # movie (+ optional genres boost)
                recommendations = recommender.recommend(
                    selected_movie,
                    preferred_genres=selected_genres,
                    top_n=5,
                )
            elif selected_genres:
                # genres only
                recommendations = recommender.recommend_by_genres(
                    selected_genres, top_n=5
                )
            else:
                error = "Pick a movie, one or more genres, or both."
        except ValueError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        movies=recommender.get_movie_titles(),
        genres=recommender.get_genres(),
        recommendations=recommendations,
        selected_movie=selected_movie,
        selected_info=selected_info,
        selected_genres=selected_genres,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
