from .models import Customer, Location, ContactPerson
from itertools import chain

class CustomerController:

    @staticmethod
    def getFilteredCustomers(word: str, contains: bool = False) -> list:
        """
        Returns the filtered customers, filtering by customer number and name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered customers
        """
        if contains:
            customersByNumber = Customer.objects.filter(customer_number__icontains = word).values('id', 'customer_number', 'name')
            customersByName   = Customer.objects.filter(name__icontains = word).values('id', 'customer_number', 'name')
        else:
            customersByNumber = Customer.objects.filter(customer_number__iexact = word).values('id', 'customer_number', 'name')
            customersByName   = Customer.objects.filter(name__iexact = word).values('id', 'customer_number', 'name')

        return list(chain(customersByName, customersByNumber))


class LocationController:

    @staticmethod
    def getLocationsByName(word: str, contains: bool = False) -> list:
        """
        Returns the filtered locations, filtering by name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered locations
        """
        if contains:
            locations = Location.objects.filter(name__icontains = word).values('id', 'name', 'postcode', 'city')
        else:
            locations = Location.objects.filter(name__iexact = word).values('id', 'name', 'postcode', 'city')
        
        for location in locations:
            customer = Customer.objects.get(id = location['id'])
            location['customer'] = customer.name

        return list(locations)


class ContactPersonController:

    @staticmethod
    def getContactPersonsByName(word: str, contains: bool = False) -> list:
        """
        Returns the filtered contact persons, filtering by first name and last name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered contact persons
        """
        words = word.split(' ')

        if contains:
            if len(words) == 2:
                contactsOne = ContactPerson.objects.filter(first_name__icontains = words[0], last_name__icontains = words[1]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contactsTwo = ContactPerson.objects.filter(first_name__icontains = words[1], last_name__icontains = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts    = list(chain(contactsOne, contactsTwo))
            elif len(words) == 3:
                contactsOne = ContactPerson.objects.filter(first_name__icontains = words[0] + words[1], last_name__icontains = words[2]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contactsTwo = ContactPerson.objects.filter(first_name__icontains = words[1] + words[2], last_name__icontains = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts    = list(chain(contactsOne, contactsTwo))
            else:
                contactsByFirstName = ContactPerson.objects.filter(first_name__icontains = word).values('id', 'first_name', 'last_name', 'location__name', 'location__customer__name', 'product__name')
                contactsByLastName  = ContactPerson.objects.filter(last_name__icontains  = word).values('id', 'first_name', 'last_name', 'location__name', 'location__customer__name', 'product__name')
                contacts            = list(chain(contactsByFirstName, contactsByLastName))
        else:
            if len(words) == 2:
                contactsOne = ContactPerson.objects.filter(first_name__iexact = words[0], last_name__iexact = words[1]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contactsTwo = ContactPerson.objects.filter(first_name__iexact = words[1], last_name__iexact = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts    = list(chain(contactsOne, contactsTwo))
            elif len(words) == 3:
                contactsOne = ContactPerson.objects.filter(first_name__iexact = words[0] + words[1], last_name__iexact = words[2]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contactsTwo = ContactPerson.objects.filter(first_name__iexact = words[1] + words[2], last_name__iexact = words[0]).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts    = list(chain(contactsOne, contactsTwo))
            else:
                contactsByFirstName = ContactPerson.objects.filter(first_name__iexact = word).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contactsByLastName  = ContactPerson.objects.filter(last_name__iexact  = word).values('id', 'first_name', 'last_name', 'location__name', 'product__name')
                contacts            = list(chain(contactsByFirstName, contactsByLastName))

        for contact in contacts:
            if not contact['product__name']:
                contact['product__name'] = 'Nicht zugewiesen'

        return list(contacts)
