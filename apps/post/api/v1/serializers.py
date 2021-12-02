from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.film.models import Film
from apps.post.constants import GENRES, MAX_GENRE_VALUE
from apps.post.models import Post

User = get_user_model()


class PostFilmSerializer(serializers.ModelSerializer):
    is_watched = serializers.SerializerMethodField(read_only=True)
    is_watchlist = serializers.SerializerMethodField(read_only=True)
    is_fav = serializers.SerializerMethodField(read_only=True)
    has_post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Film
        fields = (
            'id',
            'photo',
            'banner',
            'year',
            'name',
            'is_watched',
            'is_watchlist',
            'is_fav',
            'has_post',
        )

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


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'film',
            'genres',
            'rate',
            'caption',
            'quote',
        ]

    def validate_genres(self, value):
        if not value or not isinstance(value, dict):
            raise ValidationError(
                'Invalid genre'
            )

        for genre, rate in value.items():
            if genre not in GENRES:
                raise ValidationError(
                    f'No genre called {genre}'
                )

            if rate > MAX_GENRE_VALUE:
                raise ValidationError(
                    f'Invalid value for {genre}'
                )

        return value

    def validate(self, attrs):
        user = self.context['request'].user
        validated_data = super().validate(attrs)
        if validated_data['film'].has_post_by_user(user=user):
            raise ValidationError(
                {"details": "You already have post for this film"}
            )

        return validated_data

    def create(self, validated_data):
        film = validated_data['film']

        request = self.context.get('request', None)
        if request:
            user = request.user
            user.films_watched.add(film)

        return super().create(validated_data)


class PostDetailSerializer(serializers.ModelSerializer):
    film = PostFilmSerializer()

    class Meta:
        model = Post
        fields = [
            'id',
            'film',
            'genres',
            'rate',
            'caption',
            'quote',
        ]


class SelfPostListSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(source='film.photo', default=None)

    class Meta:
        model = Post
        fields = [
            'id',
            'rate',
            'photo',
            'genres',
        ]


class PostListSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(source='film.photo', default=None)

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'rate',
            'photo',
            'genres',
        ]


class PostUpdateSerializer(PostDetailSerializer):

    film = PostFilmSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'film',
            'genres',
            'rate',
            'caption',
            'quote',
        ]

    def validate_genres(self, value):
        if not value or not isinstance(value, dict):
            raise ValidationError(
                'Invalid genre'
            )

        for genre, rate in value.items():
            if genre not in GENRES:
                raise ValidationError(
                    f'No genre called {genre}'
                )

            if rate > MAX_GENRE_VALUE:
                raise ValidationError(
                    f'Invalid value for {genre}'
                )

        return value
