# Generated by Django 3.2.16 on 2024-11-05 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_delete_shortlink'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='favorited_by_users',
        ),
    ]
