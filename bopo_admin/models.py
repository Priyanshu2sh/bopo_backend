from django.db import models

# Create your models here.
class BopoAdmin(models.Model):
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=15)

    def __str__(self):
        return self.username