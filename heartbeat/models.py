from django.db import models

class Heartbeat(models.Model):
    """
    The model 'Heartbeat' manages when the last positive status information was received.

    Attributes:
    last_received (datetime): The date when the last heartbeat was received
    message       (str)     : The message of the received heartbeat
    detail        (str)     : The detailed information of the received heartbeat
    licence       (int)     : The licence of the used software product the heartbeat belongs to
    """
    last_received = models.DateTimeField()
    message       = models.CharField(max_length=2047)
    detail        = models.CharField(max_length=2047)
    licence       = models.ForeignKey(
        to                  = 'licences.Licence',
        on_delete           = models.CASCADE,
        related_name        = 'heartbeats',
        related_query_name  = 'heartbeat',
        null                = False,
    )
