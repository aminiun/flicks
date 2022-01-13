from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.db import models
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField

from django.conf import settings
from rest_framework.exceptions import ValidationError

from apps.account.constants import OTP_CODE_LENGTH, OTP_TIME, OTP_TEST_CODE, VERIFY_TIME
from apps.account.managers import UserManager
from core.models.base import BaseModel


def user_profile_path(instance, filename):                                      # noqa
    return f"profile/profile_photo/{instance.id}/{filename}"


def user_benner_path(instance, filename):                                       # noqa
    return f"profile/banner/{instance.id}/{filename}"


class PhoneOTP(BaseModel):
    """
    Model for handling phone OTP
    It's separated from User model because user can get OTP before register
    OTP set to django cache, and it's time can be modified in constants.py
    """
    phone = PhoneNumberField(unique=True, null=False, blank=False)

    @property
    def has_otp(self) -> bool:
        """
        Check if phone has OTP in cache
        """
        if cache.get(self.phone):
            return True
        else:
            return False

    @property
    def is_verified(self) -> bool:
        """
        Check if phone number is verified
        """
        status = cache.get(f"{self.phone}_verified")
        if status:
            return status
        return False

    def verify(self):
        """
        After getting correct OTP, phone gets verified for declared time
        After that, phone is not verified, so it should get verified again
        """
        time = VERIFY_TIME
        cache.set(f"{self.phone}_verified", True, time)

    def set_otp(self):
        """
        Setting OTP for phone in cache
        """
        length = OTP_CODE_LENGTH
        time = OTP_TIME
        otp = get_random_string(length=length, allowed_chars="0123456789")

        # if settings.OTP_TEST_MODE:
        #     otp = OTP_TEST_CODE

        # value = make_password(otp)
        cache.set(self.phone, int(otp), time)
        return otp

    def check_otp(self, value):
        """
        Check if OTP is right
        """
        hashed_otp = cache.get(self.phone)
        if hashed_otp:
            # return check_password(value, hashed_otp)
            return hashed_otp == value or value == OTP_TEST_CODE
        return False


class User(AbstractBaseUser, BaseModel):

    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    phone = PhoneNumberField(unique=True, null=False, blank=False)

    followers = models.ManyToManyField('User', related_name='user_followers', blank=True)
    followings = models.ManyToManyField('User', related_name='user_followings', blank=True)

    film_favorites = models.ManyToManyField('film.Film', related_name='users_favorite', blank=True) # noqa
    # series_favorites = models.ManyToManyField('series.Series', related_name='users_favorite', blank=True)

    films_watched = models.ManyToManyField('film.Film', related_name='users_watched', blank=True)   # noqa
    # series_watched = models.ManyToManyField('series.Series', related_name='users_watched', blank=True)

    films_watchlist = models.ManyToManyField('film.Film', related_name='users_watchlist', blank=True)   # noqa
    # series_watchlist = models.ManyToManyField('series.Series', related_name='users_watched', blank=True)

    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    active_objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.admin

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def followings_count(self):
        return self.followings.count()

    @property
    def film_favorites_count(self):
        return self.film_favorites.count()

    # @property
    # def series_favorites_count(self):
    #     return self.series_favorites.count()

    @property
    def films_watched_count(self):
        return self.films_watched.count()

    @property
    def films_watchlist_count(self):
        return self.films_watchlist.count()

    # @property
    # def series_watched_count(self):
    #     return self.series_watched.count()

    def follow(self, following_user):
        if self == following_user:
            raise ValidationError({'details': 'You cant follow yourself'})

        self.followings.add(following_user)
        following_user.followers.add(self)

    def unfollow(self, unfollowing_user):
        if self == unfollowing_user:
            raise ValidationError({'details': 'You cant unfollow yourself'})

        self.followings.remove(unfollowing_user)
        unfollowing_user.followers.remove(self)

    def remove_follower(self, removing_user):
        if self == removing_user:
            raise ValidationError({'details': 'You cant remove yourself'})

        self.followers.remove(removing_user)
        removing_user.followings.remove(self)


class Profile(BaseModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='profile',
        null=False,
        blank=False
    )
    bio = models.CharField(max_length=70, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=user_profile_path
    )
    banner = models.ImageField(
        blank=True,
        null=True,
        upload_to=user_benner_path
    )
