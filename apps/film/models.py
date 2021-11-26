from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, IntegerField
from django.db.models.fields.json import KeyTransform
from django.db.models.functions import Cast

from apps.post.constants import GENRES
from core.models.base import BaseModel

User = get_user_model()


class Artist(BaseModel):
    imdb_id = models.CharField(unique=True, max_length=20, null=False, blank=False)
    name = models.CharField(max_length=30, blank=False, null=False)
    photo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Film(BaseModel):
    imdb_id = models.CharField(unique=True, max_length=20, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    plot = models.TextField(null=True, blank=True)
    content_rating = models.CharField(max_length=10, null=True, blank=True)
    genres = ArrayField(
        models.CharField(max_length=20, blank=True),
        null=True,
        blank=True
    )
    countries = ArrayField(
        models.CharField(max_length=20, blank=True),
        null=True,
        blank=True
    )
    languages = ArrayField(
        models.CharField(max_length=20, blank=True),
        null=True,
        blank=True
    )
    writers = models.ManyToManyField('Artist', related_name='wrote_films')
    directors = models.ManyToManyField('Artist', related_name='directed_films')
    actors = models.ManyToManyField('Artist', related_name='acted_films')
    photo_url = models.URLField(null=True, blank=True)
    banner_url = models.URLField(null=True, blank=True)
    photo = models.ImageField(upload_to='posters', null=True, blank=True)
    banner = models.ImageField(upload_to='banners', null=True, blank=True)
    trailer = models.URLField(null=True, blank=True)
    year = models.IntegerField(null=False, blank=False)
    imdb = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    rotten = models.IntegerField(
        null=True,
        blank=True,
    )
    metacritic = models.IntegerField(
        null=True,
        blank=True,
    )
    time = models.IntegerField(null=True, blank=True, help_text="Film length based on minutes")

    @property
    def watched_count(self) -> int:
        return self.users_watched.count()

    @property
    def watchlist_count(self) -> int:
        return self.users_watchlist.count()

    @property
    def faved_count(self) -> int:
        return self.users_favorite.count()

    @property
    def rate_average(self) -> float:
        return self.posts.all().aggregate(rate_avg=Avg('rate')).get('rate_avg', 0)

    def add_to_watchlist(self, user: User):
        user.films_watchlist.add(self)
        user.films_watched.remove(self)
        user.film_favorites.remove(self)

    def add_to_watched(self, user: User):
        user.films_watched.add(self)
        user.films_watchlist.remove(self)

    def add_to_favorite(self, user: User):
        user.film_favorites.add(self)
        user.films_watched.add(self)
        user.films_watchlist.remove(self)

    def remove_from_watched(self, user: User):
        user.films_watched.remove(self)
        user.film_favorites.remove(self)

    @property
    def genres_average(self) -> dict:
        extracted_genre = {
            genre: Cast(KeyTransform(genre, 'genres'), IntegerField()) for genre in GENRES
        }
        avg = {
            f"{genre}_avg": Avg(genre) for genre in GENRES
        }
        genres_avgs = self.posts.filter(is_active=True).annotate(
            **extracted_genre
        ).aggregate(**avg)
        return {k: v for k, v in genres_avgs.items() if v}

    def is_watched_by_user(self, user: User) -> bool:
        return user in self.users_watched.all()

    def is_watchlist_by_user(self, user: User) -> bool:
        return user in self.users_watchlist.all()

    def is_faved_by_user(self, user: User) -> bool:
        return user in self.users_favorite.all()

    def has_post_by_user(self, user: User) -> bool:
        return self.posts.filter(is_active=True, user=user).exists()

    @staticmethod
    def get_image_from_url(url):
        img_tmp = NamedTemporaryFile(delete=True)
        with urlopen(url=url, timeout=10) as uo:
            assert uo.status == 200
            img_tmp.write(uo.read())
            img_tmp.flush()
        return img_tmp

    def download_photo(self):
        if self.photo_url:
            img = self.get_image_from_url(url=self.photo_url)
            img_file = File(img)
            file_name = self.photo_url.split('/')[-1]
            self.photo.save(file_name, img_file)

    def download_banner(self):
        if self.banner_url:
            img = self.get_image_from_url(url=self.banner_url)
            img_file = File(img)
            file_name = self.banner_url.split('/')[-1]
            self.banner.save(file_name, img_file)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.photo:
            self.download_photo()
        if not self.banner:
            self.download_banner()

    def __str__(self):
        return f"Film {self.name} ({str(self.year)})"
