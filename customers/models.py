from django.db import models

class Customer(models.Model):
    """
    The model 'Customer' is the owner of locations and has a contract with aubex.

    Attributes:
    customer_number (str): The unique identification number 
    name            (str): The name of the customer
    """
    customer_number = models.CharField(max_length = 32)
    name            = models.CharField(max_length = 64)

class Location(models.Model):
    """
    The model 'Location' is a subsidiary of a customer.

    Attributes:
    name            (str): The name of the location
    email_address   (str): The email address of the location
    phone_number    (str): The phone number of the location
    street          (str): The street where it's located
    house_number    (str): The house number of the location street
    postcode        (str): The postal code of the city where it's located
    city            (str): The city where it's located
    adviser         (int): Foreign key for the customer adviser of aubex who is responsible for the location
    """
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
    """
    The model 'Person' is abstract.

    Attributes:
    first_name      (str): The first name of the person
    last_name       (str): The last name of the person
    email_address   (str): The email address name of the person
    phone_number    (str): The phone number of the person
    """
    first_name      = models.CharField(max_length = 64)
    last_name       = models.CharField(max_length = 64)
    email_address   = models.CharField(max_length = 64)
    phone_number    = models.CharField(max_length = 64)
    class Meta:
        abstract = True

class ContactPerson(Person):
    """
    The model 'ContactPerson' inherits from abstract 'Person'.
    He is part of a customer's location and the contact person for aubex.

    Attributes:
    product  (int): The foreign keys for the products the contact person is responsible for
    location (int): The foreign key for the customer's location the contact person is from
    """
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
    """
    The model 'CustomerAdviser' inherits from abstract 'Person'.
    He is part of aubex and advises a customer's location.
    """
    pass
