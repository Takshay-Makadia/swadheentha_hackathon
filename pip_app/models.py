from django.db import models


class User(models.Model):
    name = models.CharField(max_length=32)
    email = models.EmailField()
    age = models.IntegerField()
    password = models.CharField(max_length=32)

    def __str__(self):
        return self.name
