from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import Profile, PhoneOTP

User = get_user_model()


class OTPSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(required=True)

    class Meta:
        model = PhoneOTP
        fields = [
            'id',
            'phone'
        ]


class SendOTPSerializer(OTPSerializer):

    def create(self, validated_data):
        """
        If OTP already has been sent to user, just returns it's model to resend OTP
        """
        existed_otp = PhoneOTP.objects.filter(phone=validated_data['phone'])

        if existed_otp:
            return existed_otp.first(), False

        return PhoneOTP.objects.create(
            phone=validated_data['phone'],
        ), True


class VerifyOTPSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = PhoneOTP
        fields = [
            'id',
            'otp',
        ]


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'phone',
            'username',
            'password',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        verified_user = PhoneOTP.active_objects.active().filter(phone=attrs['phone'])

        # Check if user has been verified or not
        if not verified_user or not verified_user.first().is_verified:
            raise ValidationError(
                {'details': 'first verify phone number'}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            phone=validated_data['phone'],
            username=validated_data['username'],
            password=validated_data['password'],
        )


class LoginSerializer(serializers.ModelSerializer):
    phone_username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'phone_username',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)

    class Meta:
        fields = [
            'username',
        ]


class ForgetPasswordOTPSerializer(OTPSerializer):

    def validate(self, attrs):
        """
        Make sure that user with that phone already registered
        """
        attrs = super().validate(attrs)

        get_object_or_404(User.active_objects.active(), phone=attrs['phone'])

        return attrs


class ForgetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'password',
        ]

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'old_password',
            'password'
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context.get('request').user
        if not user.check_password(attrs['old_password']):
            raise ValidationError(
                {'old_password': 'Wrong password!'}
            )
        return attrs

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance


class EditProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)

    class Meta:
        model = Profile
        fields = [
            'bio',
            'name',
            'photo',
            'banner',
            'username',
        ]

    def validate(self, attrs):
        self_user = self.context['request'].user
        new_user = attrs.get('user', None)
        if new_user:
            username = new_user.get('username')
            if User.objects.filter(username=username).exclude(id=self_user.id).exists():
                raise ValidationError(
                    {'details': 'username already exists'}
                )
        return super().validate(attrs=attrs)

    def update(self, instance, validated_data):
        try:
            username = validated_data.pop('user')['username']
            instance.user.username = username
            instance.user.save()
        except KeyError:
            pass

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProfileDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    followers_count = serializers.IntegerField(source='user.followers_count', read_only=True)
    followings_count = serializers.IntegerField(source='user.followings_count', read_only=True)
    films_watched_count = serializers.IntegerField(source='user.films_watched_count', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'bio',
            'name',
            'photo',
            'banner',
            'username',
            'followers_count',
            'followings_count',
            'films_watched_count',
        ]


class OtherProfileDetailSerializer(ProfileDetailSerializer):
    is_followed = serializers.SerializerMethodField()

    class Meta(ProfileDetailSerializer.Meta):
        fields = ProfileDetailSerializer.Meta.fields + ["is_followed"]

    def get_is_followed(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            return user.followings.filter(id=obj.user.id).exists()


class UserListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name')
    photo = serializers.ImageField(source='profile.photo')
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'photo',
            'is_followed',
        ]
        read_only_fields = fields

    def get_is_followed(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
            return user.followings.filter(id=obj.id, is_active=True).exists()
