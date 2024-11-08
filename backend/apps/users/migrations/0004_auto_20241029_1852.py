# Generated by Django 3.2.16 on 2024-10-29 15:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20241022_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodgramuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users/avatars/', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='subscriptions',
            field=models.ManyToManyField(related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Подписки на пользователей'),
        ),
    ]
