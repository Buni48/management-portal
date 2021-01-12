from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .controllers import HeartbeatController

def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the heartbeat list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the heartbeat list
    """
    return redirect('heartbeat_list')

def heartbeatList(request: WSGIRequest) -> HttpResponse:
    """
    When the heartbeat list is called. Renders the heartbeat list.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: heartbeat list
    """
    usedProducts = HeartbeatController.read()
    countMissing = HeartbeatController.getCountMissing(usedProducts)
    context = {
        'used_products' : usedProducts,
        'count_missing' : countMissing,
    }
    return render(request, 'heartbeat/list.html', context)

def history(request: WSGIRequest) -> JsonResponse:
    """
    When the history is called as an ajax request.
    Gives the data of the heartbeats of a given used product id.

    Parameters:
    request (WSGIRequest): ajax request

    Returns:
    JsonResponse: heartbeats
    """
    response = JsonResponse({})
    if request.is_ajax():
        id = request.POST.get('id', '')
        heartbeats = HeartbeatController.get_heartbeats_for_used_product_id(id = id)
        """ context    = {
            'heartbeats': heartbeats.__dict__,
        } """
        response = JsonResponse(heartbeats.__dict__)
    
    return response
