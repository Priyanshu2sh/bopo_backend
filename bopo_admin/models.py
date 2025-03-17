from django.db import models

#admin login model
class BopoAdmin(models.Model):
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=15)

    def __str__(self):
        return self.username
    

#project model
class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Corporate', 'Corporate'),
        ('Individual', 'Individual'),
    ]

    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    project_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    legal_name = models.CharField(max_length=150)
    address = models.TextField()
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="India", editable=False)
    pin = models.CharField(max_length=10)

    def __str__(self):
        return self.project_name
    

#merchant model
class Merchant(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Link to Project
    contact_person = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)  # Optional field
    shop_name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="India", editable=False)
    pin_code = models.CharField(max_length=10)

    def __str__(self):
        return self.shop_name
