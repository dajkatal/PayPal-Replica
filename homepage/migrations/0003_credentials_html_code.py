# Generated by Django 3.1.7 on 2021-04-03 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0002_auto_20210403_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentials',
            name='html_code',
            field=models.TextField(default=''),
        ),
    ]