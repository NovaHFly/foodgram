# Generated by Django 3.2.16 on 2024-11-04 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20241029_1852'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodgramuser',
            options={'ordering': ['-username'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]