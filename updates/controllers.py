from .models import Update
from customers.models import Location
from licenses.models import UsedSoftwareProduct, SoftwareProduct
from management_portal.constants import LIMIT, DATE_TYPE


class UpdateController:

    @staticmethod
    def read(limit: int = LIMIT) -> list:
        """
        Returns used products including information about product, location and if the used product uses the current software version.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: used products
        """
        usedProducts = UsedSoftwareProduct.objects.all()[:limit]

        for usedProduct in usedProducts:
            usedProduct.location = Location.objects.get(used_product__id=usedProduct.id)
            usedProduct.product = SoftwareProduct.objects.get(used_product__id=usedProduct.id)
            usedProduct.last_updated = usedProduct.last_updated.strftime(DATE_TYPE)

            if usedProduct.version == usedProduct.product.version:
                usedProduct.current = True
            else:
                usedProduct.current = False

            try:
                updates = Update.objects.filter(product_id=usedProduct.product.id).order_by('-release_date')
                usedProduct.last_released = updates[0].release_date.strftime(DATE_TYPE)
            except:
                usedProduct.last_released = 'Noch nie'
                usedProduct.last_updated = 'Noch nie'

        return usedProducts

    @staticmethod
    def getCounts(usedProducts: list) -> dict:
        """
        Returns the amount of used products recieved which are current or old.

        Parameters:
        usedProducts (list): List of used products

        Returns:
        dict: Amount of current and old used products
        """
        count = {
            'current': 0,
            'old'    : 0,
        }
        for usedProduct in usedProducts:
            if usedProduct.version == usedProduct.product.version:
                count['current'] += 1
            else:
                count['old'] += 1

        return count
