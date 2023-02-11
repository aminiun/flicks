import re
from typing import Optional

from django.conf import settings

from core.utils.api import ApiCall
from . import constants


class IMDBApiCall:

    def __init__(self):
        self.search_url = f"{constants.IMDB_API_URL}/en/API/SearchMovie/{settings.IMDB_API_KEY}/"
        self.fetch_url = f"{constants.IMDB_API_URL}/en/API/Title/{settings.IMDB_API_KEY}/"

    def _imdb_call(self, url: str) -> dict:
        res = ApiCall.api_call(
            method="get",
            url=url,
            expected_status=200
        )
        return res.json()

    def _extract_year(self, film: dict) -> Optional[str]:
        """
        Year in search result is sth like (2010)
        """
        try:
            return re.findall("\((\d{4})\)", film['description'])[0]
        except IndexError:
            return None

    def _get_proper_image_size(self, image_link: str, type_: str):
        """
        Cropping and making photos smaller
        """
        if not image_link:
            return None
        if "nopicture" in image_link:
            return None

        try:
            image_id = re.findall(r"/original/([^\.]*)", image_link)[0]
        except IndexError:
            return None

        types = {
            'actor': constants.IMAGE_SIZE,
            'poster': constants.FILM_SIZE,
        }

        return f"{constants.AMAZON_IMAGE_LINK}{image_id}{types.get(type_)}"

    def _get_proper_poster_size(self, image_id: str, type_: str):
        """
        Cropping and making photos smaller
        """
        types = {
            'poster': constants.POSTER_WIDTH,
            'banner': constants.BANNER_WIDTH,
        }
        return f"{constants.TMDB_IMAGE_LINK}{types.get(type_)}/{image_id}"

    def _list_poster(self, image_link: str):
        return self._get_proper_image_size(image_link, type_='poster')

    def search(self, film: str) -> list:
        url = self.search_url + film
        found_films = self._imdb_call(url)['results']

        return [
            {
                'imdb_id': found_film.get('id', None),
                'name': found_film.get('title', None),
                'photo': self._list_poster(found_film['image']),
                'year': self._extract_year(found_film),
            }
            for found_film in found_films
        ]

    def _get_in_list_format(self, attrs: list):
        return [attr['value'] for attr in attrs]

    def _get_in_list_of_dict_format(self, attrs: list):
        return [{
            'imdb_id': attr['id'],
            'name': attr['name'],
            'photo': self._get_proper_image_size(image_link=attr.get('image', None), type_='actor'),
        } for attr in attrs]

    def _get_nested_value(self, attr: dict, what_to_get: str):
        if not attr:
            return None

        nested_value = attr.get(what_to_get, None)
        return nested_value if nested_value else None

    def fetch(self, imdb_id: str) -> dict:
        url = self.fetch_url + imdb_id + "/Trailer,Ratings,Posters,"
        found_film = self._imdb_call(url)

        languages = self._get_in_list_format(found_film.get('languageList', None))
        countries = self._get_in_list_format(found_film.get('countryList', None))
        genres = self._get_in_list_format(found_film.get('genreList', None))

        writers = self._get_in_list_of_dict_format(found_film.get('writerList', None))
        directors = self._get_in_list_of_dict_format(found_film.get('directorList', None))
        actors = self._get_in_list_of_dict_format(found_film.get('actorList', None))

        rotten = self._get_nested_value(found_film.get('ratings', None), 'rottenTomatoes')
        trailer = self._get_nested_value(found_film.get('trailer', None), 'link')

        try:
            photo = self._get_proper_poster_size(
                image_id=found_film['posters']['posters'][0]['id'],
                type_='poster'
            )
        except (IndexError, KeyError):
            photo = None

        try:
            banner = self._get_proper_poster_size(
                image_id=found_film['posters']['backdrops'][0]['id'],
                type_='banner'
            )
        except (IndexError, KeyError):
            banner = None

        return {
            'imdb_id': imdb_id,
            'plot': found_film.get('plot', None),
            'name': found_film.get('title', None),
            'year': found_film.get('year', None),
            'photo_url': photo,
            'banner_url': banner,
            'time': found_film.get('runtimeMins', None) or None,
            'writers': writers,
            'directors': directors,
            'actors': actors[:constants.ACTORS_COUNT],
            'imdb': found_film.get('imDbRating', None) or None,
            'rotten': rotten,
            'metacritic': found_film.get('metacriticRating', None) or None,
            'languages': languages,
            'countries': countries,
            'trailer': trailer,
            'content_rating': found_film.get('contentRating', None),
            'genres': genres,
        }
