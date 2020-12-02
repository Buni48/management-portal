from django.contrib import admin
from . import models

update_models = [
    models.Update,
]

admin.site.register(update_models)
