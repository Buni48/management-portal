from django.contrib import admin
from . import models

license_models = [
    models.CustomerLicense,
    models.LocationLicense,
    models.SoftwareProduct,
    models.UsedSoftwareProduct,
    models.SoftwareModule,
]

admin.site.register(license_models)
