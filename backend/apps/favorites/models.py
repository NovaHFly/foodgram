from annoying.fields import AutoOneToOneField
from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()


class UserFavorites(models.Model):
    user = AutoOneToOneField(
        User,
        related_name='favorites_list',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='favorites_lists',
        verbose_name='Рецепты',
        blank=True,
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        ordering = ['user__username']

    def __str__(self) -> str:
        return f'Список избранного {self.user.username}'
