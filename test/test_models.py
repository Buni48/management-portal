from django.test import TestCase
from django.db import models
from customers import models
from customers import*
from licenses import models
class ModelsTestCase(TestCase):

    def create_customer(self):
        Customer = Customer()
        Customer.customer_number = 1812505
        Customer.name = "Ola"
        Customer.save()

    def create_software_product(self):
        SoftwareProduct=SoftwareProduct()
        SoftwareProduct.name="Eclipse"
        SoftwareProduct.category="JRE"
        SoftwareProduct.version="2.7.1"
        SoftwareProduct.adviser="Ola"
        return SoftwareProduct

    def test_softwareproduct(self):
        SoftwareProduct = create_software_product(self)
        record=SoftwareProduct.objects.get()
        self.assertEquals(record, SoftwareProduct)

    def test_fields(self):
        Customer =Customer()
        Customer.customer_number=1812505
        Customer.name="Ola"
        Customer.save()
        record=Customer.objects.get()
        print(Customer.get_asoloute_url())
        self.assertEquals(record, Customer)

    def test_location(self):
        Location= Location()
        customer1 = customer()
        customer1.create_customer()
        Location.name="Mannheim Arena"
        Location.email_address="olaalabrash@icloud.com"
        Location.phone_number="015757118667"
        Location.street="Ulmenweg"
        Location.house_number="5A"
        Location.postcode="68167"
        Location.city="Weinheim"
        Location.customer= customer1
        Location.save()
        record=Location.objects.get()
        self.assertEquals(record,Location)
