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
    content_rating = models.CharField(max_length=5, null=True, blank=True)
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
    photo = models.URLField(null=True, blank=True)
    banner = models.URLField(null=True, blank=True)
    trailer = models.URLField(null=True, blank=True)
    year = models.IntegerField(null=False, blank=False)
    imdb = models.FloatField(
        null=False,
        blank=False,
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

    @staticmethod
    def is_watched_by_user(user: User, **kwargs) -> bool:
        return Film.active_objects.active().filter(
            users_watched=user,
            **kwargs
        ).exists()

    @staticmethod
    def is_watchlist_by_user(user: User, **kwargs) -> bool:
        return Film.active_objects.active().filter(
            users_watchlist=user,
            **kwargs
        ).exists()

    @staticmethod
    def is_faved_by_user(user: User, **kwargs) -> bool:
        return Film.active_objects.active().filter(
            users_favorite=user,
            **kwargs
        ).exists()

    def __str__(self):
        return f"Film {self.name} ({str(self.year)})"
