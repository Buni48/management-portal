from django.db import models
from datetime import datetime, timezone, timedelta
from customers.models import Location
from updates.models import Update

EXPECTED_MAX_DURATION = timedelta(weeks = 6)
LIMIT                 = 1000
DATE_TYPE             = '%Y/%m/%d'

class Licence(models.Model):
    """
    The model 'Licence' is the permission to use a software module of a software product.
    It is abstract: There are customer and location licences.

    Attributes:
    key              (str)      : The licence key
    detail           (str)      : The detailed information about the licence
    start_date       (datetime) : The start date of the licence
    end_date         (datetime) : The end date of the licence
    module           (int)      : Foreign key for the software module the licence is for
    """
    key              = models.CharField(max_length = 255)
    detail           = models.CharField(max_length = 2047)
    start_date       = models.DateTimeField(auto_now_add = True)
    end_date         = models.DateTimeField()
    module           = models.ForeignKey(
        to                  = 'SoftwareModule',
        on_delete           = models.CASCADE,
        related_name        = 'licences',
        related_query_name  = 'licence',
        null                = False,
    )

    def getLicences(limit: int = LIMIT) -> list:
        """
        Returns licences including information about product, location and if a licence is expiring soon.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: licences
        """
        licences = Licence.objects.all().order_by('end_date')[:limit]

        for licence in licences:
            duration = licence.end_date - datetime.now(timezone.utc)
            licence.start_date = licence.start_date.strftime(DATE_TYPE)
            licence.end_date   = licence.end_date.strftime(DATE_TYPE)
            if (duration > EXPECTED_MAX_DURATION):
                licence.valid = 1
            elif (duration > timedelta(seconds = 0)):
                licence.valid = 0
            else:
                licence.valid = -1

            usedProduct      = UsedSoftwareProduct.objects.get(licence__id = licence.id)
            licence.product  = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            licence.location = Location.objects.get(used_product__id = usedProduct.id)

        return licences

class CustomerLicence(Licence):
    """
    The customer licence is a licence valid for the whole customer.

    Attributes:
    licence_ptr (int): Primary key identifier for all licences
    customer    (int): Foreign key for the customer which uses the licence
    """
    customer = models.ForeignKey(
        to                  = 'customers.Customer',
        on_delete           = models.CASCADE,
        related_name        = 'customer_licences',
        related_query_name  = 'customer_licence',
        null                = False,
    )

class LocationLicence(Licence):
    """
    The location licence is a licence valid for a single customer's location.

    Attributes:
    licence_ptr (int): Primary key identifier for all licences
    location    (int): Foreign key for the customer's location which uses the licence
    """
    location = models.ForeignKey(
        to                  = 'customers.Location',
        on_delete           = models.CASCADE,
        related_name        = 'location_licences',
        related_query_name  = 'location_licence',
        null                = False,
    )

class SoftwareProduct(models.Model):
    """
    The model 'SoftwareProduct' is a software product which can be used by many customers.
    It has multiple software modules.

    Attributes:
    name     (str): The name of the software product
    category (str): The category the software product belongs to
    version  (str): The current version of the software product
    adviser  (str): The adviser of the software product
    """
    name     = models.CharField(max_length = 64)
    category = models.CharField(max_length = 64)
    version  = models.CharField(max_length = 16)
    adviser  = models.CharField(max_length = 64, null = True)

    def __str__(self):
        return self.name

class UsedSoftwareProduct(models.Model):
    """
    The model 'UsedSoftwareProduct' represents the used software product.

    Attributes:
    location (int): Foreign key to the customer's location the software product is used by
    product  (int): Foreign key to the software product the customer's location uses
    """
    version      = models.CharField(max_length = 16)
    last_updated = models.DateTimeField(auto_now_add = True)
    location     = models.ForeignKey(
        to                  = 'customers.Location',
        on_delete           = models.CASCADE,
        related_name        = 'used_products',
        related_query_name  = 'used_product',
        null                = False,
    )
    product      = models.ForeignKey(
        to                  = 'SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'used_products',
        related_query_name  = 'used_product',
        null                = False,
    )

    def getUsedProducts(limit: int = LIMIT) -> list:
        """
        Returns used products including information about product, location and if the used product uses the current software version.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: used products
        """
        usedProducts = UsedSoftwareProduct.objects.all()[:limit]

        for usedProduct in usedProducts:
            usedProduct.location     = Location.objects.get(used_product__id = usedProduct.id)
            usedProduct.product      = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            usedProduct.last_updated = usedProduct.last_updated.strftime(DATE_TYPE)

            if usedProduct.version == usedProduct.product.version:
                usedProduct.current = True
            else:
                usedProduct.current = False

            try:
                updates = Update.objects.filter(product_id = usedProduct.product.id).order_by('-release_date')
                usedProduct.last_released = updates[0].release_date.strftime(DATE_TYPE)
            except:
                usedProduct.last_released = 'Noch nie'
                usedProduct.last_updated  = 'Noch nie'

        return usedProducts

class SoftwareModule(models.Model):
    """
    The model 'SoftwareModule' is a part of a software product.
    It has multiple licences.

    Attributes:
    name    (str): The name of the software module
    product (int): Foreign key to the software product the module belongs to
    """
    name    = models.CharField(max_length = 127)
    product = models.ForeignKey(
        to                  = 'SoftwareProduct',
        on_delete           = models.CASCADE,
        related_name        = 'modules',
        related_query_name  = 'module',
        null                = False,
    )

    def __str__(self):
        return self.name
