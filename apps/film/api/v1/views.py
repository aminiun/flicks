from django.db.models import Count
from rest_framework import mixins, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.film.api.v1 import serializers
from apps.film.models import Film, Artist
from apps.film.utils import IMDBApiCall
from apps.post.models import Post
from core.pagination import CustomLimitOffsetPagination


class WatchListViewSet(GenericViewSet):
    queryset = Film.active_objects.active()

    @action(
        detail=True,
        methods=["POST"],
        url_name="add",
        url_path="add",
    )
    def add(self, request, *args, **kwargs):
        selected_film = self.get_object()
        selected_film.add_to_watchlist(user=self.request.user)

        return Response(
            {'details': 'added'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="remove",
        url_path="remove",
    )
    def remove(self, request, *args, **kwargs):
        selected_film = self.get_object()
        self.request.user.films_watchlist.remove(selected_film)

        return Response(
            {'details': 'removed'},
            status=status.HTTP_200_OK
        )


class WatchedViewSet(GenericViewSet):
    queryset = Film.active_objects.active()

    @action(
        detail=True,
        methods=["POST"],
        url_name="add",
        url_path="add",
    )
    def add(self, request, *args, **kwargs):
        selected_film = self.get_object()
        selected_film.add_to_watched(user=self.request.user)

        return Response(
            {'details': 'added'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="remove",
        url_path="remove",
    )
    def remove(self, request, *args, **kwargs):
        selected_film = self.get_object()
        selected_film.remove_from_watched(user=self.request.user)

        if Film.has_post_by_user(user=self.request.user):
            posts = Post.objects.get(user=self.request.user, film=selected_film)
            posts.delete()

        return Response(
            {'details': 'removed'},
            status=status.HTTP_200_OK
        )


class FavViewSet(GenericViewSet):
    queryset = Film.active_objects.active()

    @action(
        detail=True,
        methods=["POST"],
        url_name="add",
        url_path="add",
    )
    def add(self, request, *args, **kwargs):
        selected_film = self.get_object()
        selected_film.add_to_favorite(user=self.request.user)

        return Response(
            {'details': 'added'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="remove",
        url_path="remove",
    )
    def remove(self, request, *args, **kwargs):
        selected_film = self.get_object()
        self.request.user.film_favorites.remove(selected_film)

        return Response(
            {'details': 'removed'},
            status=status.HTTP_200_OK
        )


class SearchViewSet(GenericViewSet):
    """
    Search in films
    """

    serializer_class = serializers.IMDBListSerializer

    filter_backends = [filters.SearchFilter]

    def list(self, request, *args, **kwargs):
        query_params = self.request.query_params.get('search', None)
        if not query_params:
            raise ValidationError(
                {"details": "Specify search param"}
            )

        found_films = IMDBApiCall().search(
            film=query_params
        )
        serializer = self.get_serializer(data=found_films, many=True)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FilmViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):

    serializer_classes = {
        'list': serializers.ListWatchedSerializer,
        'retrieve': serializers.FilmDetailSerializer,
        'create': serializers.FetchIMDBFilmSerializer,
    }
    queryset = Film.active_objects.active().prefetch_related(
        'users_watched',
        'users_favorite',
        'posts',
    ).annotate(
        watched=Count('users_watched'),
        fav=Count('users_favorite'),
        post=Count('posts'),
    )

    pagination_class = CustomLimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['imdb', 'fav', 'watched', 'post']

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def create(self, request, *args, **kwargs):
        """
        Fetching film from IMDB and saving it in db
        If id already exists in db, nothing would be saved
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        out_serializer = serializers.FilmCreatedSerializer

        imdb_id = serializer.validated_data['imdb_id']

        # If film exists, just return that from db and don't fetch it again from api
        film_exists = Film.active_objects.active().filter(imdb_id=imdb_id)
        if film_exists:
            return Response(
                out_serializer(instance=film_exists[0]).data,
                status=status.HTTP_200_OK
            )

        found_film = IMDBApiCall().fetch(imdb_id)

        actors = [
            Artist.objects.get(imdb_id=actor['imdb_id']) or Artist.objects.create(**actor)
            for actor in found_film.pop('actors', None)
        ]
        writers = [
            Artist.objects.get(imdb_id=writer['imdb_id']) or Artist.objects.create(**writer)
            for writer in found_film.pop('writers', None)
        ]
        directors = [
            Artist.objects.get(imdb_id=director['imdb_id']) or Artist.objects.create(**director)
            for director in found_film.pop('directors', None)
        ]

        created_film = Film.objects.create(**found_film)
        created_film.actors.add(*actors)
        created_film.writers.add(*writers)
        created_film.directors.add(*directors)

        return Response(
            out_serializer(instance=created_film).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["GET"],
        serializer_class=serializers.FilmPostsSerializer,
        url_name="posts",
        url_path="posts",
    )
    def posts(self, request, *args, **kwargs):
        """
        Showing the posts of a film
        First the posts of followings come, then the other posts
        """
        film = self.get_object()
        user = request.user

        # Getting followings posts
        followings_film_posts = film.posts.filter(
            is_active=True,
            user__followers=user
        ).exclude(caption=None)

        # Getting all users posts about film and exclude followings posts
        not_followings_film_posts = film.posts.filter(
            is_active=True
        ).exclude(id__in=followings_film_posts)

        # Combining two queryset
        posts = followings_film_posts.union(not_followings_film_posts, all=True)

        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
