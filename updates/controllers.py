from .models import Update
from customers.models import Location
from licenses.models import UsedSoftwareProduct, SoftwareProduct
from management_portal.constants import LIMIT, DATE_TYPE


class UpdateController:
    """
    The 'UpdateController' manages the update model.
    This includes things like read and counts.
    """

    @staticmethod
    def read(limit: int = LIMIT) -> list:
        """
        Returns used products including information about product, location and if the used product uses the current software version.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: used products
        """
        used_products = UsedSoftwareProduct.objects.all()[:limit]

        for used_product in used_products:
            used_product.location     = Location.objects.get(used_product__id = used_product.id)
            used_product.product      = SoftwareProduct.objects.get(used_product__id = used_product.id)
            used_product.last_updated = used_product.last_updated.strftime(DATE_TYPE)

            if used_product.version == used_product.product.version:
                used_product.current = True
            else:
                used_product.current = False

            try:
                updates                    = Update.objects.filter(product_id = used_product.product.id).order_by('-release_date')
                used_product.last_released = updates[0].release_date.strftime(DATE_TYPE)
            except:
                used_product.last_released = 'Noch nie'
                used_product.last_updated  = 'Noch nie'

        return used_products

    @staticmethod
    def get_counts(used_products: list) -> dict:
        """
        Returns the amount of used products recieved which are current or old.

        Parameters:
        used_products (list): List of used products

        Returns:
        dict: Amount of current and old used products
        """
        count = {
            'current': 0,
            'old'    : 0,
        }
        for used_product in used_products:
            if used_product.version == used_product.product.version:
                count['current'] += 1
            else:
                count['old'] += 1

        return count
