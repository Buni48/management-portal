from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .models import Customer, Location
from heartbeat.models import Heartbeat

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('customers_list')

def customerList(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    customersA  = Customer.objects.filter(name__startswith='A')
    customersB  = Customer.objects.filter(name__startswith='B')
    customersC  = Customer.objects.filter(name__startswith='C')
    customersD  = Customer.objects.filter(name__startswith='D')
    customersE  = Customer.objects.filter(name__startswith='E')
    customersF  = Customer.objects.filter(name__startswith='F')

    context = {
        'heartbeats': heartbeats,
        'customersA' : customersA,
        'customersB' : customersB,
        'customersC' : customersC,
        'customersD' : customersD,
        'customersE' : customersE,
        'customersF' : customersF,

    }
    return render(request, 'customers/list.html', context=context)

def customer(request: WSGIRequest, id:int=0) -> HttpResponse:
    if id==0:
        return redirect('customers_list')

    heartbeats = Heartbeat.getHeartbeatsMissing()
    customer = Customer.objects.get(id = id)
    locations  = Location.objects.filter(customer_id = id)
    context = {
        'heartbeats': heartbeats,
        'locations' : locations,
        'customer' : customer,
    }
    return render(request, 'customers/customer.html', context=context)
