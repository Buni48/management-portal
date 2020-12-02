from django.db import models
from datetime import datetime, timezone, timedelta
from customers.models import Location
from updates.models import Update

EXPECTED_MAX_DURATION = timedelta(weeks = 6)
LIMIT                 = 1000
DATE_TYPE             = '%Y/%m/%d'

class License(models.Model):
    """
    The model 'License' is the permission to use a software module of a software product.
    It is abstract: There are customer and location licenses.

    Attributes:
    key              (str)      : The license key
    detail           (str)      : The detailed information about the license
    start_date       (datetime) : The start date of the license
    end_date         (datetime) : The end date of the license
    module           (int)      : Foreign key for the software module the license is for
    """
    key              = models.CharField(max_length = 255)
    detail           = models.CharField(max_length = 2047)
    start_date       = models.DateTimeField(auto_now_add = True)
    end_date         = models.DateTimeField()
    module           = models.ForeignKey(
        to                  = 'SoftwareModule',
        on_delete           = models.CASCADE,
        related_name        = 'licenses',
        related_query_name  = 'license',
        null                = False,
    )

    def getLicenses(limit: int = LIMIT) -> list:
        """
        Returns licenses including information about product, location and if a license is expiring soon.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: licenses
        """
        licenses = License.objects.all().order_by('end_date')[:limit]

        for license in licenses:
            duration = license.end_date - datetime.now(timezone.utc)
            license.start_date = license.start_date.strftime(DATE_TYPE)
            license.end_date   = license.end_date.strftime(DATE_TYPE)
            if (duration > EXPECTED_MAX_DURATION):
                license.valid = 1
            elif (duration > timedelta(seconds = 0)):
                license.valid = 0
            else:
                license.valid = -1

            usedProduct      = UsedSoftwareProduct.objects.get(license__id = license.id)
            license.product  = SoftwareProduct.objects.get(used_product__id = usedProduct.id)
            license.location = Location.objects.get(used_product__id = usedProduct.id)

        return licenses

class CustomerLicense(License):
    """
    The customer license is a license valid for the whole customer.

    Attributes:
    license_ptr (int): Primary key identifier for all licenses
    customer    (int): Foreign key for the customer which uses the license
    """
    customer = models.ForeignKey(
        to                  = 'customers.Customer',
        on_delete           = models.CASCADE,
        related_name        = 'customer_licenses',
        related_query_name  = 'customer_license',
        null                = False,
    )

class LocationLicense(License):
    """
    The location license is a license valid for a single customer's location.

    Attributes:
    license_ptr (int): Primary key identifier for all licenses
    location    (int): Foreign key for the customer's location which uses the license
    """
    location = models.ForeignKey(
        to                  = 'customers.Location',
        on_delete           = models.CASCADE,
        related_name        = 'location_licenses',
        related_query_name  = 'location_license',
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
    It has multiple licenses.

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
