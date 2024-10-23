import base64

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import FoodgramUser


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
            'password',
            'avatar',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('avatar',)

    def get_is_subscribed(self, obj):
        if request := self.context.get('request', None):
            current_user = request.user
            if current_user.is_anonymous:
                return False
            return obj in current_user.subscriptions.all()
        return False

    def validate_password(self, data):
        validate_password(data)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuthoredRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()


class SubscriptionUserSerializer(UserSerializer):
    recipes = AuthoredRecipeSerializer(many=True)
    recipe_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipe_count',
        )

    def get_recipe_count(self, obj):
        return obj.recipes.count()


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
