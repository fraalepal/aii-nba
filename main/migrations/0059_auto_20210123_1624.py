# Generated by Django 3.1.3 on 2021-01-23 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_auto_20210123_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipo',
            name='id',
        ),
        migrations.AlterField(
            model_name='equipo',
            name='nombreEquipo',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='jugador',
            name='nombreEquipo',
            field=models.ForeignKey(max_length=256, on_delete=django.db.models.deletion.DO_NOTHING, to='main.equipo'),
        ),
    ]
