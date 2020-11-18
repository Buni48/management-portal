from django.db import models

class Customer(models.Model):
    customer_number = models.CharField(max_length = 32)
    name            = models.CharField(max_length = 64)

class Location(models.Model):
    name            = models.CharField(max_length = 64)
    email_address   = models.CharField(max_length = 64)
    phone_number    = models.CharField(max_length = 64)
    street          = models.CharField(max_length = 64)
    house_number    = models.CharField(max_length = 8)
    postcode        = models.CharField(max_length = 16)
    city            = models.CharField(max_length = 64)
    adviser         = models.ForeignKey(
        to                  = 'CustomerAdviser',
        on_delete           = models.SET_NULL,
        related_name        = 'advisers',
        related_query_name  = 'adviser',
        null                = True,
    )

class Person(models.Model):
    first_name      = models.CharField(max_length = 64)
    last_name       = models.CharField(max_length = 64)
    email_address   = models.CharField(max_length = 64)
    phone_number    = models.CharField(max_length = 64)
    class Meta:
        abstract = True

class ContactPerson(Person):
    product  = models.ManyToManyField(
        to                  = 'licences.SoftwareProduct',
        related_name        = 'contact_persons',
        related_query_name  = 'contact_person',
    )
    location = models.ForeignKey(
        to                  = 'Location',
        on_delete           = models.CASCADE,
        related_name        = 'contact_persons',
        related_query_name  = 'contact_person',
        null                = True,
    )

class CustomerAdviser(Person):
    pass
