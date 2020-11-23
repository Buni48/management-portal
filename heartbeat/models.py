from django.db import models
from datetime import datetime, timezone, timedelta
from licences.models import UsedSoftwareProduct, SoftwareProduct
from customers.models import Location

EXPECTED_MAX_DURATION = timedelta(days = 1, minutes = -45)
LIMIT = 1000

class Heartbeat(models.Model):
    """
    The model 'Heartbeat' manages when the last positive status information was received.

    Attributes:
    last_received (datetime): The date when the last heartbeat was received
    message       (str)     : The message of the received heartbeat
    detail        (str)     : The detailed information of the received heartbeat
    used_product  (int)     : The used product the heartbeat belongs to
    """
    last_received = models.DateTimeField(auto_now_add = True)
    message       = models.CharField(max_length = 2047)
    detail        = models.CharField(max_length = 2047)
    used_product  = models.ForeignKey(
        to                  = 'licences.UsedSoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'heartbeats',
        related_query_name  = 'heartbeat',
        null                = False,
    )

    def getHeartbeats(limit: int = LIMIT) -> list:
        """
        Returns heartbeats including information about product, location and if a heartbeat is missing.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: Heartbeats
        """
        heartbeats = Heartbeat.objects.all().order_by('last_received')[:limit]

        for heartbeat in heartbeats:
            duration = datetime.now(timezone.utc) - heartbeat.last_received
            heartbeat.last_received = heartbeat.last_received.strftime("%d/%m/%Y %H:%M:%S")
            if (duration <= EXPECTED_MAX_DURATION):
                heartbeat.received = True
            else:
                heartbeat.received = False

            usedProduct         = UsedSoftwareProduct.objects.get(heartbeat__id = heartbeat.id)
            heartbeat.product   = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            heartbeat.location  = Location.objects.get(used_product__id = usedProduct.id)

        return heartbeats

    def getCountMissing(heartbeats: list) -> int:
        """
        Returns the amount of heartbeats not received in expected time.

        Parameters:
        heartbeats (list): List of heartbeat objects

        Returns:
        int: Amount of missing heartbeats
        """
        count = 0
        for heartbeat in heartbeats:
            if (heartbeat.received == False):
                count += 1
        return count

    def getHeartbeatsMissing() -> list:
        """
        Returns the missing heartbeats including the location.

        Returns:
        list: Heartbeats
        """
        missingTime = datetime.now(timezone.utc) - EXPECTED_MAX_DURATION
        heartbeats = Heartbeat.objects.filter(last_received__lte = missingTime).order_by('last_received')

        for heartbeat in heartbeats:
            usedProduct         = UsedSoftwareProduct.objects.get(heartbeat__id = heartbeat.id)
            heartbeat.location  = Location.objects.get(used_product__id = usedProduct.id)

        return heartbeats
