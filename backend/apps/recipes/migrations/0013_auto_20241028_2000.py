# Generated by Django 3.2.16 on 2024-10-28 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20241024_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
