# Generated by Django 3.2.16 on 2024-11-05 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0021_delete_shoppingcart'),
        ('favorites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfavorites',
            name='recipes',
            field=models.ManyToManyField(blank=True, related_name='favorites_lists', to='recipes.Recipe', verbose_name='Рецепты'),
        ),
    ]