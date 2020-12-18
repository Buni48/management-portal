from .models import Heartbeat
from django.db.models import Max
from datetime import datetime, timezone
from licenses.models import UsedSoftwareProduct, SoftwareProduct
from customers.models import Location
from management_portal.constants import LIMIT, DATETIME_TYPE, HEARTBEAT_DURATION

class HeartbeatController:

    @staticmethod
    def read(limit: int = LIMIT) -> list:
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
                usedProduct.last_received = usedProduct.heartbeat.last_received.strftime(DATETIME_TYPE)
                if (duration <= HEARTBEAT_DURATION):
                    usedProduct.received = True
                else:
                    usedProduct.received = False
            except:
                usedProduct.last_received = 'Noch nie'
                usedProduct.received      = False

            usedProduct.product   = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            usedProduct.location  = Location.objects.get(used_product__id = usedProduct.id)

        return usedProducts

    @staticmethod
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

    @staticmethod
    def getCounts(usedProducts: list) -> dict:
        """
        Returns the amount of heartbeats recieved and not received in expected time.

        Parameters:
        usedProducts (list): List of used products

        Returns:
        dict: Amount of valid and missing heartbeats
        """
        count = {
            'missing': 0,
            'valid'  : 0,
        }
        for usedProduct in usedProducts:
            if usedProduct.received:
                count['valid'] += 1
            else:
                count['missing'] += 1

        return count