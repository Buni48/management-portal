from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('licences_list')

def licencesList(request: WSGIRequest) -> HttpResponse:
    return render(request, 'licences/list.html')
