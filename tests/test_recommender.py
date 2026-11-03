from pathlib import Path
import xml.etree.ElementTree as ET

from app import MovieRecommender, slugify


def build_recommender():
    return MovieRecommender(Path(__file__).resolve().parents[1] / "data" / "movies.csv")


def test_catalog_has_35_unique_titles_with_poster_sources():
    recommender = build_recommender()
    assert recommender.movie_count == 35
    assert len(recommender.index) == 35
    assert all(movie["poster_url"] or movie["poster_alt_url"] for movie in recommender.all_movies())


def test_pawan_kalyan_fan_shelf_has_six_films():
    titles = {movie["title"] for movie in build_recommender().power_star_movies()}
    assert titles == {
        "Tholi Prema", "Kushi", "Jalsa", "Gabbar Singh",
        "Attarintiki Daredi", "Bheemla Nayak",
    }

def test_movie_years_are_formatted_without_decimal_suffix():
    recommender = build_recommender()
    assert recommender.get_movie("Kushi")["year"] == "2001"
    assert recommender.get_movie("Bheemla Nayak")["year"] == "2022"


def test_sita_ramam_uses_telugu_poster_and_has_alternate_source():
    movie = build_recommender().get_movie("Sita Ramam")
    assert "amazon.com" in movie["poster_url"]
    assert "filmaffinity.com" in movie["poster_alt_url"]


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
    try:
        recommender.recommend("Not a Telugu Movie")
        assert False, "Expected ValueError"
    except ValueError:
        pass
    try:
        recommender.recommend_by_genres([])
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_slugify_is_stable():
    assert slugify("Attarintiki Daredi") == "attarintiki-daredi"
