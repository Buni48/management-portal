from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from heartbeat.controllers import HeartbeatController
from customers.controllers import CustomerController, ContactPersonController
from .controllers import LocationController
import json


def index(request: WSGIRequest) -> HttpResponseRedirect:
    """
    When the app root is called. Redirects to the customer list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the customer list
    """
    return redirect('customers_list')

def customer_list(request: WSGIRequest) -> HttpResponse:
    """
    When the customer list is called. Renders the customer list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: customer list
    """
    status       = request.COOKIES.get('customer_status_status')
    message      = request.COOKIES.get('customer_status_message')
    heartbeats   = HeartbeatController.read()
    customer_list = CustomerController.get_customers_for_each_letter()
    customers    = CustomerController.read()
    context      = {
        'heartbeats'    : heartbeats,
        'customer_list' : customer_list,
        'customers'     : customers,
        'status'        : status,
        'message'       : message,
    }

    response = render(request, 'customers/list.html', context = context)
    response.delete_cookie('customer_status_status')
    response.delete_cookie('customer_status_message')

    return response

def customer(request: WSGIRequest, id: int = 0):
    """
    When a customer is called. Renders the customer page with the given id.

    Parameters:
    request (WSGIRequest): url request of the user
    id      (int)        : id of the customer to load

    Returns:
    customer page
    """
    response = None
    if request.is_ajax and id == 0:
        customer_number = request.POST.get('customer_number', '')
        customer        = CustomerController.get_customer_by_customer_number(customer_number = customer_number)
        id              = customer.id
        response        = JsonResponse({'id': id})
    elif id < 1:
        return redirect('customers_list')


    status      = request.COOKIES.get('customer_status_status')
    message     = request.COOKIES.get('customer_status_message')
    heartbeats  = HeartbeatController.read()

    customer    = CustomerController.get_customer_by_id(id = id)
    locations   = LocationController.get_locations_by_customer(customer_id = id)
    context     = {
        'heartbeats': heartbeats,
        'locations' : locations,
        'customer'  : customer,
        'status'    : status,
        'message'   : message,
    }
    if not response:
        response = render(request, 'customers/customer.html', context = context)
        response.delete_cookie('customer_status_status')
        response.delete_cookie('customer_status_message')

    return response

def create(request: WSGIRequest) -> HttpResponse:
    """
    When the customer create is called. Renders the form to create a customer.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: form to create customer
    """
    heartbeats = HeartbeatController.read()
    context    = {
        'title'     : 'Kunden erstellen',
        'heartbeats': heartbeats,
    }
    return render(request, 'customers/edit.html', context)

def edit(request: WSGIRequest, id: int = 0) -> HttpResponse:
    """
    When the customer edit is called.
    Renders the form to edit the customer with the given id. 

    Parameters:
    request (WSGIRequest): url request of the user
    id      (int)        : id of the customer to edit

    Returns:
    HttpResponse: form to edit customer
    """
    if id < 1:
        return redirect('customers_list')

    customer   = CustomerController.get_customer_by_id(id = id)
    heartbeats = HeartbeatController.read()
    context    = {
        'title'     : 'Kunden bearbeiten',
        'customer'  : customer,
        'heartbeats': heartbeats,
    }
    return render(request, 'customers/edit.html', context)

def save(request: WSGIRequest) -> JsonResponse:
    """
    When the customer save is called as an ajax request.
    Saves the data sent if valid and complete and returns the status.
    If id is also sent this customer will be edited, otherwise a new one will be created.

    Parameters:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
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

def delete(request: WSGIRequest, id: int = 0) -> HttpResponseRedirect:
    """
    When the customer delete is called. Deletes the customer with the given id.
    After that it redirects to the customer list.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the customer list
    """
    response = redirect('customers_list')
    if id > 0:
        status = CustomerController.delete(id = id)
        response.set_cookie('customer_status_status' , status.status , 7)
        response.set_cookie('customer_status_message', status.message, 7)

    return response

def create_location(request: WSGIRequest, customer_id: int = 0) -> HttpResponse:
    """
    When the location create is called. Renders the form to create a location.
    Pass the id of the customer the location should belong to.

    Parameters:
    request     (WSGIRequest): url request of the user
    customer_id (int)        : id of the customer

    Returns:
    HttpResponse: form to create location
    """
    if customer_id < 1:
        return redirect('customers_list')

    heartbeats  = HeartbeatController.read()
    customer    = CustomerController.get_customer_by_id(id = customer_id)
    context     = {
        'title'     : 'Standort erstellen',
        'customer'  : customer,
        'heartbeats': heartbeats,
    }
    return render(request, 'customers/edit-location.html', context)

def edit_location(request: WSGIRequest, id: int = 0, customer_id: int = 0) -> HttpResponse:
    """
    When the location edit is called. Renders the form to edit the location with the given id.
    Pass also the id of the customer the location belongs to.

    Parameters:
    request     (WSGIRequest): url request of the user
    customer_id (int)        : id of the customer
    id          (int)        : id of the location to edit

    Returns:
    HttpResponse: form to edit location
    """
    if id < 1 or customer_id < 1:
        return redirect('customers_list')

    location   = LocationController.get_location_by_id(id = id)
    heartbeats = HeartbeatController.read()
    customer   = CustomerController.get_customer_by_id(id = customer_id)
    context    = {
        'title'     : 'Standort bearbeiten',
        'location'  : location,
        'customer'  : customer,
        'heartbeats': heartbeats,
    }
    return render(request, 'customers/edit-location.html', context)

def save_location(request: WSGIRequest) -> JsonResponse:
    """
    When the location save is called as an ajax request.
    Saves the data sent if valid and complete and returns the status.
    If id is also sent this location will be edited, otherwise a new one will be created.

    Parameters:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id            = request.POST.get('id', '')
        name          = request.POST.get('name', '')
        email_address = request.POST.get('email_address', '')
        phone_number  = request.POST.get('phone_number', '')
        street        = request.POST.get('street', '')
        house_number  = request.POST.get('house_number', '')
        postcode      = request.POST.get('postcode', '')
        city          = request.POST.get('city', '')
        customer      = request.POST.get('customer', '')
        status        = LocationController.save(
            id            = id,
            name          = name,
            email_address = email_address,
            phone_number  = phone_number,
            street        = street,
            house_number  = house_number,
            postcode      = postcode,
            city          = city,
            customer      = customer,
        )
        response = JsonResponse(status.__dict__)
        if status.status:
            response.set_cookie('customer_status_status' , status.status , 7)
            response.set_cookie('customer_status_message', status.message, 7)

    return response

def delete_location(request: WSGIRequest) -> JsonResponse:
    """
    When the location delete is called as an ajax request.
    Deletes the location with the given id and returns the status.

    Parameters:
    request (WSGIRequest): ajax delete request

    Returns:
    JsonResponse: delete status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id       = request.POST.get('id', '')
        status   = LocationController.delete(id = id)
        response = JsonResponse(status.__dict__)
        response.set_cookie('customer_status_status' , status.status , 7)
        response.set_cookie('customer_status_message', status.message, 7)

    return response

def contact_persons(request: WSGIRequest) -> JsonResponse:
    """
    When the history is called as an ajax request.
    Gives the data of the heartbeats of a given used product id.

    Parameters:
    request (WSGIRequest): ajax request

    Returns:
    JsonResponse: contact persons
    """
    response = JsonResponse({})
    if request.is_ajax:
        id              = request.POST.get('id', '')
        contact_persons = ContactPersonController.get_contact_persons_by_location(location_id = id)
        context         = {
            'contact_persons': json.dumps(contact_persons),
            'location_id'    : id,
        }
        response = JsonResponse(context)

    return response

def create_contact_person(request: WSGIRequest, location_id: int = 0, customer_id: int = 0) -> HttpResponse:
    """
    When the contact person create is called. Renders the form to create a contact person.
    Pass the id of the customer the contact person should belong to.

    Parameters:
    request     (WSGIRequest): url request of the user
    location_id (int)        : id of the location
    customer_id (int)        : id of the customer

    Returns:
    HttpResponse: form to create location
    """
    if location_id < 1 or customer_id < 1:
        return redirect('customers_list')

    heartbeats  = HeartbeatController.read()
    customer    = CustomerController.get_customer_by_id(id = customer_id)
    location    = LocationController.get_location_by_id(id = location_id)
    context     = {
        'title'     : 'Ansprechpartner erstellen',
        'customer'  : customer,
        'location'  : location,
        'heartbeats': heartbeats,
    }

    return render(request, 'customers/edit-contact-person.html', context)

def edit_contact_person(request: WSGIRequest, id: int = 0, location_id: int = 0, customer_id: int = 0) -> HttpResponse:
    """
    When the contact person create is called. Renders the form to create a contact person.
    Pass the id of the customer the contact person should belong to.

    Parameters:
    request     (WSGIRequest): url request of the user
    id (int)                 : id of the contact person
    location_id (int)        : id of the location
    customer_id (int)        : id of the customer

    Returns:
    HttpResponse: form to create location
    """
    if id < 1 or location_id < 1 or customer_id < 1:
        return redirect('customers_list')

    heartbeats      = HeartbeatController.read()
    customer        = CustomerController.get_customer_by_id(id = customer_id)
    location        = LocationController.get_location_by_id(id = location_id)
    contact_person  = ContactPersonController.get_contact_persons_by_id(id = id)
    context         = {
        'title'         : 'Ansprechpartner bearbeiten',
        'customer'      : customer,
        'location'      : location,
        'contact_person': contact_person,
        'heartbeats'    : heartbeats,
    }

    return render(request, 'customers/edit-contact-person.html', context)

def save_contact_person(request: WSGIRequest) -> JsonResponse:
    """
    When the contact person save is called as an ajax request.
    Saves the data sent if valid and complete and returns the status.
    If id is also sent this contact person will be edited, otherwise a new one will be created.

    Parameters:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id            = request.POST.get('id', '')
        first_name    = request.POST.get('first_name', '')
        last_name     = request.POST.get('last_name', '')
        email_address = request.POST.get('email_address', '')
        phone_number  = request.POST.get('phone_number', '')
        location      = request.POST.get('location', '')
        status        = ContactPersonController.save(
            first_name    = first_name,
            last_name     = last_name,
            email_address = email_address,
            phone_number  = phone_number,
            location      = location,
            id            = id,
        )
        response = JsonResponse(status.__dict__)
        if status.status:
            response.set_cookie('customer_status_status' , status.status , 7)
            response.set_cookie('customer_status_message', status.message, 7)

    return response

def delete_contact_person(request: WSGIRequest) -> JsonResponse:
    """
    When the contact person delete is called as an ajax request.
    Deletes the contact person with the given id and returns the status.

    Parameters:
    request (WSGIRequest): ajax delete request

    Returns:
    JsonResponse: delete status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id       = request.POST.get('id', '')
        status   = ContactPersonController.delete(id = id)
        response = JsonResponse(status.__dict__)
        response.set_cookie('customer_status_status' , status.status , 7)
        response.set_cookie('customer_status_message', status.message, 7)
    
    return response
