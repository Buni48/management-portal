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
    return render(request, 'customers/list.html', context)

def customer(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    customers  = Customer.objects.all()
    locations  = Location.objects.all()
    context = {
        'heartbeats': heartbeats,
        'customers' : customers,
        'locations' : locations,
    }
    return render(request, 'customers/customer.html', context)
