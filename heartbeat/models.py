from django.db import models

class Heartbeat(models.Model):
    last_received = models.DateTimeField()
    message       = models.CharField(max_length=2047)
    detail        = models.CharField(max_length=2047)
    licence       = models.ForeignKey(
        to = 'licences.Licence',
        on_delete = models.CASCADE,
        related_name = 'heartbeats',
        related_query_name = 'heartbeat',
        null = False,
    )
