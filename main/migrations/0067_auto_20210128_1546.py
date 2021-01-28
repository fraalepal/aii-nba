# Generated by Django 3.1.3 on 2021-01-28 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0066_auto_20210128_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='Universidad',
            fields=[
                ('nombreUniversidad', models.CharField(max_length=64, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='drafteado',
            name='universidad',
            field=models.ForeignKey(default='nul', max_length=256, on_delete=django.db.models.deletion.CASCADE, to='main.universidad'),
        ),
    ]