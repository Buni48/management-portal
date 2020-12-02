from django.contrib import admin
from customers import models as customers_models
from heartbeat import models as heartbeat_models
from licenses  import models as licenses_models
from updates   import models as updates_models

models = [
    customers_models.Customer,
    customers_models.Location,
    customers_models.ContactPerson,
    heartbeat_models.Heartbeat,
    licenses_models.CustomerLicense,
    licenses_models.LocationLicense,
    licenses_models.SoftwareProduct,
    licenses_models.UsedSoftwareProduct,
    licenses_models.SoftwareModule,
    updates_models.Update,
]

admin.site.register(models)
