# Generated by Django 3.1.3 on 2021-01-23 14:55

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_delete_jugador'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagenJugador', models.CharField(default='nul', max_length=256)),
                ('nombreJugador', models.CharField(default='nul', max_length=64)),
                ('posicionJugador', models.CharField(default='nul', max_length=64, verbose_name=main.models.Posicion)),
                ('salarioNumero', models.IntegerField(default=0)),
                ('puntosPorPartido', models.FloatField(default=0.0)),
                ('asistenciasPorPartido', models.FloatField(default=0.0)),
                ('rebotesPorPartido', models.FloatField(default=0.0)),
                ('nombreEquipo', models.ForeignKey(default='nul', max_length=256, on_delete=django.db.models.deletion.DO_NOTHING, to='main.equipo')),
            ],
        ),
    ]