from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from .filters import LicenceFilter

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licences_list')

def licencesList(request: WSGIRequest) -> HttpResponse:
    myFilter= LicenceFilter(request.GET, queryset= licencesList())
    return render(request, 'licences/list.html')
