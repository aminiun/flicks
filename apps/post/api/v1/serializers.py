from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.film.models import Film
from apps.post.constants import GENRES, MAX_GENRE_VALUE
from apps.post.models import Post

User = get_user_model()


class PostFilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = (
            'id',
            'photo',
            'year',
            'name',
        )


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

    class Meta(PostDetailSerializer.Meta):
        read_only_fields = [
            'film',
        ]
