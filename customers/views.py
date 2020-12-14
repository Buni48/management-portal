from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from heartbeat.controllers import HeartbeatController
from customers.controllers import CustomerController
from .controllers import LocationController


def index(request: WSGIRequest) -> HttpResponse:
    return redirect('customers_list')


def customerList(request: WSGIRequest) -> HttpResponse:
    status       = request.COOKIES.get('customer_status_status')
    message      = request.COOKIES.get('customer_status_message')
    heartbeats   = HeartbeatController.read()
    customerList = CustomerController.getCustomersForEachLetter()
    context      = {
        'heartbeats'    : heartbeats,
        'customer_list' : customerList,
        'status'        : status,
        'message'       : message,
    }

    response = render(request, 'customers/list.html', context = context)
    response.delete_cookie('customer_status_status')
    response.delete_cookie('customer_status_message')

    return response


def customer(request: WSGIRequest, id: int = 0) -> HttpResponse:
    if id == 0:
        return redirect('customers_list')

    heartbeats  = HeartbeatController.read()
    customer    = CustomerController.getCustomerById(id = id)
    locations   = LocationController.getLocationsByCustomer(customer_id = id)
    context     = {
        'heartbeats': heartbeats,
        'locations' : locations,
        'customer'  : customer,
    }
    return render(request, 'customers/customer.html', context = context)


def create(request: WSGIRequest) -> HttpResponse:
    context = {
        'title': 'Kunden erstellen',
    }
    return render(request, 'customers/create.html', context)

def save(request: WSGIRequest) -> JsonResponse:
    response = JsonResponse({})
    if request.is_ajax:
        id              = request.POST.get('id', '')
        customer_number = request.POST.get('customer_number', '')
        name            = request.POST.get('name', '')
        status          = CustomerController.save(
            id              = id,
            customer_number = customer_number,
            name            = name,
        )
        response = JsonResponse(status.__dict__)
        if status.status:
            response.set_cookie('customer_status_status' , status.status , 7)
            response.set_cookie('customer_status_message', status.message, 7)

    return response
