from django.contrib import admin
from . import models

customer_models = [
    models.Customer,
    models.Location,
    models.Person,
    models.ContactPerson,
]

admin.site.register(customer_models)
