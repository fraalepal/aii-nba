# Generated by Django 3.1.3 on 2020-12-30 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_jugador_imagenjugador'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipo',
            name='logoEquipo',
            field=models.CharField(default='nul', max_length=256),
        ),
    ]