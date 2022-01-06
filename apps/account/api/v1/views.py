from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, mixins, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rest_framework_simplejwt.tokens import RefreshToken

from apps.film.api.v1.serializers import ListWatchListSerializer, ListWatchedSerializer
from apps.post.api.v1.serializers import SelfPostListSerializer
from . import serializers
from ...models import Profile, PhoneOTP

User = get_user_model()


class AuthViewSet(GenericViewSet):
    queryset = PhoneOTP.active_objects.active()
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.SendOTPSerializer,
        url_name="send_otp",
        url_path="send_otp",
    )
    def send_otp(self, request, *args, **kwargs):
        """
        Sending OTP sms to user phone number
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_existed = User.objects.filter(phone=serializer.validated_data['phone']).exists()
        if user_existed:
            raise ValidationError(
                {'details': 'User with that phone number already existed'}
            )

        unverified_user, created = serializer.save()

        if not created:
            if unverified_user.has_otp:
                raise ValidationError(
                    {'details': 'Try getting otp after 1 min'}
                )

        unverified_user.set_otp()
        return Response(
            self.get_serializer(unverified_user).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["POST"],
        serializer_class=serializers.VerifyOTPSerializer,
        url_name="verify",
        url_path="verify",
    )
    def verify(self, request, *args, **kwargs):
        """
        Verify sent OTP and input OTP with phone number
        """
        existed_otp = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]

        if not existed_otp.has_otp:
            raise ValidationError(
                {'details': 'Your code is expired. Try to get it again'}
            )

        if not existed_otp.check_otp(otp):
            raise ValidationError(
                {'details': 'Entered code is wrong!'}
            )

        existed_otp.verify()

        return Response(
            self.get_serializer(instance=existed_otp).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.RegisterSerializer,
        url_name="register",
        url_path="register",
    )
    def register(self, request, *args, **kwargs):
        """
        Registering new user after validating OTP
        If user was not validated, raises error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        refresh = RefreshToken.for_user(new_user)

        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.LoginSerializer,
        url_name="login",
        url_path="login",
    )
    def login(self, request, *args, **kwargs):
        """
        Login can happen with either username or phone number
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_username = serializer.validated_data.get('phone_username', None)
        password = serializer.validated_data.get('password', None)

        # Finding user with username or phone number
        logged_in_user = get_object_or_404(
            User.active_objects.active(),
            Q(username=phone_username) | Q(phone=phone_username)
        )

        if not logged_in_user.check_password(password):
            return Response(
                {'details': 'Username or password is wrong!'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user=logged_in_user)

        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.UsernameCheckSerializer,
        url_name="check_username",
        url_path="check_username",
    )
    def check_username(self, request, *args, **kwargs):
        """
        API for checking if username is free
        True means that username existed, False means not existed
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check username existence in both active and inactive users to avoid db conflicts ...
        username_exists = User.objects.filter(username__iexact=serializer.validated_data['username']).exists()

        return Response(
            {
                'details': username_exists
            }, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=serializers.ForgetPasswordOTPSerializer,
        url_name="forget_password_otp",
        url_path="forget_password_otp",
    )
    def forget_password_otp(self, request, *args, **kwargs):
        """
        If user had forgotten password. sends OTP to input phonenumber, after that, proceed to verify forget password
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user = get_object_or_404(PhoneOTP.active_objects.active(), phone=phone)

        user.set_otp()

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        serializer_class=serializers.ForgetPasswordSerializer,
        url_name="forget_password_change",
        url_path="forget_password_change",
    )
    def forget_password_change(self, request, *args, **kwargs):
        existed_otp = self.get_object()
        if not existed_otp.is_verified:
            raise ValidationError(
                {'details': 'First verify your phone number'}
            )

        user = get_object_or_404(User.active_objects.active(), phone=existed_otp.phone)

        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "details": "Password changed successfully"
            }, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        serializer_class=serializers.ChangePasswordSerializer,
        url_name="change_password",
        url_path="change_password",
    )
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'details': 'Password changed successfully!'},
            status=status.HTTP_200_OK
        )


class SelfProfileViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):

    serializer_class = serializers.ProfileDetailSerializer
    serializer_classes = {
        'edit': serializers.EditProfileSerializer,
    }
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'profile__name']

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def get_object(self):
        try:
            profile = self.request.user.profile
        except User.profile.RelatedObjectDoesNotExist:
            profile = Profile.objects.create(user=self.request.user)
        return profile

    def list(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["DELETE"],
        url_name="delete",
        url_path="delete",
    )
    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.delete()
        profile.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["PUT", "PATCH"],
        url_name="edit",
        url_path="edit",
    )
    def edit(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=serializers.UserListSerializer,
        url_name="self_followers_list",
        url_path="followers_list",
    )
    def self_followers_list(self, request, *args, **kwargs):
        """
        For seeing current user followers
        """
        followers = self.filter_queryset(request.user.followers.filter(is_active=True))
        page = self.paginate_queryset(followers)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=serializers.UserListSerializer,
        url_name="self_following_list",
        url_path="following_list",
    )
    def self_following_list(self, request, *args, **kwargs):
        """
        For seeing current user followings
        """
        followings = self.filter_queryset(request.user.followings.filter(is_active=True))
        page = self.paginate_queryset(followings)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=SelfPostListSerializer,
        url_name="self_posts",
        url_path="posts",
    )
    def self_posts(self, request, *args, **kwargs):
        posts = request.user.posts.filter(is_active=True)

        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchListSerializer,
        url_name="self_watchlist",
        url_path="watchlist",
    )
    def self_watchlist(self, request, *args, **kwargs):

        films = request.user.films_watchlist.filter(is_active=True)

        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchedSerializer,
        url_name="self_watched",
        url_path="watched",
    )
    def self_watched(self, request, *args, **kwargs):
        search_name = self.request.query_params.get('search', None)

        if search_name:
            films = request.user.films_watched.filter(is_active=True, name__icontains=search_name)
        else:
            films = request.user.films_watched.filter(is_active=True)

        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchedSerializer,
        url_name="self_fave",
        url_path="fav",
    )
    def self_fav(self, request, *args, **kwargs):
        films = request.user.film_favorites.filter(is_active=True)
        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class OtherProfileViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = serializers.OtherProfileDetailSerializer
    queryset = User.active_objects.active()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'profile__name']

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(self.get_queryset(), id=user_id)
        return user

    def list(self, request, *args, **kwargs):
        try:
            profile = self.get_object().profile
        except User.profile.RelatedObjectDoesNotExist:
            profile = Profile.objects.create(user=self.get_object())

        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=serializers.UserListSerializer,
        url_name="other_followers_list",
        url_path="followers_list",
    )
    def other_followers_list(self, request, *args, **kwargs):
        """
        For seeing current user followers
        """
        user_followers = self.filter_queryset(self.get_object().followers.filter(is_active=True))
        page = self.paginate_queryset(user_followers)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=serializers.UserListSerializer,
        url_name="other_following_list",
        url_path="following_list",
    )
    def other_following_list(self, request, *args, **kwargs):
        """
        For seeing current user followings
        """
        user_followings = self.filter_queryset(self.get_object().followings.filter(is_active=True))
        page = self.paginate_queryset(user_followings)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=SelfPostListSerializer,
        url_name="other_posts",
        url_path="posts",
    )
    def other_posts(self, request, *args, **kwargs):
        posts = self.get_object().posts.filter(is_active=True)

        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchListSerializer,
        url_name="other_watchlist",
        url_path="watchlist",
    )
    def other_watchlist(self, request, *args, **kwargs):
        films = self.get_object().films_watchlist.filter(is_active=True)

        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchedSerializer,
        url_name="other_watched",
        url_path="watched",
    )
    def other_watched(self, request, *args, **kwargs):
        search_name = self.request.query_params.get('search', None)

        if search_name:
            films = self.get_object().films_watched.filter(is_active=True, name__icontains=search_name)
        else:
            films = self.get_object().films_watched.filter(is_active=True)

        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=ListWatchedSerializer,
        url_name="other_fave",
        url_path="fav",
    )
    def other_fav(self, request, *args, **kwargs):
        films = self.get_object().film_favorites.filter(is_active=True)

        page = self.paginate_queryset(films)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class FollowViewSet(GenericViewSet):
    queryset = User.active_objects.active()

    @action(
        detail=True,
        methods=["POST"],
        url_name="follow",
        url_path="follow",
    )
    def follow(self, request, *args, **kwargs):
        user = request.user
        following_user = self.get_object()
        if user == following_user:
            return Response(
                {'details': 'You cant follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.follow(following_user)

        return Response(
            {'details': 'Followed'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="unfollow",
        url_path="unfollow",
    )
    def unfollow(self, request, *args, **kwargs):
        user = request.user
        unfollowing_user = self.get_object()
        if user == unfollowing_user:
            return Response(
                {'details': 'You cant unfollow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.unfollow(unfollowing_user)

        return Response(
            {'details': 'Unfollowed'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["POST"],
        url_name="remove_follower",
        url_path="remove_follower",
    )
    def remove_follower(self, request, *args, **kwargs):
        user = request.user
        removing_user = self.get_object()
        if user == removing_user:
            return Response(
                {'details': 'You cant remove yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.remove_follower(removing_user)

        return Response(
            {'details': 'Unfollowed'},
            status=status.HTTP_200_OK
        )


class SearchViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    """
    Search in users
    Search fields are username, first_name, last_name
    """
    serializer_class = serializers.UserListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'profile__name']

    def get_queryset(self):
        user = self.request.user
        return User.active_objects.active().exclude(id=user.id).order_by('-created_time')
