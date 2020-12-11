from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from heartbeat.controllers import HeartbeatController
from customers.controllers import CustomerController, LocationController, ContactPersonController
from licenses.controllers  import LicenseController, SoftwareProductController, SoftwareModuleController
from updates.controllers   import UpdateController
import json

def index(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request: WSGIRequest) -> HttpResponse:
    heartbeats = HeartbeatController.read()
    countMissing = HeartbeatController.getCountMissing(heartbeats)
    countTotal = len(HeartbeatController.read(1000))
    licenses = LicenseController.read()
    licenseCount = LicenseController.getCounts(licenses)
    licensesExpired = licenseCount['missing']
    licensesOkay = licenseCount['valid']
    countOkay = countTotal - countMissing
    updateList = UpdateController.getStatus()
    updateCurrent = updateList[0]
    updateExpired = updateList[1]

    context = {
        'heartbeats'      : heartbeats,
        'count_missing'   : countMissing,
        'count_okay'      : countOkay,
        'licenses_okay'   : licensesOkay,
        'licenses_expired': licensesExpired,
        'update_current'  : updateCurrent,
        'update_expired'  : updateExpired,
    }
    return render(request, 'home.html', context)

def search(request: WSGIRequest) -> HttpResponse:
    heartbeats = HeartbeatController.read()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'search.html', context)

def searchResult(request: WSGIRequest) -> JsonResponse:
    response = {}
    if request.is_ajax():
        searchWord = request.POST.get('search_word', '')
        contains   = request.POST.get('contains', True)
        if contains == 'False':
            contains = False
        if len(searchWord) > 2 and len(searchWord) < 101:
            customers = CustomerController.getFilteredCustomers(word = searchWord, contains = contains)
            locations = LocationController.getLocationsByName(word = searchWord, contains = contains)
            contacts  = ContactPersonController.getContactPersonsByName(word = searchWord, contains = contains)
            products  = SoftwareProductController.getProductsByName(word = searchWord, contains = contains)
            modules   = SoftwareModuleController.getModulesByName(word = searchWord, contains = contains)
            response = {
                'customers'         : json.dumps(customers),
                'locations'         : json.dumps(locations),
                'contact_persons'   : json.dumps(contacts),
                'software_products' : json.dumps(products),
                'software_modules'  : json.dumps(modules),
            }
    else:
        return redirect('search')
    return JsonResponse(response)

def login(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:login')

def logout(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:logout')
