# Generated by Django 3.2.16 on 2024-10-23 09:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0005_delete_favoriterecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='favorited_by_users',
            field=models.ManyToManyField(related_name='favorited_recipes', to=settings.AUTH_USER_MODEL),
        ),
    ]