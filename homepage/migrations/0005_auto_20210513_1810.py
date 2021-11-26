# Generated by Django 3.1.7 on 2021-05-13 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0004_credentials_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='viewers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='credentials',
            name='cookies',
            field=models.TextField(default=''),
        ),
    ]