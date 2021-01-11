from django.db import models

class Heartbeat(models.Model):
    """
    The model 'Heartbeat' manages when the last positive status information was received.

    Attributes:
    last_received (datetime): The date when the last heartbeat was received
    message       (str)     : The message of the received heartbeat
    detail        (str)     : The detailed information of the received heartbeat
    used_product  (int)     : The used product the heartbeat belongs to
    """
    last_received    = models.DateTimeField(auto_now_add = True)
    message          = models.CharField(max_length = 2047)
    detail           = models.CharField(max_length = 2047)
    unknown_location = models.BooleanField(default = False)
    used_product     = models.ForeignKey(
        to                  = 'licenses.UsedSoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'heartbeats',
        related_query_name  = 'heartbeat',
        null                = False,
    )
