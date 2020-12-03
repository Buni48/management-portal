from django.db import models
from django.db.models import Max
from datetime import datetime, timezone, timedelta
from licenses.models import UsedSoftwareProduct, SoftwareProduct
from customers.models import Location

EXPECTED_MAX_DURATION = timedelta(days = 1, minutes = -45)
LIMIT                 = 1000
DATE_TYPE             = '%Y/%m/%d %H:%M:%S'

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
        to                  = 'licenses.UsedSoftwareProduct',
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
        usedProducts = UsedSoftwareProduct.objects.all()[:limit]

        for usedProduct in usedProducts:
            heartbeats            = Heartbeat.objects.filter(used_product_id = usedProduct.id)
            last_received_max     = heartbeats.aggregate(Max('last_received'))

            try:
                usedProduct.heartbeat     = Heartbeat.objects.get(used_product_id = usedProduct.id, last_received = last_received_max['last_received__max'])
                duration                  = datetime.now(timezone.utc) - usedProduct.heartbeat.last_received
                usedProduct.last_received = usedProduct.heartbeat.last_received.strftime(DATE_TYPE)
                if (duration <= EXPECTED_MAX_DURATION):
                    usedProduct.received = True
                else:
                    usedProduct.received = False
            except:
                usedProduct.last_received = 'Noch nie'
                usedProduct.received = False

            usedProduct.product   = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            usedProduct.location  = Location.objects.get(used_product__id = usedProduct.id)

        return usedProducts

    def getCountMissing(usedProducts: list) -> int:
        """
        Returns the amount of heartbeats not received in expected time.

        Parameters:
        usedProducts (list): List of used products

        Returns:
        int: Amount of missing heartbeats
        """
        count = 0
        for usedProduct in usedProducts:
            if (usedProduct.received == False):
                count += 1
        return count
