# Generated by Django 3.1.3 on 2020-12-25 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20201225_2318'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreEquipo', models.TextField(unique=True, verbose_name='Nombre')),
            ],
        ),
        migrations.DeleteModel(
            name='Equipos',
        ),
    ]
