from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from core.models.base import BaseModel


class Post(BaseModel):
    user = models.ForeignKey(
        "account.User",
        related_name="posts",
        blank=True,
        on_delete=models.CASCADE
    )
    film = models.ForeignKey(
        "film.Film",
        related_name="posts",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    genres = models.JSONField(null=False, blank=False)
    # series = models.ForeignKey(
    #     "series.Series",
    #     related_name="posts",
    #     null=True,
    #     blank=True,
    #     on_delete=models.CASCADE
    # )

    rate = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    caption = models.TextField(null=True, blank=True)
    quote = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        # if not self.series:
        return f"{str(self.user)} post for film {str(self.film)}"

        # return f"{str(self.user)} post for series {str(self.series)}"
