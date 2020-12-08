from .models import License, CustomerLicense, LocationLicense, SoftwareProduct
from customers.models import Customer, Location
from datetime import datetime, timezone, timedelta
from management_portal.constants import LIMIT, DATE_TYPE, LICENSE_EXPIRE_WARNING


class LicenseController:

    @staticmethod
    def read(limit: int = LIMIT) -> list:
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
            license.end_date = license.end_date.strftime(DATE_TYPE)
            if (duration > LICENSE_EXPIRE_WARNING):
                license.valid = 1
            elif (duration > timedelta(seconds=0)):
                license.valid = 0
            else:
                license.valid = -1

            license.product = SoftwareProduct.objects.get(id=license.module.product_id)
            try:
                # if license is a location license
                locationLicense = LocationLicense.objects.get(license_ptr_id=license.id)
                license.location = Location.objects.get(id=locationLicense.location_id)
                license.customer = Customer.objects.get(id=license.location.customer_id)
            except:
                try:
                    # if license is a customer license
                    customerLicense = CustomerLicense.objects.get(license_ptr_id=license.id)
                    license.location = 'Für alle gültig'
                    license.customer = Customer.objects.get(id=customerLicense.customer_id)
                except:
                    # if license has no child (this shouldn't happen: license is abstract!)
                    license.location = 'Nicht zugewiesen'
                    license.customer = 'Nicht zugewiesen'

        return licenses

    @staticmethod
    def getCounts(licenses: list) -> list:
        count = {
            'missing': 0,
            'valid': 0,
        }
        for license in licenses:
            if license.valid == -1:
                count['missing'] += 1
        else:
            count['valid'] += 1

        return count
