from annoying.fields import AutoOneToOneField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserSubscriptions(models.Model):
    user = AutoOneToOneField(
        User,
        related_name='subscription_list',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    users = models.ManyToManyField(
        User,
        verbose_name='Пользователи',
    )

    class Meta:
        verbose_name = 'Список подписок'
        verbose_name_plural = 'Списки подписок'