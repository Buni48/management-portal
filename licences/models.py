from django.db import models

class Licence(models.Model):
    key              = models.CharField(max_length = 255)
    detail           = models.CharField(max_length = 2047)
    start_date       = models.DateTimeField(auto_now_add = True)
    end_date         = models.DateTimeField()
    software_version = models.CharField(max_length=16)
    product          = models.ForeignKey(
        to                  = 'SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'softwares',
        related_query_name  = 'software',
        null                = False,
    )
    location         = models.ForeignKey(
        to                  = 'customers.Location',
        on_delete           = models.CASCADE,
        related_name        = 'locations',
        related_query_name  = 'location',
        null                = False,
    )

class SoftwareProduct(models.Model):
    name     = models.CharField(max_length = 64)
    category = models.CharField(max_length = 64)
    version  = models.CharField(max_length = 16)

class SoftwareModule(models.Model):
    name    = models.CharField(max_length = 127)
    version = models.CharField(max_length = 16)
    product = models.ForeignKey(
        to                  = 'SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'modules',
        related_query_name  = 'module',
        null                = False,
    )
