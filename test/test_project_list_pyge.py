# noinspection PyUnresolvedReferences
from selenium import webdriver
from customers.models import Customer
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

class TestCustomerListPage(StaticLiveServerTestCase):
    def test_customer(self):
        self.assertEqual(0,1)
