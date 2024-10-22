from rest_framework import serializers

from .models import FoodgramUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodgramUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = FoodgramUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()


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
