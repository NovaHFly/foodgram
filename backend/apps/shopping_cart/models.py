from annoying.fields import AutoOneToOneField
from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()


class ShoppingCart(models.Model):
    user = AutoOneToOneField(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_carts',
        verbose_name='Рецепты',
        blank=True,
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['user__username']

    def __str__(self) -> str:
        return f'Список покупок {self.user}'
