from .models import License, CustomerLicense, LocationLicense, SoftwareProduct, UsedSoftwareProduct, SoftwareModule
from customers.models import Customer, Location
from datetime import datetime, timezone, timedelta
from management_portal.constants import LIMIT, DATE_TYPE, DATE_TYPE_JS, LICENSE_EXPIRE_WARNING
from management_portal.general import Status, SaveStatus
from datetime import datetime, timezone, timedelta
import json

class LicenseController:
    """
    The 'LicenseController' manages the license model.
    This includes things like read, save and delete functions which can be called from the view.
    """

    @staticmethod
    def read(limit: int = LIMIT) -> list:
        """
        Returns licenses including information about product, location and if a license is expiring soon.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: licenses
        """
        licenses = License.objects.filter(replace_license__isnull = True).order_by('end_date')[:limit]

        for license in licenses:
            license.start_date = license.start_date.strftime(DATE_TYPE)
            try:
                future_license   = License.objects.get(replace_license = license.id)
                license.end_date = future_license.end_date.strftime(DATE_TYPE)
                license.valid    = 2
            except:
                duration         = license.end_date - datetime.now(timezone.utc)
                license.end_date = license.end_date.strftime(DATE_TYPE)
                if (duration > LICENSE_EXPIRE_WARNING):
                    license.valid = 1
                elif (duration > timedelta(seconds = 0)):
                    license.valid = 0
                else:
                    license.valid = -1

            license.product  = SoftwareProduct.objects.get(id = license.module.product_id)
            try:
                # if license is a location license
                location_license = LocationLicense.objects.get(license_ptr_id = license.id)
                license.location = Location.objects.get(id = location_license.location_id)
                license.customer = Customer.objects.get(id = license.location.customer_id)
            except:
                try:
                    # if license is a customer license
                    customer_license  = CustomerLicense.objects.get(license_ptr_id = license.id)
                    license.location = 'Für alle gültig'
                    license.customer = Customer.objects.get(id = customer_license.customer_id)
                except:
                    # if license has no child (this shouldn't happen: license is abstract!)
                    license.location = 'Nicht zugewiesen'
                    license.customer = 'Nicht zugewiesen'

        return licenses

    @staticmethod
    def get_license_by_id(id: int):
        """
        Returns the location or customer license to a given id.
        Returns 'None', if no license exists.

        Parameters:
        id (int): license id

        Returns:
        License: location or customer license
        """
        try:
            license            = LocationLicense.objects.get(license_ptr_id = id)
            license.start_date = license.start_date.strftime(DATE_TYPE_JS)
            license.end_date   = license.end_date.strftime(DATE_TYPE_JS)
        except:
            try:
                license            = CustomerLicense.objects.get(license_ptr_id = id)
                license.start_date = license.start_date.strftime(DATE_TYPE_JS)
                license.end_date   = license.end_date.strftime(DATE_TYPE_JS)
            except:
                license = None
        
        return license


    @staticmethod
    def save(key: str, detail: str, start_date: str, end_date: str, module: int,
        location: int = 0, customer: int = 0, id: int = 0, replace_license: int = 0) -> Status:
        """
        Saves a license.
        By giving an id it edits this license otherwise it creates a new one.
        Give a location id to save a location license and a customer id to save a customer.

        Parameters:
        key             (str): license key
        detail          (str): license details
        start_date      (str): start date of the license
        end_date        (str): end date of the license
        module          (int): id of the belonging software module
        location        (int): id of the belonging customer's location
        customer        (int): id of the belonging customer
        id              (int): license id if license should been edited
        replace_license (int): license id of the license to replace

        Returns:
        Status: save status
        """
        status        = Status()
        status        = LicenseController.__check_validity(
            key             = key,
            detail          = detail,
            start_date      = start_date,
            end_date        = end_date,
            module          = module,
            location        = location,
            customer        = customer,
            id              = id,
            replace_license = replace_license,
        )
        if status.status:
            if replace_license:
                status = LicenseController.__future_license(
                    replace_license = replace_license,
                    id              = id,
                    key             = key,
                    detail          = detail,
                    end_date        = end_date,
                )
            else:
                save_status  = LicenseController.__check_foreign_keys(
                    module   = module,
                    location = location,
                    customer = customer,
                )
                if save_status.status:
                    if id:
                        status          = LicenseController.edit(
                            id          = id,
                            key         = key,
                            detail      = detail,
                            start_date  = start_date,
                            end_date    = end_date,
                            module      = save_status.instances['module'],
                            location    = save_status.instances['location'],
                            customer    = save_status.instances['customer'],
                        )
                    else:
                        status          = LicenseController.create(
                            key         = key,
                            detail      = detail,
                            start_date  = start_date,
                            end_date    = end_date,
                            module      = save_status.instances['module'],
                            location    = save_status.instances['location'],
                            customer    = save_status.instances['customer'],
                        )
                else:
                    status.status  = save_status.status
                    status.message = save_status.message

        return status

    @staticmethod
    def create(key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Creates a license and belonging used software products.
        Pass a location object to create a location license and a customer object to create a customer.

        Parameters:
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
        status        = Status(True, 'Die Lizenz wurde erfolgreich angelegt.')
        create_status = None
        try:
            if location:
                create_status = LicenseController.__create_location_license(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    location    = location,
                )
            else:
                create_status = LicenseController.__create_customer_license(
                    key         = key,
                    detail      = detail,
                    start_date  = start_date,
                    end_date    = end_date,
                    module      = module,
                    customer    = customer,
                )
        except:
            status.set_unexpected()

        if create_status and not create_status.status:
            status.set_unexpected()

        return status

    @staticmethod
    def edit(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        Edits a license and creates or deletes belonging used software products if needed.
        Pass a location id to edit a location license and a customer id to edit a customer.

        Parameters:
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
        status        = Status(True, 'Die Lizenz wurde erfolgreich aktualisiert.')
        edit_status = None
        try:
            edit_status = LicenseController.__edit_location_license(
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
                edit_status = LicenseController.__edit_customer_license(
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
                status.set_unexpected('Die zu bearbeitende Lizenz wurde nicht gefunden.')

        if edit_status and not edit_status.status:
            status.set_unexpected()

        return status
    
    @staticmethod
    def delete(id: int) -> Status:
        """
        Deletes the license with the given id.

        Parameters:
        id (int): id of the license to delete

        Returns:
        Status: delete status
        """
        status = Status(True, 'Die Lizenz wurde erfolgreich gelöscht.')
        try:
            license         = LocationLicense.objects.get(license_ptr_id = id)
            future_licenses = LocationLicense.objects.exclude(replace_license__isnull = True)
            for future_license in future_licenses:
                future_license.delete()
            try:
                LicenseController.__delete_redundant_used_product(
                    location = license.location,
                    module   = license.module,
                )
            except:
                pass
            license.delete()
        except:
            try:
                license         = CustomerLicense.objects.get(license_ptr_id = id)
                future_licenses = CustomerLicense.objects.exclude(replace_license__isnull = True)
                for future_license in future_licenses:
                    future_license.delete()
                locations = Location.objects.filter(customer = license.customer)
                for location in locations:
                    try:
                        LicenseController.__delete_redundant_used_product(
                            location = location,
                            module   = license.module,
                        )
                    except:
                        pass
                license.delete()
            except:
                status.set_unexpected('Die zu löschende wurde Lizenz nicht gefunden.')

        return status

    @staticmethod
    def get_counts(licenses: list) -> dict:
        """
        Returns the amount of missing and valid licenses in a given license list.

        Parameters:
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
    def get_settings_information(id: int) -> dict:
        """
        Returns the information needed for the license settings.
        This includes the current and the future license.

        Parameters:
        id (int): license id

        Returns:
        dict: current and future license
        """
        settings = {
            'current': LicenseController.get_license_by_id(id = id),
            'future' : LicenseController.get_future_license(id = id),
        }
        if settings['current']:
            settings['current']           = settings['current'].__dict__
            settings['current']['_state'] = ''
            settings['current']           = json.dumps(settings['current'])
        else:
            settings['current'] = ''
        if settings['future']:
            settings['future']           = settings['future'].__dict__
            settings['future']['_state'] = ''
            settings['future']           = json.dumps(settings['future'])
        else:
            settings['future'] = ''

        return settings

    @staticmethod
    def get_future_license(id: int):
        """
        Returns the future license to a given id.
        Returns 'None', if no future license exists.

        Parameters:
        id (int): license id

        Returns:
        License: future license
        """
        try:
            license             = License.objects.get(replace_license__id = id)
            license.start_date  = license.start_date.strftime(DATE_TYPE)
            license.end_date    = license.end_date.strftime(DATE_TYPE)
            return license
        except:
            return None

    @staticmethod
    def __check_validity(key: str, detail: str, start_date: str, end_date: str,
        module: int, location: int, customer: int, id: int, replace_license: int) -> Status:
        """
        Checks if all necessary attributes to save a license are set and valid.

        Parameters:
        key             (str): license key
        detail          (str): license details
        start_date      (str): start date of the license
        end_date        (str): end date of the license
        module          (int): id of the belonging software module
        location        (int): id of the belonging customer's location
        customer        (int): id of the belonging customer
        id              (int): license id if license should been edited
        replace_license (int): license id of the license to replace

        Returns:
        Status: status
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
        elif not len(start_date) and not replace_license:
            status.message = 'Bitte Anfangsdatum angeben.'
        elif not len(end_date):
            status.message = 'Bitte Enddatum angeben.'
        elif start_date >= end_date:
            status.message = 'Enddatum muss später als Anfangsdatum sein.'
        elif not module and not replace_license:
            status.message = 'Bitte Modul angeben.'
        elif customer and location:
            status.message = 'Bitte nur Kunde ODER Standort zuweisen.'
        elif not customer and not location and not replace_license:
            status.message = 'Bitte Kunde oder Standort zuweisen.'
        elif replace_license and (customer or location or module or start_date):
            status.message = 'Bei ersetzender Lizenz bitte nicht Kunde, Standort, Modul oder Anfangsdatum zuweisen.'
        else:
            licenses = License.objects.all()
            for license in licenses:
                if key == license.key and not id == str(license.id):
                    status.message = 'Dieser Lizenzschlüssel wird bereits verwendet.'
                    break
            if not len(status.message):
                status.status = True
        
        return status

    @staticmethod
    def __check_foreign_keys(module: int, location: int, customer: int) -> SaveStatus:
        """
        Checks if foreign keys are valid and returns status including belonging objects.

        Parameters:
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
                    status.status                = True
                except:
                    status.message               = 'Zugewiesenen Standort nicht gefunden.'
            else:
                try:
                    status.instances['customer'] = Customer.objects.get(id = customer)
                    status.status                = True
                except:
                    status.message               = 'Zugewiesenen Kunden nicht gefunden.'

        return status

    @staticmethod
    def __future_license(replace_license: int, key: str, detail: str, end_date: str, id: int = 0) -> Status:
        """
        If the license to create should be replace another in the future.

        Parameters:
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license
        id              (int): license id if license should been edited

        Returns:
        Status: status
        """
        status = None

        if id:
            status = LicenseController.__edit_future_license(
                id              = id,
                replace_license = replace_license,
                key             = key,
                detail          = detail,
                end_date        = end_date,
            )
        else:
            status = LicenseController.__create_future_license(
                replace_license = replace_license,
                key             = key,
                detail          = detail,
                end_date        = end_date,
            )

        return status

    @staticmethod
    def __create_future_license(replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        If the license to create should be replace another in the future.

        Parameters:
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: create status
        """
        status        = Status(True, 'Die Lizenz wurde erfolgreich angelegt.')
        create_status = None
        try:
            create_status = LicenseController.__create_future_location_license(
                replace_license = replace_license,
                key             = key,
                detail          = detail,
                end_date        = end_date,
            )
        except:
            try:
                create_status = LicenseController.__create_future_customer_license(
                    replace_license = replace_license,
                    key             = key,
                    detail          = detail,
                    end_date        = end_date,
                )
            except:
                status.set_unexpected('Zu ersetzende Lizenz nicht gefunden.')
        
        if create_status and not create_status.status:
            status.set_unexpected(create_status.message)

        return status

    @staticmethod
    def __edit_future_license(id: int, replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        If the license to edit should be replace another in the future.

        Parameters:
        id              (int): license id of the license to edit
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: edit status
        """
        status      = Status(True, 'Die Lizenz wurde erfolgreich aktualisiert.')
        edit_status = None
        try:
            edit_status = LicenseController.__edit_future_location_license(
                id              = id,
                replace_license = replace_license,
                key             = key,
                detail          = detail,
                end_date        = end_date,
            )
        except:
            try:
                edit_status = LicenseController.__edit_future_customer_license(
                    id              = id,
                    replace_license = replace_license,
                    key             = key,
                    detail          = detail,
                    end_date        = end_date,
                )
            except:
                status.set_unexpected('Zu bearbeitende Lizenz nicht gefunden.')
        
        if edit_status and not edit_status.status:
            status.set_unexpected(edit_status.message)

        return status

    @staticmethod
    def __create_future_location_license(replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        Creates the location license to replace.

        Parameters:
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: create status
        """
        status      = Status(True)
        old_license = LocationLicense.objects.get(license_ptr_id = replace_license)
        dates_valid = LicenseController.__check_dates_validity(
            end_date_string = end_date,
            start_date      = old_license.end_date,
        )
        if not dates_valid:
            status.set_unexpected('Enddatum muss später als Anfangsdatum sein.')
        else:
            try:
                new_license = LocationLicense(
                    key             = key,
                    detail          = detail,
                    start_date      = old_license.end_date,
                    end_date        = end_date,
                    module          = old_license.module,
                    replace_license = old_license,
                    location        = old_license.location,
                )
                new_license.save()
            except:
                status.set_unexpected()

        return status

    @staticmethod
    def __create_future_customer_license(replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        Creates the customer license to replace.

        Parameters:
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: status
        """
        status = Status(True)
        old_license = CustomerLicense.objects.get(license_ptr_id = replace_license)
        dates_valid = LicenseController.__check_dates_validity(
            end_date_string = end_date,
            start_date      = old_license.end_date,
        )
        if not dates_valid:
            status.set_unexpected('Enddatum muss später als Anfangsdatum sein.')
        else:
            try:
                new_license = CustomerLicense(
                    key             = key,
                    detail          = detail,
                    start_date      = old_license.end_date,
                    end_date        = end_date,
                    module          = old_license.module,
                    replace_license = old_license,
                    customer        = old_license.customer,
                )
                new_license.save()
            except:
                status.set_unexpected()

        return status
    
    @staticmethod
    def __edit_future_location_license(id: int, replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        Edits the location license to replace.

        Parameters:
        id              (int): license id of the license to edit
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: edit status
        """
        status = Status(True)
        license = LocationLicense.objects.get(id = id)
        try:
            old_license = LocationLicense.objects.get(license_ptr_id = replace_license)
            dates_valid = LicenseController.__check_dates_validity(
                end_date_string = end_date,
                start_date      = old_license.end_date,
            )
            if not dates_valid:
                status.set_unexpected('Enddatum muss später als Anfangsdatum sein.')
            else:
                try:
                    license.key      = key
                    license.detail   = detail
                    license.end_date = end_date
                    license.save()
                except:
                    status.set_unexpected()
        except:
            status.set_unexpected('Zu ersetzende Lizenz nicht gefunden.')

        return status

    @staticmethod
    def __edit_future_customer_license(id: int, replace_license: int, key: str, detail: str, end_date: str) -> Status:
        """
        Edits the customer license to replace.

        Parameters:
        id              (int): license id of the license to edit
        replace_license (int): license id of the license to replace
        key             (str): license key
        detail          (str): license details
        end_date        (str): end date of the license

        Returns:
        Status: edit status
        """
        status = Status(True)
        license = CustomerLicense.objects.get(id = id)
        try:
            old_license = CustomerLicense.objects.get(license_ptr_id = replace_license)
            dates_valid = LicenseController.__check_dates_validity(
                end_date_string = end_date,
                start_date      = old_license.end_date,
            )
            if not dates_valid:
                status.set_unexpected('Enddatum muss später als Anfangsdatum sein.')
            else:
                try:
                    license.key      = key
                    license.detail   = detail
                    license.end_date = end_date
                    license.save()
                except:
                    status.set_unexpected()
        except:
            status.set_unexpected('Zu ersetzende Lizenz nicht gefunden.')

        return status
    
    @staticmethod
    def __check_dates_validity(end_date_string: str, start_date: datetime) -> bool:
        """
        Checks if the end date given as a string is later than the start date.

        end_date_string (str)     : license end date as string
        start_date      (datetime): license start date

        Returns:
        bool: if valid
        """
        end_date = datetime.now(timezone.utc)
        date_parts = end_date_string.split('-')
        end_date = datetime(
            int(date_parts[0]),
            int(date_parts[1]),
            int(date_parts[2]),
            0, 0, 0,
            tzinfo=timezone.utc,
        )
        difference = end_date - start_date
        return difference > timedelta(0)

    @staticmethod
    def __create_location_license(key: str, detail: str,
        start_date: str, end_date: str, module, location) -> Status:
        """
        Creates a location license and belonging used software products.

        Parameters:
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        location    (Location)      : belonging customer's location

        Returns:
        Status: create status
        """
        status = LicenseController.__check_license_duplicate_for_location(
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
            status = LicenseController.__create_used_product(
                location = location,
                module   = module,
            )
            if status.status:
                license.save()

        return status

    @staticmethod
    def __create_customer_license(key: str, detail: str,
        start_date: str, end_date: str, module, customer) -> Status:
        """
        Creates a customer license and belonging used software products.
        Redundant location licenses will be removed.

        Parameters:
        key         (str)           : license key
        detail      (str)           : license details
        start_date  (str)           : start date of the license
        end_date    (str)           : end date of the license
        module      (SoftwareModule): belonging software module
        customer    (Customer)      : belonging customer

        Returns:
        Status: create status
        """
        status = LicenseController.__check_license_duplicate_for_customer(
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
            status = LicenseController.__create_used_products_for_customer(
                customer = customer,
                module   = module,
            )
            if status.status:
                license.save()

        return status

    @staticmethod
    def __check_license_duplicate_for_location(location, module) -> Status:
        """
        Checks if a license already existing for a location-module-combination.

        Parameters:
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
            status = LicenseController.__check_customer_license_duplicate(
                customer = location.customer,
                module   = module,
            )
        
        return status

    @staticmethod
    def __check_license_duplicate_for_customer(customer, module) -> Status:
        """
        Checks if a license already existing for a customer-module-combination.
        If location licenses get redundant by the customer license they will be deleted.

        Parameters:
        customer (Customer)      : customer
        module   (SoftwareModule): software module

        Returns:
        Status: status
        """
        status = Status()
        status = LicenseController.__check_customer_license_duplicate(
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
    def __check_customer_license_duplicate(customer, module) -> Status:
        """
        Checks if a customer license already existing for a customer-module-combination.

        Parameters:
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
    def __create_used_product(location, module) -> Status:
        """
        Creates a used product for the given location if it doesn't exist already.

        Parameters:
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
    def __create_used_products_for_customer(customer, module) -> Status:
        """
        Creates used products for all location of the given customer if them doesn't exist already.

        Parameters:
        customer (Customer)       : customer the used products should be created for
        product  (SoftwareProduct): the software product the used software product is
        """
        status    = Status(True)
        locations = Location.objects.filter(customer = customer)
        for location in locations:
            status = LicenseController.__create_used_product(
                location = location,
                module   = module,
            )
        
        return status

    @staticmethod
    def __edit_location_license(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        edits a location license if a location is passed.
        If a customer is given instead the old location license gonna be deleted and a customer license is gonna be created instead.
        In this case the used products for the other locations will be also created.

        Parameters:
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
        status = Status(True)
        location_license = LocationLicense.objects.get(license_ptr_id = id)
        if location:
            if not location_license.location == location:
                used_product = UsedSoftwareProduct.objects.get(
                    location = location,
                    product  = module.product,
                )
                used_product.location = location
                used_product.save()
            location_license.key         = key
            location_license.detail      = detail
            location_license.start_date  = start_date
            location_license.end_date    = end_date
            location_license.module      = module
            location_license.location    = location
            location_license.save()
        else:
            customer_license = CustomerLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                customer    = customer,
            )
            up_status = LicenseController.__create_used_products_for_customer(
                customer = customer,
                module   = module,
            )
            if up_status:
                location_license.delete()
                customer_license.save()

        return status

    @staticmethod
    def __edit_customer_license(id: int, key: str, detail: str,
        start_date: str, end_date: str, module, location, customer) -> Status:
        """
        edits a customer license if a customer is passed.
        If a location is given instead the old customer license gonna be deleted and a location license is gonna be created instead.
        In this case the used products for the old customer's locations will be also deleted and the new one will be created.

        Parameters:
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
        status = Status(True)
        customer_license = CustomerLicense.objects.get(license_ptr_id = id)
        if customer:
            if not customer_license.customer == customer:
                status = LicenseController.__delete_used_products_for_customer(
                    customer = customer,
                    module   = module,
                )
            if status.status:
                customer_license.key         = key
                customer_license.detail      = detail
                customer_license.start_date  = start_date
                customer_license.end_date    = end_date
                customer_license.module      = module
                customer_license.customer    = customer
                customer_license.save()
        else:
            location_license = LocationLicense(
                id          = id,
                key         = key,
                detail      = detail,
                start_date  = start_date,
                end_date    = end_date,
                module      = module,
                location    = location,
            )
            status = LicenseController.__delete_used_products_for_customer(
                customer         = location.customer,
                module           = module,
                location_to_keep = location,
            )
            if status.status:
                customer_license.delete()
                location_license.save()
        
        return status

    @staticmethod
    def __delete_used_products_for_customer(customer, module, location_to_keep = None) -> Status:
        """
        Deletes the used products for the customers.
        You can optionally pass a location to keep.

        Parameters:
        customer         (Customer)      : customer the used products should be deleted
        module           (SoftwareModule): software module
        location_to_keep (Location)      : location to keep

        Returns:
        Status: delete status
        """
        status        = Status(True)
        location_kept = False
        locations     = Location.objects.filter(customer = customer)
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
            status = LicenseController.__create_used_product(
                location = location_to_keep,
                module   = module,
            )

        return status

    @staticmethod
    def __delete_redundant_used_product(location, module):
        """
        Deletes the used product of the given location-module-combination if it's redundant.

        Parameters:
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
    """
    The 'SoftwareProductController' manages the software product model.
    """

    @staticmethod
    def get_products_by_name(word: str, contains: bool = False) -> list:
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
    """
    The 'SoftwareModuleController' manages the software product model.
    """

    @staticmethod
    def get_module_names(limit: int = LIMIT) -> list:
        """
        Returns all module names as list.

        Parameters:
        limit (int): Maximum number of objects to load (default: 1000)

        Returns:
        list: module names
        """
        return list(SoftwareModule.objects.all()[:limit].values('id', 'name'))

    @staticmethod
    def get_modules_by_name(word: str, contains: bool = False) -> list:
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
