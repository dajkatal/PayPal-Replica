# Generated by Django 3.1.7 on 2021-04-03 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentials',
            name='html_code',
        ),
        migrations.RemoveField(
            model_name='credentials',
            name='otp',
        ),
        migrations.AddField(
            model_name='credentials',
            name='dob',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='credentials',
            name='income_after_tax',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='credentials',
            name='phone_number',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='credentials',
            name='ssn',
            field=models.CharField(default='', max_length=100),
        ),
    ]
