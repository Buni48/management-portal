from .models import License, CustomerLicense, LocationLicense, SoftwareProduct, UsedSoftwareProduct,SoftwareModule
from customers.models import Customer, Location
from datetime import datetime, timezone, timedelta
from management_portal.constants import LIMIT, DATE_TYPE, DATE_TYPE_JS, LICENSE_EXPIRE_WARNING
from management_portal.general import Status, SaveStatus

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
        """
        Returns the location or customer license to a given id.
        Returns 'None', if no license exists.

        Attributes:
        id (int): license id

        Returns:
        License: location or customer license
        """
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
        module: int, location: int = 0, customer: int = 0, id: int = 0) -> Status:
        """
        Saves a license.
        By giving an id it edits this license otherwise it creates a new one.
        Give a location id to save a location license and a customer id to save a customer.

        Attributes:
        key         (str): license key
        detail      (str): license details
        start_date  (str): start date of the license
        end_date    (str): end date of the license
        module      (int): id of the belonging software module
        location    (int): id of the belonging customer's location
        customer    (int): id of the belonging customer
        id          (int): license id if license should been edited

        Returns:
        Status: save status
        """
        status = Status()
        status = LicenseController.__checkValidity(
            key         = key,
            detail      = detail,
            start_date  = start_date,
            end_date    = end_date,
            module      = module,
            location    = location,
            customer    = customer,
            id          = id,
        )
        if status.status:
            saveStatus   = LicenseController.__checkForeignKeys(
                module   = module,
                location = location,
                customer = customer,
            )
            if saveStatus.status:
                if id:
                    status          = LicenseController.edit(
                        id          = id,
                        key         = key,
                        detail      = detail,
                        start_date  = start_date,
                        end_date    = end_date,
                        module      = saveStatus.instances['module'],
                        location    = saveStatus.instances['location'],
                        customer    = saveStatus.instances['customer'],
                    )
                else:
                    status          = LicenseController.create(
                        key         = key,
                        detail      = detail,
                        start_date  = start_date,
                        end_date    = end_date,
                        module      = saveStatus.instances['module'],
                        location    = saveStatus.instances['location'],
                        customer    = saveStatus.instances['customer'],
                    )
            else:
                status.status  = saveStatus.status
                status.message = saveStatus.message

        return status

    @staticmethod
    def create(key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Creates a license and belonging used software products.
        Pass a location object to create a location license and a customer object to create a customer.

        Attributes:
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location
        customer    (Customer)      : belonging customer

        Returns:
        Status: create status
        """
        status = Status(True, 'Die Lizenz wurde erfolgreich angelegt.')
        try:
            if location:
                create_status = LicenseController.__createLocationLicense(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    location    = location,
                )
            else:
                create_status = LicenseController.__createCustomerLicense(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    customer    = customer,
                )
        except:
            status.status  = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        if create_status and not create_status.status:
            status.status = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        return status

    @staticmethod
    def edit(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Edits a license and creates or deletes belonging used software products if needed.
        Pass a location id to edit a location license and a customer id to edit a customer.

        Attributes:
        id          (int)           : license id
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location
        customer    (Customer)      : belonging customer

        Returns:
        Status: edit status
        """
        status = Status(True, 'Die Lizenz wurde erfolgreich aktualisiert.')
        try:
            update_status = LicenseController.__updateLocationLicense(
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
                update_status = LicenseController.__updateCustomerLicense(
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
                status.status  = False
                status.message = 'Die zu bearbeitende Lizenz wurde nicht gefunden.'

        if update_status and not update_status.status:
            status.status = False
            status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        return status
    
    @staticmethod
    def delete(id: int) -> Status:
        """
        Deletes the license with the given id.

        Attributes:
        id (int): id of the license to delete

        Returns:
        Status: delete status
        """
        status = Status(True, 'Die Lizenz wurde erfolgreich gelöscht.')
        try:
            license = LocationLicense.objects.get(license_ptr_id = id)
            LicenseController.__deleteRedundantUsedProduct(
                location = license.location,
                module   = license.module,
            )
            license.delete()
        except:
            try:
                license = CustomerLicense.objects.get(license_ptr_id = id)
                locations = Location.objects.filter(customer = license.customer)
                for location in locations:
                    LicenseController.__deleteRedundantUsedProduct(
                        location = location,
                        module   = license.module,
                    )
                license.delete()
            except:
                status.status  = False
                status.message = 'Die zu löschende wurde Lizenz nicht gefunden.'

        return status

    @staticmethod
    def getCounts(licenses: list) -> dict:
        """
        Returns the amount of missing and valid licenses in a given license list.

        Attributes:
        licenses (list): list of licenses

        Returns:
        dict: amount of missing and valid licenses
        """
        count = {
            'expired': 0,
            'valid'  : 0,
        }
        for license in licenses:
            if license.valid == -1:
                count['expired'] += 1
            else:
                count['valid'] += 1

        return count

    @staticmethod
    def __checkValidity(key: str, detail: str, start_date: str,
        end_date: str, module: int, location: int, customer: int, id: int) -> Status:
        """
        Checks if all necessary attributes to save a license are set and valid.

        Attributes:
        key         (str): license key
        detail      (str): license details
        start_date  (str): start date of the license
        end_date    (str): end date of the license
        module      (int): id of the belonging software module
        location    (int): id of the belonging customer's location
        customer    (int): id of the belonging customer
        id          (int): license id if license should been edited

        Returns:
        Status: save status
        """
        status = Status()
        if not len(key):
            status.message = 'Bitte Lizenzschlüssel angeben.'
        elif len(key) > 255:
            status.message = 'Lizenzschlüssel darf maximal 255 Zeichen lang sein.'
        elif not len(detail):
            status.message = 'Bitte Details angeben.'
        elif len(detail) > 2047:
            status.message = 'Details dürfen maximal 2047 Zeichen lang sein.'
        elif not len(start_date):
            status.message = 'Bitte Anfangsdatum angeben.'
        elif not len(end_date):
            status.message = 'Bitte Enddatum angeben.'
        elif start_date >= end_date:
            status.message = 'Enddatum muss später als Anfangsdatum sein.'
        elif not module:
            status.message = 'Bitte Modul angeben.'
        elif customer and location:
            status.message = 'Bitte nur Kunde ODER Standort zuweisen.'
        elif not customer and not location:
            status.message = 'Bitte Kunde oder Standort zuweisen.'
        else:
            licenses = LicenseController.read()
            for license in licenses:
                if key == license.key and not id == str(license.id):
                    status.message = 'Diese Lizenzschlüssel wird bereits verwendet.'
                    break
            if not len(status.message):
                status.status = True
        
        return status

    @staticmethod
    def __checkForeignKeys(module: int, location: int, customer: int) -> SaveStatus:
        """
        Checks if foreign keys are valid and returns status including belonging objects.

        Attributes:
        module      (int): id of the belonging software module
        location    (int): id of the belonging customer's location
        customer    (int): id of the belonging customer

        Returns:
        SaveStatus: save status including instances
        """
        instances = {
            'module'  : None,
            'location': None,
            'customer': None,
        }
        status = SaveStatus(instances = instances)
        try:
            status.instances['module'] = SoftwareModule.objects.get(id = module)
        except:
            status.message = 'Zugewiesenes Modul nicht gefunden.'
    
        if not len(status.message):
            if location:
                try:
                    status.instances['location'] = Location.objects.get(id = location)
                    status.status = True
                except:
                    status.message = 'Zugewiesenen Standort nicht gefunden.'
            else:
                try:
                    status.instances['customer'] = Customer.objects.get(id = customer)
                    status.status = True
                except:
                    status.message = 'Zugewiesenen Kunden nicht gefunden.'

        return status

    @staticmethod
    def __createLocationLicense(key: str, detail: str,
        start_date: str, end_date: str, module, location) -> Status:
        """
        Creates a location license and belonging used software products.

        Attributes:
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location

        Returns:
        Status: create status
        """
        status = LicenseController.__checkLicenseDuplicateForLocation(
            location = location,
            module   = module,
        )
        if status.status:
            license = LocationLicense(
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                location    = location,
            )
            status = LicenseController.__createUsedProduct(
                location = location,
                module   = module,
            )
            if status.status:
                license.save()

        return status

    @staticmethod
    def __createCustomerLicense(key: str, detail: str,
        start_date: str, end_date: str, module, customer) -> Status:
        """
        Creates a customer license and belonging used software products.
        Redundant location licenses will be removed.

        Attributes:
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        customer    (Customer)      : belonging customer

        Returns:
        Status: create status
        """
        status = LicenseController.__checkLicenseDuplicateForCustomer(
            customer = customer,
            module   = module,
        )
        if status.status:
            license = CustomerLicense(
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                customer    = customer,
            )
            status = LicenseController.__createUsedProductsForCustomer(
                customer = customer,
                module   = module,
            )
            if status.status:
                license.save()

        return status

    @staticmethod
    def __checkLicenseDuplicateForLocation(location, module) -> Status:
        """
        Checks if a license already existing for a location-module-combination.

        Attributes:
        location (Location)      : customer's location
        module   (SoftwareModule): software module

        Returns:
        Status: status
        """
        status = Status()
        try:
            LocationLicense.objects.get(
                module   = module,
                location = location,
            )
            status.message = 'Es existiert bereits eine Standortlizenz für diese Standort-Modul-Kombination.'
        except:
            status = LicenseController.__checkCustomerLicenseDuplicate(
                customer = location.customer,
                module   = module,
            )
        
        return status

    @staticmethod
    def __checkLicenseDuplicateForCustomer(customer, module) -> Status:
        """
        Checks if a license already existing for a customer-module-combination.
        If location licenses get redundant by the customer license they will be deleted.

        Attributes:
        customer (Customer)      : customer
        module   (SoftwareModule): software module

        Returns:
        Status: status
        """
        status = Status()
        status = LicenseController.__checkCustomerLicenseDuplicate(
            customer = customer,
            module   = module,
        )
        if status.status:
            locations = Location.objects.filter(customer = customer)
            for location in locations:
                try:
                    license = LocationLicense.objects.get(
                        location = location,
                        module   = module,
                    )
                    license.delete()
                    status.message = 'Deleted'
                except:
                    continue

        return status

    @staticmethod
    def __checkCustomerLicenseDuplicate(customer, module) -> Status:
        """
        Checks if a customer license already existing for a customer-module-combination.

        Attributes:
        customer (Customer)      : customer
        module   (SoftwareModule): software module

        Returns:
        Status: status
        """
        status = Status()
        try:
            CustomerLicense.objects.get(
                module   = module,
                customer = customer,
            )
            status.message = 'Es existiert bereits eine Kundenlizenz, die diese Standort-Modul-Kombination abdeckt.'
        except:
            status.status = True

        return status

    @staticmethod
    def __createUsedProduct(location, module) -> Status:
        """
        Creates a used product for the given location if it doesn't exist already.

        Attributes:
        location (Location)     : location of the used product
        module  (SoftwareModule): software module

        Returns:
        Status: status
        """
        status = Status(True)
        try:
            UsedSoftwareProduct.objects.get(
                location = location,
                product  = module.product,
            )
        except:
            try:
                used_product = UsedSoftwareProduct(
                    version  = module.product.version,
                    location = location,
                    product  = module.product,
                )
                used_product.save()
            except:
                status = False

        return status

    @staticmethod
    def __createUsedProductsForCustomer(customer, module) -> Status:
        """
        Creates used products for all location of the given customer if them doesn't exist already.

        Attributes:
        customer (Customer)       : customer the used products should be created for
        product  (SoftwareProduct): the software product the used software product is
        """
        status    = Status(True)
        locations = Location.objects.filter(customer = customer)
        for location in locations:
            status = LicenseController.__createUsedProduct(
                location = location,
                module   = module,
            )
        
        return status

    @staticmethod
    def __updateLocationLicense(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Updates a location license if a location is passed.
        If a customer is given instead the old location license gonna be deleted and a customer license is gonna be created instead.
        In this case the used products for the other locations will be also created.

        Attributes:
        id          (int)           : license id
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location
        customer    (Customer)      : belonging customer

        Returns:
        Status: update status
        """
        status = Status(True)
        locationLicense = LocationLicense.objects.get(license_ptr_id = id)
        if location:
            if not locationLicense.location == location:
                used_product = UsedSoftwareProduct.objects.get(
                    location = location,
                    product  = module.product,
                )
                used_product.location = location
                used_product.save()
            locationLicense.key         = key
            locationLicense.detail      = detail
            locationLicense.start_date  = start_date
            locationLicense.end_date    = end_date
            locationLicense.module      = module
            locationLicense.location    = location
            locationLicense.save()
        else:
            customerLicense = CustomerLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                customer    = customer,
            )
            up_status = LicenseController.__createUsedProductsForCustomer(
                customer = customer,
                module   = module,
            )
            if up_status:
                locationLicense.delete()
                customerLicense.save()

        return status

    @staticmethod
    def __updateCustomerLicense(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Updates a customer license if a customer is passed.
        If a location is given instead the old customer license gonna be deleted and a location license is gonna be created instead.
        In this case the used products for the old customer's locations will be also deleted and the new one will be created.

        Attributes:
        id          (int)           : license id
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location
        customer    (Customer)      : belonging customer

        Returns:
        Status: update status
        """
        status = Status(True)
        customerLicense = CustomerLicense.objects.get(license_ptr_id = id)
        if customer:
            if not customerLicense.customer == customer:
                status = LicenseController.__deleteUsedProductsForCustomer(
                    customer = customer,
                    module   = module,
                )
            if status.status:
                customerLicense.key         = key
                customerLicense.detail      = detail
                customerLicense.start_date  = start_date
                customerLicense.end_date    = end_date
                customerLicense.module      = module
                customerLicense.customer    = customer
                customerLicense.save()
        else:
            locationLicense = LocationLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                location    = location,
            )
            status = LicenseController.__deleteUsedProductsForCustomer(
                customer         = location.customer,
                module           = module,
                location_to_keep = location,
            )
            if status.status:
                customerLicense.delete()
                locationLicense.save()
        
        return status

    @staticmethod
    def __deleteUsedProductsForCustomer(customer, module, location_to_keep = None) -> Status:
        """
        Deletes the used products for the customers.
        You can optionally pass a location to keep.

        Attributes:
        customer         (Customer)      : customer the used products should be deleted
        module           (SoftwareModule): software module
        location_to_keep (Location)      : location to keep

        Returns:
        Status: delete status
        """
        status = Status(True)
        location_kept = False
        locations = Location.objects.filter(customer = customer)
        for location in locations:
            if location_to_keep and location_to_keep == location:
                location_kept = True
                continue
            try:
                used_product = UsedSoftwareProduct.objects.get(
                    location = location,
                    product  = module.product,
                )
                used_product.delete()
            except:
                status.status = False
                break
        if status.status and location_to_keep and not location_kept:
            status = LicenseController.__createUsedProduct(
                location = location_to_keep,
                module   = module,
            )

        return status

    @staticmethod
    def __deleteRedundantUsedProduct(location, module):
        """
        Deletes the used product of the given location-module-combination if it's redundant.

        Attributes:
        location (Location)      : customer's location
        module   (SoftwareModule): software module
        """
        location_licenses = LocationLicense.objects.filter(
            location = location,
            module   = module,
        )
        customer_licenses = CustomerLicense.objects.filter(
            customer = location.customer,
            module   = module,
        )
        amount = len(location_licenses) + len(customer_licenses)
        if amount < 2:
            used_product = UsedSoftwareProduct.objects.get(
                location = location,
                product  = module.product,
            )
            used_product.delete()


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
