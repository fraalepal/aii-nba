# Generated by Django 3.1.3 on 2020-12-25 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20201226_0004'),
    ]

    operations = [
        migrations.RenameField(
            model_name='equipo',
            old_name='estadisticas',
            new_name='proxPartido',
        ),
        migrations.RenameField(
            model_name='equipo',
            old_name='lesionados',
            new_name='ranking',
        ),
    ]