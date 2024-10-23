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
    subscriptions = models.ManyToManyField(
        'FoodgramUser',
        related_name='subscribers',
    )

    def __str__(self) -> str:
        return f'{self.username} [{self.email}]'
