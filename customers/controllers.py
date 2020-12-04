from .models import Customer, Location
from itertools import chain

class CustomerController:

    @staticmethod
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


class LocationController:

    @staticmethod
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
