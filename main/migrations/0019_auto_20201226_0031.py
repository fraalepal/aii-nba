# Generated by Django 3.1.3 on 2020-12-25 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20201226_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='proxPartido',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='record',
            field=models.CharField(max_length=256),
        ),
    ]