from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('customers_list')

def customerList(request: WSGIRequest) -> HttpResponse:
    return render(request, 'customers/list.html')
