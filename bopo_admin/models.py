from django.db import models

# Create your models here.
class BopoAdmin(models.Model):
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=15)

    def __str__(self):
        return self.username
    

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    aadhaar = models.CharField(max_length=12, unique=True)
    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10, unique=True)
    pan = models.CharField(max_length=10, unique=True)
    pincode = models.CharField(max_length=6)

    def __str__(self):
        return self.name