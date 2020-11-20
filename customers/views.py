from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .models import *

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('customers_list')

def customerList(request: WSGIRequest) -> HttpResponse:
    return render(request, 'customers/list.html')

def customer(request: WSGIRequest) -> HttpResponse:
    customers = Customer.objects.all()
    locations = Location.objects.all()
    context = {
        'customers' : customers,
        'locations' : locations,
    }
    return render(request, 'customers/customer.html', context)
