from django.db import models

class Heartbeat(models.Model):
    last_received = models.DateTimeField()
    licence       = models.ForeignKey(to = 'licences.Licence', on_delete = models.CASCADE, null = False)
