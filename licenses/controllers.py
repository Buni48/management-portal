from .models import License, CustomerLicense, LocationLicense, SoftwareProduct, SoftwareModule
from customers.models import Customer, Location
from datetime import datetime, timezone, timedelta
from management_portal.constants import LIMIT, DATE_TYPE, DATE_TYPE_JS, LICENSE_EXPIRE_WARNING

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
            license.end_date   = license.end_date.strftime(DATE_TYPE)
            if (duration > LICENSE_EXPIRE_WARNING):
                license.valid = 1
            elif (duration > timedelta(seconds = 0)):
                license.valid = 0
            else:
                license.valid = -1

            license.product  = SoftwareProduct.objects.get(id = license.module.product_id)
            try:
                # if license is a location license
                locationLicense  = LocationLicense.objects.get(license_ptr_id = license.id)
                license.location = Location.objects.get(id = locationLicense.location_id)
                license.customer = Customer.objects.get(id = license.location.customer_id)
            except:
                try:
                    # if license is a customer license
                    customerLicense  = CustomerLicense.objects.get(license_ptr_id = license.id)
                    license.location = 'Für alle gültig'
                    license.customer = Customer.objects.get(id = customerLicense.customer_id)
                except:
                    # if license has no child (this shouldn't happen: license is abstract!)
                    license.location = 'Nicht zugewiesen'
                    license.customer = 'Nicht zugewiesen'

        return licenses

    @staticmethod
    def getLicenseById(id: int):
        try:
            license = LocationLicense.objects.get(license_ptr_id = id)
            license.start_date = license.start_date.strftime(DATE_TYPE_JS)
            license.end_date   = license.end_date.strftime(DATE_TYPE_JS)
        except:
            try:
                license = CustomerLicense.objects.get(license_ptr_id = id)
                license.start_date = license.start_date.strftime(DATE_TYPE_JS)
                license.end_date   = license.end_date.strftime(DATE_TYPE_JS)
            except:
                license = None
        
        return license


    @staticmethod
    def save(key: str, detail: str, start_date: str, end_date: str,
        module: int, location: int = 0, customer: int = 0, id: int = 0) -> dict:
        status = {
            'status' : False,
            'message': '',
        }
        status = LicenseController.__checkCompleteness(
            key         = key,
            detail      = detail,
            start_date  = start_date,
            end_date    = end_date,
            module      = module,
            location    = location,
            customer    = customer,
            id          = id,
        )
        if status['status']:
            result = LicenseController.__checkForeignKeys(
                module   = module,
                location = location,
                customer = customer,
            )
            if result['status']:
                if id:
                    status          = LicenseController.edit(
                        id          = id,
                        key         = key,
                        detail      = detail,
                        start_date  = start_date,
                        end_date    = end_date,
                        module      = result['moduleInstance'],
                        location    = result['locationInstance'],
                        customer    = result['customerInstance'],
                    )
                else:
                    status          = LicenseController.create(
                        key         = key,
                        detail      = detail,
                        start_date  = start_date,
                        end_date    = end_date,
                        module      = result['moduleInstance'],
                        location    = result['locationInstance'],
                        customer    = result['customerInstance'],
                    )
            else:
                status['status']  = result['status']
                status['message'] = result['message']

        return status

    @staticmethod
    def create(key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> dict:
        status = {
            'status' : True,
            'message': 'Die Lizenz wurde erfolgreich angelegt.',
        }
        try:
            if location:
                license = LocationLicense(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    location    = location,
                )
                license.save()
            else:
                license = CustomerLicense(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    customer    = customer,
                )
                license.save()
        except:
            status['status']  = False
            status['message'] = 'Es ist ein unerwarteter Fehler aufgetreten'

        return status

    @staticmethod
    def edit(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> dict:
        status = {
            'status' : True,
            'message': 'Die Lizenz wurde erfolgreich aktualisiert.',
        }
        try:
            LicenseController.__updateLocationLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                location    = location,
                customer    = customer,
            )
        except:
            try:
                LicenseController.__updateCustomerLicense(
                    id          = id,
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    location    = location,
                    customer    = customer,
                )
            except:
                status['status']  = False
                status['message'] = 'Die zu bearbeitende Lizenz wurde nicht gefunden'

        return status

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
    
    @staticmethod
    def __checkCompleteness(key: str, detail: str, start_date: str, end_date: str,
        module: int, location: int, customer: int, id: int) -> dict:
        status = {
            'status' : False,
            'message': '',
        }
        if not len(key):
            status['message'] = 'Bitte Lizenzschlüssel angeben.'
        elif not len(detail):
            status['message'] = 'Bitte Details angeben.'
        elif not len(start_date):
            status['message'] = 'Bitte Anfangsdatum angeben.'
        elif not len(end_date):
            status['message'] = 'Bitte Enddatum angeben.'
        elif start_date >= end_date:
            status['message'] = 'Enddatum muss später als Anfangsdatum sein.'
        elif not module:
            status['message'] = 'Bitte Modul angeben.'
        elif customer and location:
            status['message'] = 'Bitte nur Kunde ODER Standort zuweisen.'
        elif not customer and not location:
            status['message'] = 'Bitte Kunde oder Standort zuweisen.'
        else:
            status['status'] = True
        
        return status

    @staticmethod
    def __checkForeignKeys(module: int, location: int, customer: int):
        result = {
            'status'          : False,
            'message'         : '',
            'moduleInstance'  : None,
            'locationInstance': None,
            'customerInstance': None,
        }
        try:
            result['moduleInstance'] = SoftwareModule.objects.get(id = module)
        except:
            result['message'] = 'Zugewiesenes Modul nicht gefunden.'
    
        if not len(result['message']):
            if location:
                try:
                    result['locationInstance'] = Location.objects.get(id = location)
                    result['status']           = True
                except:
                    result['message'] = 'Zugewiesenen Standort nicht gefunden.'
            else:
                try:
                    result['customerInstance'] = Customer.objects.get(id = customer)
                    result['status']           = True
                except:
                    result['message'] = 'Zugewiesenen Kunden nicht gefunden.'

        return result

    @staticmethod
    def __updateLocationLicense(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer):
        locationLicense = LocationLicense.objects.get(license_ptr_id = id)
        if location:
            locationLicense.key         = key
            locationLicense.detail      = detail
            locationLicense.start_date  = start_date
            locationLicense.end_date    = end_date
            locationLicense.module      = module
            locationLicense.location    = location
            locationLicense.save()
        else:
            locationLicense.delete()
            customerLicense = CustomerLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                customer    = customer,
            )
            customerLicense.save()

    def __updateCustomerLicense(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer):
        customerLicense = CustomerLicense.objects.get(license_ptr_id = id)
        if customer:
            customerLicense.key         = key
            customerLicense.detail      = detail
            customerLicense.start_date  = start_date
            customerLicense.end_date    = end_date
            customerLicense.module      = module
            customerLicense.customer    = customer
            customerLicense.save()
        else:
            customerLicense.delete()
            locationLicense = LocationLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                location    = location,
            )
            locationLicense.save()


class SoftwareProductController:

    @staticmethod
    def getProductsByName(word: str, contains: bool = False) -> list:
        """
        Returns the filtered software products, filtering by name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered software products
        """
        if contains:
            products = SoftwareProduct.objects.filter(name__icontains = word).values('id', 'name', 'category')
        else:
            products = SoftwareProduct.objects.filter(name__iexact = word).values('id', 'name', 'category')

        return list(products)


class SoftwareModuleController:

    @staticmethod
    def getModuleNames(limit: int = LIMIT) -> list:
        """
        Returns all module names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: module names
        """
        return list(SoftwareModule.objects.all()[:limit].values('id', 'name'))

    @staticmethod
    def getModulesByName(word: str, contains: bool = False) -> list:
        """
        Returns the filtered software modules, filtering by name.
        Pass a word to filter. You can choose to filter "contains" or "is".

        Parameters:
        word     (str) : word to filter by
        contains (bool): if contains or is

        Returns:
        list: filtered software modules
        """
        if contains:
            modules = SoftwareModule.objects.filter(name__icontains = word).values('id', 'name', 'product__name')
        else:
            modules = SoftwareModule.objects.filter(name__iexact = word).values('id', 'name', 'product__name')

        return list(modules)
