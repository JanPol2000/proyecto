# Generated by Django 4.1.6 on 2023-02-09 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Geo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.BigIntegerField()),
                ('lon', models.BigIntegerField()),
                ('w', models.PositiveBigIntegerField()),
                ('h', models.PositiveBigIntegerField()),
            ],
        ),
    ]
