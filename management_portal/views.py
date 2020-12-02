from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from heartbeat.models import Heartbeat
from customers.models import Customer, Location
import json

def index(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'home.html', context)

def search(request: WSGIRequest) -> HttpResponse:
    heartbeats = Heartbeat.getHeartbeatsMissing()
    context = {
        'heartbeats': heartbeats,
    }
    return render(request, 'search.html', context)

def searchResult(request: WSGIRequest) -> JsonResponse:
    response = {}
    if request.is_ajax():
        searchWord = request.POST.get('search_word', '')
        contains   = request.POST.get('if_contains', True)
        if len(searchWord) > 2:
            customers = Customer.getFilteredCustomers(word = searchWord, contains = contains)
            locations = Location.getLocationsByName(word = searchWord, contains = contains)
            response = {
                'customers': json.dumps(customers),
                'locations': json.dumps(locations),
            }
    return JsonResponse(response)

def login(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:login')

def logout(request: WSGIRequest) -> HttpResponse:
    return redirect('user_management:logout')
