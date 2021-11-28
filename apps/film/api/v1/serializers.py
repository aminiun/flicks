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
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)
    is_fav = serializers.SerializerMethodField(read_only=True)
    has_post = serializers.SerializerMethodField(read_only=True)

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
            'is_watched',
            'is_watchlist',
            'is_fav',
            'has_post',
        ]
        extra_kwargs = {
            'imdb_id': {'write_only': True}
        }

    def get_actors(self, obj):
        actors = obj.actors.all().order_by('created_time')
        return ArtistSerializer(actors, many=True).data

    def get_is_watched(self, obj):
        user = self.context.get('request').user
        return obj.is_watched_by_user(user=user)

    def get_is_watchlist(self, obj):
        user = self.context.get('request').user
        return obj.is_watchlist_by_user(user=user)

    def get_is_fav(self, obj):
        user = self.context.get('request').user
        return obj.is_faved_by_user(user=user)

    def get_has_post(self, obj):
        user = self.context.get('request').user
        return obj.has_post_by_user(user=user)


class ListWatchListSerializer(FilmListSerializer):
    pass


class ListWatchedSerializer(FilmListSerializer):
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)
    is_fav = serializers.SerializerMethodField(read_only=True)
    has_post = serializers.SerializerMethodField(read_only=True)

    class Meta(FilmListSerializer.Meta):
        fields = FilmListSerializer.Meta.fields + [
            'name',
            'year',
            'imdb',
            'is_watched',
            'is_watchlist',
            'is_fav',
            'has_post',
        ]

    def get_is_watched(self, obj):
        user = self.context.get('request').user
        return obj.is_watched_by_user(user=user)

    def get_is_watchlist(self, obj):
        user = self.context.get('request').user
        return obj.is_watchlist_by_user(user=user)

    def get_is_fav(self, obj):
        user = self.context.get('request').user
        return obj.is_faved_by_user(user=user)

    def get_has_post(self, obj):
        user = self.context.get('request').user
        return obj.has_post_by_user(user=user)


class IMDBListSerializer(serializers.Serializer):
    imdb_id = serializers.CharField()
    photo = serializers.URLField(allow_null=True)
    year = serializers.CharField(allow_null=True)
    name = serializers.CharField()
    watched_count = serializers.SerializerMethodField(read_only=True)
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)
    is_fav = serializers.SerializerMethodField(read_only=True)
    has_post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = [
            'imdb_id',
            'name',
            'year',
            'photo',
            'watched_count',
            'is_watched',
            'is_watchlist',
            'is_fav',
            'has_post',
        ]
        # read_only_true = fields

    def _film_obj(self, obj) -> Film:
        try:
            return Film.active_objects.active().prefetch_related(
                'users_watched',
                'users_watchlist',
                'users_favorite',
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
        film = self._film_obj(obj)
        if not film:
            return False
        return film.is_watched_by_user(user=user)

    def get_is_watchlist(self, obj):
        user = self.context.get('request').user
        film = self._film_obj(obj)
        if not film:
            return False
        return film.is_watchlist_by_user(user=user)

    def get_is_fav(self, obj):
        user = self.context.get('request').user
        film = self._film_obj(obj)
        if not film:
            return False
        return film.is_faved_by_user(user=user)

    def get_has_post(self, obj):
        user = self.context.get('request').user
        film = self._film_obj(obj)
        if not film:
            return False
        return film.has_post_by_user(user=user)


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
