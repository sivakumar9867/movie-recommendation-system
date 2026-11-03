from pathlib import Path

import pytest

from app import MovieRecommender, slugify


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_recommender():
    return MovieRecommender(PROJECT_ROOT / "data" / "movies.csv")


def test_catalog_has_500_unique_titles_with_local_poster_files():
    recommender = build_recommender()
    movies = recommender.all_movies()

    assert recommender.movie_count == 500
    assert len(recommender.index) == 500
    assert len(movies) == 500

    for movie in movies:
        poster_url = movie["poster_url"]
        assert poster_url.startswith("/static/posters/")
        poster_file = PROJECT_ROOT / poster_url.lstrip("/")
        assert poster_file.is_file(), f"Missing local poster for {movie['title']}: {poster_file}"


def test_pawan_kalyan_fan_shelf_has_twelve_films():
    titles = {movie["title"] for movie in build_recommender().power_star_movies()}

    assert len(titles) == 12
    assert "Gabbar Singh" in titles
    assert "Bheemla Nayak" in titles
    assert "Jalsa" in titles


def test_movie_years_are_formatted_without_decimal_suffix():
    recommender = build_recommender()

    # The current 500-film catalogue contains the 2023 Vijay Deverakonda film Kushi.
    assert recommender.get_movie("Kushi")["year"] == "2023"
    assert recommender.get_movie("Bheemla Nayak")["year"] == "2022"


def test_sita_ramam_uses_local_jpg_poster():
    movie = build_recommender().get_movie("Sita Ramam")

    assert movie["poster_url"] == "/static/posters/029-sita-ramam.jpg"
    assert (PROJECT_ROOT / movie["poster_url"].lstrip("/")).is_file()


def test_movie_recommendations_exclude_the_selected_movie():
    recommendations = build_recommender().recommend("Kushi")

    assert len(recommendations) == 6
    assert all(movie["title"] != "Kushi" for movie in recommendations)
    assert all(0 <= movie["similarity"] <= 1 for movie in recommendations)


def test_genre_recommendations_match_selected_genres():
    recommendations = build_recommender().recommend_by_genres(["Romance"])

    assert recommendations
    assert all("Romance" in movie["genres"] for movie in recommendations)


def test_combined_mode_applies_genre_matches():
    recommendations = build_recommender().recommend("Tholi Prema", ["Romance"])

    assert recommendations
    assert all("similarity" in movie for movie in recommendations)
    assert all("matched_genres" in movie for movie in recommendations)


def test_unknown_title_and_empty_genres_are_rejected():
    recommender = build_recommender()

    with pytest.raises(ValueError):
        recommender.recommend("Not a Telugu Movie")

    with pytest.raises(ValueError):
        recommender.recommend_by_genres([])


def test_slugify_is_stable():
    assert slugify("Attarintiki Daredi") == "attarintiki-daredi"
