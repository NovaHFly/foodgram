from django.contrib.auth.models import AbstractUser
from django.db import models

from .const import MAX_NAME_LENGTH


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Фамилия',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар',
    )
    subscriptions = models.ManyToManyField(
        'FoodgramUser',
        related_name='subscribers',
        verbose_name='Подписки на пользователей',
    )

    def __str__(self) -> str:
        return f'{self.username} [{self.email}]'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-username']
