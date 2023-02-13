import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.film.models import Film


User = get_user_model()


@pytest.mark.django_db
class TestWatchListViewSet:

    @pytest.fixture()
    def user(self):
        return User.objects.create_user(
            username="test",
            password="test",
            phone="09191234567"
        )

    @pytest.fixture()
    def film(self):
        return Film.objects.create(name="film", year="2020")

    @pytest.fixture()
    def client(self, client, user):
        client.force_login(user)
        return client

    def test_add_watch_list_then_removed_from_watched_success(self, user, film, client):
        user.films_watched.add(film)
        res = client.post(
            reverse("watchlist-add", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film in user.films_watchlist.all()
        assert film not in user.films_watched.all()

    def test_remove_watch_list_success(self, user, film, client):
        user.films_watchlist.add(film)
        res = client.post(
            reverse("watchlist-remove", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film not in user.films_watchlist.all()


@pytest.mark.django_db
class TestWatchedViewSet:

    @pytest.fixture()
    def user(self):
        return User.objects.create_user(
            username="test",
            password="test",
            phone="09191234567"
        )

    @pytest.fixture()
    def film(self):
        return Film.objects.create(name="film", year="2020")

    @pytest.fixture()
    def client(self, client, user):
        client.force_login(user)
        return client

    def test_add_watched_then_removed_from_watch_list_success(self, user, film, client):
        user.films_watchlist.add(film)
        res = client.post(
            reverse("watched-add", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film in user.films_watched.all()
        assert film not in user.films_watchlist.all()

    def test_remove_watched_then_remove_from_fav_success(self, user, film, client):
        user.films_watched.add(film)
        user.film_favorites.add(film)
        res = client.post(
            reverse("watched-remove", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film not in user.films_watched.all()
        assert film not in user.film_favorites.all()


@pytest.mark.django_db
class TestFavViewSet:

    @pytest.fixture()
    def user(self):
        return User.objects.create_user(
            username="test",
            password="test",
            phone="09191234567"
        )

    @pytest.fixture()
    def film(self):
        return Film.objects.create(name="film", year="2020")

    @pytest.fixture()
    def client(self, client, user):
        client.force_login(user)
        return client

    def test_add_fav_then_added_to_watched_success(self, user, film, client):
        res = client.post(
            reverse("fav-add", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film in user.films_watched.all()
        assert film in user.film_favorites.all()

    def test_remove_fav_success(self, user, film, client):
        user.film_favorites.add(film)
        res = client.post(
            reverse("fav-remove", kwargs={"pk": film.id})
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert film not in user.film_favorites.all()
