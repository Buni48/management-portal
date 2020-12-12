from .models import Customer, Location, ContactPerson, Person
from itertools import chain
from management_portal.constants import LIMIT

class CustomerController:

    @staticmethod
    def getCustomerNames(limit: int = LIMIT) -> list:
        """
        Returns all customer names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: customer names
        """
        return list(Customer.objects.all()[:limit].values('id', 'name'))

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
    def getLocationsByCustomer(customer_id: int, limit: int = LIMIT) -> list:
        locations = Location.objects.filter(customer_id = customer_id)

        for location in locations:
            location.persons = ContactPerson.objects.filter(location_id = location.id)

        return locations

    @staticmethod
    def getLocationNames(limit: int = LIMIT) -> list:
        """
        Returns all location names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: location names
        """
        return list(Location.objects.all()[:limit].values('id', 'name'))

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
