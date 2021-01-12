from .models import Heartbeat
from django.db.models import Max
from datetime import datetime, timezone
from licenses.models import UsedSoftwareProduct, SoftwareProduct
from customers.models import Location
from management_portal.constants import LIMIT, DATETIME_TYPE, HEARTBEAT_DURATION

class HeartbeatController:
    """
    The 'HeartbeatController' manages the heartbeat model.
    This includes things like read and counts.
    """

    @staticmethod
    def read(limit: int = LIMIT) -> list:
        """
        Returns heartbeats including information about product, location and if a heartbeat is missing.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: Heartbeats
        """
        used_products = UsedSoftwareProduct.objects.all()[:limit]

        for used_product in used_products:
            heartbeats            = Heartbeat.objects.filter(used_product_id = used_product.id)
            last_received_max     = heartbeats.aggregate(Max('last_received'))

            try:
                used_product.heartbeat     = Heartbeat.objects.get(used_product_id = used_product.id, last_received = last_received_max['last_received__max'])
                duration                  = datetime.now(timezone.utc) - used_product.heartbeat.last_received
                used_product.last_received = used_product.heartbeat.last_received.strftime(DATETIME_TYPE)
                if (duration <= HEARTBEAT_DURATION):
                    used_product.received = True
                else:
                    used_product.received = False
            except:
                used_product.last_received = 'Noch nie'
                used_product.received      = False

            used_product.product   = SoftwareProduct.objects.get(used_product__id = used_product.id)
            used_product.location  = Location.objects.get(used_product__id = used_product.id)

        return used_products

    @staticmethod
    def get_heartbeats_for_used_product_id(id: int) -> list:
        """
        Returns all heartbeats that belong to the used product.

        Parameters:
        id (int): used product id

        Returns:
        list: heartbeats
        """
        heartbeats = Heartbeat.objects.filter(used_product__id = id).values('id', 'last_received', 'message', 'detail')
        for heartbeat in heartbeats:
            heartbeat['last_received'] = heartbeat['last_received'].strftime(DATETIME_TYPE)

        return list(heartbeats)

    @staticmethod
    def get_count_missing(used_products: list) -> int:
        """
        Returns the amount of heartbeats not received in expected time.

        Parameters:
        used_products (list): List of used products

        Returns:
        int: Amount of missing heartbeats
        """
        count = 0
        for used_product in used_products:
            if (used_product.received == False):
                count += 1

        return count

    @staticmethod
    def get_counts(used_products: list) -> dict:
        """
        Returns the amount of heartbeats recieved and not received in expected time.

        Parameters:
        used_products (list): List of used products

        Returns:
        dict: Amount of valid and missing heartbeats
        """
        count = {
            'missing': 0,
            'valid'  : 0,
        }
        for used_product in used_products:
            if used_product.received:
                count['valid'] += 1
            else:
                count['missing'] += 1

        return count
