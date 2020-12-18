from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from heartbeat.controllers import HeartbeatController
from .controllers import LicenseController, SoftwareModuleController
from customers.controllers import CustomerController, LocationController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the license list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the license list
    """
    return redirect('licenses_list')

def licensesList(request: WSGIRequest) -> HttpResponse:
    """
    When the license list is called. Renders the license list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: license list
    """
    status     = request.COOKIES.get('license_status_status')
    message    = request.COOKIES.get('license_status_message')
    heartbeats = HeartbeatController.read()
    licenses   = LicenseController.read()
    context    = {
        'heartbeats': heartbeats,
        'licenses'  : licenses,
        'status'    : status,
        'message'   : message,
    }

    response = render(request, 'licenses/list.html', context)
    response.delete_cookie('license_status_status')
    response.delete_cookie('license_status_message')

    return response

def create(request: WSGIRequest) -> HttpResponse:
    """
    When the license create is called. Renders the form to create a license.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: form to create license
    """
    heartbeats = HeartbeatController.read()
    modules    = SoftwareModuleController.getModuleNames()
    locations  = LocationController.getLocationNames()
    customers  = CustomerController.getCustomerNames()
    context    = {
        'title'     : 'Lizenz erstellen',
        'heartbeats': heartbeats,
        'modules'   : modules,
        'locations' : locations,
        'customers' : customers,
    }
    return render(request, 'licenses/edit.html', context)

def edit(request: WSGIRequest, id: int = 0) -> HttpResponse:
    """
    When the license edit is called.
    Renders the form to edit the license with the given id. 

    Attributes:
    request (WSGIRequest): url request of the user
    id      (int)        : id of the license to edit

    Returns:
    HttpResponse: form to edit license
    """
    if id < 1:
        return redirect('licenses_list')

    license    = LicenseController.getLicenseById(id = id)
    heartbeats = HeartbeatController.read()
    modules    = SoftwareModuleController.getModuleNames()
    locations  = LocationController.getLocationNames()
    customers  = CustomerController.getCustomerNames()
    context    = {
        'title'     : 'Lizenz bearbeiten',
        'license'   : license,
        'heartbeats': heartbeats,
        'modules'   : modules,
        'locations' : locations,
        'customers' : customers,
    }
    return render(request, 'licenses/edit.html', context)

def save(request: WSGIRequest) -> JsonResponse:
    """
    When the license save is called as an ajax request.
    Saves the data sent if valid and complete and returns the status.
    If id is also sent this license will be edited, otherwise a new one will be created.

    Attributes:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
    response = JsonResponse({})
    if request.is_ajax():
        id          = request.POST.get('id', '')
        key         = request.POST.get('key', '')
        detail      = request.POST.get('detail', '')
        start_date  = request.POST.get('start_date', '')
        end_date    = request.POST.get('end_date', '')
        module      = request.POST.get('module', '')
        location    = request.POST.get('location', '')
        customer    = request.POST.get('customer', '')

        status      = LicenseController.save(
            id          = id,
            key         = key,
            detail      = detail,
            start_date  = start_date,
            end_date    = end_date,
            module      = module,
            location    = location,
            customer    = customer,
        )
        response = JsonResponse(status.__dict__)
        if status.status:
            response.set_cookie('license_status_status' , status.status , 7)
            response.set_cookie('license_status_message', status.message, 7)

    return response

def delete(request: WSGIRequest, id: int = 0) -> HttpResponseRedirect:
    """
    When the license delete is called. Deletes the license with the given id.
    After that it redirects to the license list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the license list
    """
    response = redirect('licenses_list')
    if id > 0:
        status = LicenseController.delete(id = id)
        response.set_cookie('license_status_status' , status.status , 7)
        response.set_cookie('license_status_message', status.message, 7)

    return response
