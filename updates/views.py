from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

def index(request: WSGIRequest) -> HttpResponse:
    return redirect('updates_list')

def updatesList(request: WSGIRequest) -> HttpResponse:
    return render(request, 'updates/list.html')
