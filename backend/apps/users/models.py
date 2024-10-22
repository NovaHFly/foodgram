from django.contrib.auth.models import AbstractUser
from django.db import models

# TODO: Generalize image upload path
# TODO: Add verbose names


class FoodgramUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
    )


class UserSubscription(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribed_to_users',
    )
    subscribed_to = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
