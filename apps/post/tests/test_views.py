import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.film.models import Film
from apps.post.models import Post

User = get_user_model()


@pytest.mark.django_db
class TestPostViewSet:

    @pytest.fixture()
    def user(self):
        return User.objects.create_user(
            username="test",
            password="test",
            phone="09191234567"
        )

    @pytest.fixture()
    def client(self, client, user):
        client.force_login(user)
        return client

    @pytest.fixture()
    def film(self):
        return Film.objects.create(name="film", year="2020")

    @pytest.fixture()
    def following_user(self, user):
        following_user = User.objects.create(username="follower", phone="09121112233")
        user.followings.add(following_user)
        return following_user

    @pytest.fixture()
    def post_from_following(self, film, following_user):
        return Post.objects.create(
            user=following_user,
            film=film,
            genres={}
        )

    def test_get_post_list_return_just_followings_posts(self, client, post_from_following):
        res = client.get(
            reverse("posts-list")
        )
        assert res.status_code == 200
        assert len(res.json()["results"]) == 1
        assert res.json()["results"][0]["id"] == post_from_following.id

    def test_get_post_detail_success(self, client, post_from_following):
        res = client.get(
            reverse("posts-detail", kwargs={"pk": post_from_following.id})
        )
        assert res.status_code == 200
        assert res.json()["id"] == post_from_following.id

    def test_create_post_success(self, client, film):
        res = client.post(
            reverse("posts-list"),
            data={
                "film": film.id,
                "genres": json.dumps({
                    "drama": 5,
                    "horror": 3
                })
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        assert res.status_code == 201
        film.refresh_from_db()
        assert film.posts.last()

    def test_create_post_with_invalid_genre_fail_400(self, client, film):
        res = client.post(
            reverse("posts-list"),
            data={
                "film": film.id,
                "genres": {"test": 10}
            }
        )
        assert res.status_code == 400
