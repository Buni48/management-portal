from django.db import models

class Customer(models.Model):
    customer_number = models.CharField(max_length = 32)
    company         = models.CharField(max_length = 64)
    first_name      = models.CharField(max_length = 64)
    last_name       = models.CharField(max_length = 64)
    email_address   = models.CharField(max_length = 64)
    phone_number    = models.CharField(max_length = 64)
    active          = models.BooleanField(default = True)
