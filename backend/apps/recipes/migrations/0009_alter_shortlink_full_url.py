# Generated by Django 3.2.16 on 2024-10-23 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_shortlink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlink',
            name='full_url',
            field=models.URLField(unique=True),
        ),
    ]