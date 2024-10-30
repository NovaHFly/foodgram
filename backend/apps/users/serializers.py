from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from common.serializers import Base64ImageField

from .models import FoodgramUser


class CreateUserSerializer(serializers.ModelSerializer):
    """Contains fields needed to register new user.

    Fields:
        id (int): User id.
        email (str[254]): User email.
        username (str[150]): User on-site name.
        first_name (str[64]): User first name.
        last_name (str[64]): User last name.
        password (str[Password]): User password.
    """

    class Meta:
        model = FoodgramUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, data: str) -> str:
        validate_password(data)
        return data

    def create(self, validated_data: dict) -> FoodgramUser:
        password = validated_data.pop('password')
        user = FoodgramUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Api representation of user object.

    Fields:
        id (int): User id.
        email (str[254]): User email.
        username (str[150]): User on-site name.
        first_name (str[64]): User first name.
        last_name (str[64]): User last name.
        avatar (str[Url]): Url to user avatar.
        is_subscribed (bool): Current user is subscribed to this user.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = FoodgramUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, user: FoodgramUser) -> bool:
        if request := self.context.get('request', None):
            current_user = request.user
            if current_user.is_anonymous:
                return False
            return user in current_user.subscriptions.all()
        return False


class SubscriptionUserSerializer(UserSerializer):
    """Api representation of user in subscriptions list.

    Can be replaced with extended version:
    ```
    users.serializers.SubscriptionUserSerializer = ...
    ```
    Base version does not provide any functionality different
    from UserSerializer.
    This serializer is used to allow additional data be
    shown when viewing user on subscriptions list without altering
    UserSerializer.
    """


class AvatarSerializer(serializers.ModelSerializer):
    """Serializer to set user avatar.

    Fields:
        avatar: str[Base64 Image]: Base64-encoded image to use as avatar.
    """

    avatar = Base64ImageField()

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)

    def update(self, user: FoodgramUser, validated_data: dict) -> FoodgramUser:
        user.avatar.delete()
        return super().update(user, validated_data)


class AuthSerializer(serializers.Serializer):
    """Authentication serializer.

    Fields:
        email (str[254]): User email.
        password (str[Password]): User password.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, email: str) -> str:
        if not FoodgramUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Неверный email или пароль!')
        return email

    def validate(self, attrs: dict) -> dict:
        user = self.user = FoodgramUser.objects.get(email=attrs['email'])
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('Неверный email или пароль!')
        return attrs


class PasswordChangeSerializer(serializers.ModelSerializer):
    """Serializer to change user password.

    Fields:
        current_password (str[Password]): Current user password.
        new_password (str[Password]): New user password.
    """

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        model = FoodgramUser
        fields = ('new_password', 'current_password')

    def validate_current_password(self, password: str) -> str:
        if not self.instance.check_password(password):
            raise serializers.ValidationError('Неверный пароль!')
        return password

    def validate_new_password(self, password: str) -> str:
        validate_password(password)
        return password

    def update(self, user: FoodgramUser, validated_data: dict) -> FoodgramUser:
        user.set_password(validated_data['new_password'])
        user.save()
        return user
