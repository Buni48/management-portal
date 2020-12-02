from django.db import models
from itertools import chain

class Customer(models.Model):
    """
    The model 'Customer' is the owner of locations and has a contract with aubex.

    Attributes:
    customer_number (str): The unique identification number 
    name            (str): The name of the customer
    """
    customer_number = models.CharField(max_length = 32)
    name            = models.CharField(max_length = 64)

    def __str__(self):
        return self.name
    
    def getFilteredCustomers(word: str, contains: bool = False) -> list:
        """
        Returns the filtered customers, filtering by customer number and name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word (str): word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered customers
        """
        if contains:
            customersByNumber = Customer.objects.filter(customer_number__icontains = word).values('id', 'customer_number', 'name')
            customersByName   = Customer.objects.filter(name__icontains = word).values('id', 'customer_number', 'name')
        else:
            customersByNumber = Customer.objects.filter(customer_number_iexact = word).values('id', 'customer_number', 'name')
            customersByName   = Customer.objects.filter(name_iexact = word).values('id', 'customer_number', 'name')

        return list(chain(customersByName, customersByNumber))

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
    customer        (int): Foreign key for the customer the location belongs to
    adviser         (int): Foreign key for the customer adviser of aubex who is responsible for the location
    """
    name            = models.CharField(max_length = 64)
    email_address   = models.CharField(max_length = 64)
    phone_number    = models.CharField(max_length = 64)
    street          = models.CharField(max_length = 64)
    house_number    = models.CharField(max_length = 8)
    postcode        = models.CharField(max_length = 16)
    city            = models.CharField(max_length = 64)
    customer        = models.ForeignKey(
        to                  = 'Customer',
        on_delete           = models.CASCADE,
        related_name        = 'locations',
        related_query_name  = 'location',
        null                = False,
    )
    adviser         = models.ForeignKey(
        to                  = 'CustomerAdviser',
        on_delete           = models.SET_NULL,
        related_name        = 'locations',
        related_query_name  = 'location',
        null                = True,
    )

    def __str__(self):
        return self.name

    def getLocationsByName(word: str, contains: bool = True) -> list:
        """
        Returns the filtered locations, filtering by name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word (str): word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered locations
        """
        if contains:
            locations = Location.objects.filter(name__icontains = word).values('id', 'name', 'postcode', 'city')
        else:
            locations = Location.objects.filter(name_iexact = word).values('id', 'name', 'postcode', 'city')
        
        for location in locations:
            customer = Customer.objects.get(id = location['id'])
            location['customer'] = customer.name

        return list(locations)

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

    def __str__(self):
        return self.first_name + ' ' + self.last_name

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
