from django.db import models

class Licence(models.Model):
    key         = models.CharField(max_length=256)
    start_date  = models.DateTimeField(auto_now_add = True)
    end_date    = models.DateTimeField()
    current_software_version = models.CharField(max_length=16)
    software    = models.ForeignKey(to = 'Software', on_delete = models.CASCADE, null = False)
    customer    = models.ForeignKey(to = 'customers.Customer', on_delete = models.CASCADE, null = False)
    active      = models.BooleanField(default = True)

class Software(models.Model):
    name = models.CharField(max_length = 64)
