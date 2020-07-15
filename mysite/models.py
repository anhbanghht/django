from django.db import models

class User(models.Model):
    user_name = models.CharField(max_length=200)
    birthday = models.DateField()
    email = models.EmailField(max_length=50)
    department = models.IntegerField(default=0)

class Department(models.Model):
    name = models.CharField(max_length=50)
    parent_id = models.IntegerField(default=0)
    note = models.CharField(max_length=200)
