# Generated by Django 3.1.3 on 2021-12-25 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitedb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='persecution',
            name='permission_level',
            field=models.IntegerField(default=0, verbose_name='допуск'),
        ),
    ]
