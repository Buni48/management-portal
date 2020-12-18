from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from heartbeat.controllers import HeartbeatController
from customers.controllers import CustomerController, LocationController, ContactPersonController
from licenses.controllers  import LicenseController, SoftwareProductController, SoftwareModuleController
from updates.controllers   import UpdateController
import json

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the website root is called.
    If the user is logged in it redirects to the homepage.
    If the user is logged out it redirects to the login page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the homepage or login page
    """
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request: WSGIRequest) -> HttpResponse:
    """
    When home is called. Renders the homepage with the charts.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: homepage
    """
    heartbeats      = HeartbeatController.read()
    licenses        = LicenseController.read()
    heartbeatsCount = HeartbeatController.getCounts(heartbeats)
    licensesCount   = LicenseController.getCounts(licenses)
    updatesCount    = UpdateController.getCounts(heartbeats)

    context = {
        'heartbeats'      : heartbeats,
        'heartbeats_count': heartbeatsCount,
        'licenses_count'  : licensesCount,
        'updates_count'   : updatesCount,
    }
    return render(request, 'home.html', context)

def search(request: WSGIRequest) -> HttpResponse:
    """
    When the search is called. Renders the global search form.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: global search form
    """
    heartbeats = HeartbeatController.read()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'search.html', context)

def searchResult(request: WSGIRequest) -> JsonResponse:
    """
    When the search result is called as an ajax request.
    Searches for customers, locations, contact persons, software products and software modules by a given search word.
    It returns all the search results grouped by tables.

    Attributes:
    request (WSGIRequest): ajax request

    Returns:
    JsonResponse: serach result
    """
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

def login(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Redirects to the login page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the login page
    """
    return redirect('user_management:login')

def logout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Redirects to the logout page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the logout page
    """
    return redirect('user_management:logout')
