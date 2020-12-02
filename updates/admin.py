from django.contrib import admin
from customers import models as customers_models
from heartbeat import models as heartbeat_models
from licences  import models as licences_models
from updates   import models as updates_models

models = [
    customers_models.Customer,
    customers_models.Location,
    customers_models.ContactPerson,
    heartbeat_models.Heartbeat,
    licences_models.CustomerLicence,
    licences_models.LocationLicence,
    licences_models.SoftwareProduct,
    licences_models.UsedSoftwareProduct,
    licences_models.SoftwareModule,
    updates_models.Update,
]

admin.site.register(models)
