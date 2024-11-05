from django.db import models

from common.const import MAX_SLUG_LENGTH, MAX_URL_LENGTH


class ShortLink(models.Model):
    full_path = models.CharField(
        max_length=MAX_URL_LENGTH,
        unique=True,
        verbose_name='Полный путь до ресурса',
    )
    short_token = models.CharField(
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        verbose_name='Короткий токен',
    )

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ['full_path']

    def __str__(self) -> str:
        return f'/s/{self.short_token} -> {self.full_path}'
