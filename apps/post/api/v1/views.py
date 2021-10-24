from django.contrib.auth import get_user_model
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.post.api.v1 import serializers
from apps.post.models import Post

User = get_user_model()


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):

    serializer_classes = {
        'update': serializers.PostUpdateSerializer,
        'partial_update': serializers.PostUpdateSerializer,
        'create': serializers.PostCreateSerializer,
        'list': serializers.PostListSerializer,
        'retrieve': serializers.PostDetailSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return Post.active_objects.active().filter(user__in=user.followings.filter(is_active=True))

        if self.action == 'retrieve':
            return Post.active_objects.active()

        return Post.active_objects.active().filter(user=user)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
