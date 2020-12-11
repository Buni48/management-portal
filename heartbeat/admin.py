from django.contrib import admin
from . import models

heartbeat_models = [
    models.Heartbeat,
]

admin.site.register(heartbeat_models)
