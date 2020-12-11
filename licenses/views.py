from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from heartbeat.controllers import HeartbeatController
from .controllers import LicenseController, SoftwareModuleController
from customers.controllers import CustomerController, LocationController

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licenses_list')

def licensesList(request: WSGIRequest) -> HttpResponse:
    heartbeats = HeartbeatController.read()
    licenses   = LicenseController.read()
    context    = {
        'heartbeats': heartbeats,
        'licenses'  : licenses,
    }
    return render(request, 'licenses/list.html', context)

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

def save(request: WSGIRequest) -> HttpResponse:
    return redirect('licenses_list')
