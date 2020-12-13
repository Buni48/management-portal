from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from heartbeat.controllers import HeartbeatController
from .controllers import LicenseController, SoftwareModuleController
from customers.controllers import CustomerController, LocationController

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licenses_list')

def licensesList(request: WSGIRequest) -> HttpResponse:
    message    = request.COOKIES.get('license_status_message')
    heartbeats = HeartbeatController.read()
    licenses   = LicenseController.read()
    context    = {
        'heartbeats': heartbeats,
        'licenses'  : licenses,
        'message'   : message,
    }
    response = render(request, 'licenses/list.html', context)
    response.delete_cookie('license_status_message')
    return response

def create(request: WSGIRequest) -> HttpResponse:
    heartbeats = HeartbeatController.read()
    modules    = SoftwareModuleController.getModuleNames()
    locations  = LocationController.getLocationNames()
    customers  = CustomerController.getCustomerNames()
    context    = {
        'heartbeats': heartbeats,
        'modules'   : modules,
        'locations' : locations,
        'customers' : customers,
    }
    return render(request, 'licenses/create.html', context)

def save(request: WSGIRequest) -> JsonResponse:
    response = JsonResponse({})
    if request.is_ajax():
        key         = request.POST.get('key', '')
        detail      = request.POST.get('detail', '')
        start_date  = request.POST.get('start_date', '')
        end_date    = request.POST.get('end_date', '')
        module      = request.POST.get('module', '')
        location    = request.POST.get('location', '')
        customer    = request.POST.get('customer', '')

        status      = LicenseController.save(
            key         = key,
            detail      = detail,
            start_date  = start_date,
            end_date    = end_date,
            module      = module,
            location    = location,
            customer    = customer,
        )
        response = JsonResponse(status)
        if status['status']:
            response.set_cookie('license_status_message', status['message'], 7)

    return response
