# Generated by Django 3.2.16 on 2024-11-05 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_alter_shoppingcart_recipes'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ShortLink',
        ),
    ]
