from rest_framework import serializers

from apps.account.api.v1.serializers import UserListSerializer
from apps.film.models import Film, Artist
from apps.post.models import Post


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = [
            'id',
            'name',
            'photo',
        ]


class FilmListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = [
            "id",
            "photo",
        ]
        read_only_fields = fields


class FilmPostsSerializer(serializers.ModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'genres',
            'rate',
            'caption',
        ]


class FilmDetailSerializer(serializers.ModelSerializer):
    actors = serializers.SerializerMethodField()
    writers = ArtistSerializer(many=True)
    directors = ArtistSerializer(many=True)

    class Meta:
        model = Film
        fields = [
            "id",
            "imdb_id",
            "name",
            "writers",
            "directors",
            "actors",
            "photo",
            "banner",
            "year",
            "time",
            "imdb",
            "rotten",
            "metacritic",
            "rate_average",
            "genres_average",
            "plot",
            "content_rating",
            "genres",
            "countries",
            "languages",
            "writers",
            "directors",
            "trailer",
        ]
        extra_kwargs = {
            'imdb_id': {'write_only': True}
        }

    def get_actors(self, obj):
        actors = obj.actors.all().order_by('created_time')
        return ArtistSerializer(actors, many=True).data


class ListWatchListSerializer(FilmListSerializer):
    pass


class ListWatchedSerializer(FilmListSerializer):
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)

    class Meta(FilmListSerializer.Meta):
        fields = FilmListSerializer.Meta.fields + [
            'name',
            'year',
            'imdb',
            'is_watched',
            'is_watchlist',
        ]

    def get_is_watched(self, obj):
        user = self.context.get('request').user
        return Film.is_watched_by_user(user=user, id=obj.id)

    def get_is_watchlist(self, obj):
        user = self.context.get('request').user
        return Film.is_watchlist_by_user(user=user, id=obj.id)


class IMDBListSerializer(serializers.Serializer):
    imdb_id = serializers.CharField()
    photo = serializers.URLField(allow_null=True)
    year = serializers.CharField(allow_null=True)
    name = serializers.CharField()
    watched_count = serializers.SerializerMethodField(read_only=True)
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = [
            'imdb_id',
            'name',
            'year',
            'photo',
            'watched_count',
            'is_watched',
            'is_watchlist',
        ]
        # read_only_true = fields

    def _film_obj(self, obj):
        try:
            return Film.active_objects.active().prefetch_related(
                'users_watched'
            ).get(
                imdb_id=obj.get('imdb_id')
            )
        except Film.DoesNotExist:
            return None

    def get_watched_count(self, obj):
        film = self._film_obj(obj)
        if not film:
            return 0

        return film.watched_count

    def get_is_watched(self, obj):
        user = self.context.get('request').user
        return Film.is_watched_by_user(user=user, imdb_id=obj.get('imdb_id'))

    def get_is_watchlist(self, obj):
        user = self.context.get('request').user
        return Film.is_watchlist_by_user(user=user, imdb_id=obj.get('imdb_id'))


class FetchIMDBFilmSerializer(serializers.Serializer):
    imdb_id = serializers.CharField(required=True)

    class Meta:
        fields = [
            'imdb_id',
        ]


class FilmCreatedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = [
            'id'
        ]
