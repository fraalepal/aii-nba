# Generated by Django 3.1.3 on 2020-12-25 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20201225_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='estadisticas',
            field=models.CharField(default=None, max_length=256),
        ),
        migrations.AddField(
            model_name='equipo',
            name='lesionados',
            field=models.CharField(default=None, max_length=256),
        ),
    ]
