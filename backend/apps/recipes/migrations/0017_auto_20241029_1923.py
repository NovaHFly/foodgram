# Generated by Django 3.2.16 on 2024-10-29 16:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20241029_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Время приготовления не может быть меньше 1!')], verbose_name='Время приготовления (мин.)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Количество не может быть меньше 1!')], verbose_name='Количество'),
        ),
    ]
