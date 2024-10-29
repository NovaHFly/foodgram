from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from common.serializers import Base64ImageField

from .models import FoodgramUser


class UserRegisterSerializer(serializers.ModelSerializer):
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

    def validate_password(self, data):
        validate_password(data)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
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

    def get_is_subscribed(self, obj):
        if request := self.context.get('request', None):
            current_user = request.user
            if current_user.is_anonymous:
                return False
            return obj in current_user.subscriptions.all()
        return False


class SubscriptionUserSerializer(UserSerializer):
    """Serializer used to represent user object in subscription list.

    Can be extended by injecting new fields into."""

    class Meta(UserSerializer.Meta): ...


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar.delete()
        return super().update(instance, validated_data)


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, data):
        if not FoodgramUser.objects.filter(email=data).exists():
            raise serializers.ValidationError('Invalid email or password!')
        return data

    def validate(self, attrs):
        user = self.user = FoodgramUser.objects.get(email=attrs['email'])
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('Invalid email or password!')
        return attrs


class PasswordChangeSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        model = FoodgramUser
        fields = ('new_password', 'current_password')

    def validate_current_password(self, data):
        if not self.instance.check_password(data):
            raise serializers.ValidationError('Invalid password!')
        return data

    def validate_new_password(self, data):
        validate_password(data)
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
