from django.core.management.base import BaseCommand

from apps.film import constants
from apps.film.models import Film
from django.conf import settings

from core.utils.api import ApiCall


class Command(BaseCommand):
    help = 'Downloading posters and banners of films'

    def handle(self, *args, **options):
        for film in Film.active_objects.filter(genres__isnull=True):
            url = f"{constants.IMDB_API_URL}/en/API/Title/{settings.IMDB_API_KEY}/" + film.imdb_id

            res = ApiCall.api_call(
                method="get",
                url=url,
                expected_status=200
            )

            genres = [attr['value'] for attr in res.json().get('genreList', None)]

            film.genres = genres
            film.save()

            self.stdout.write(self.style.SUCCESS('Genre added successfully "%s"' % film.name))
