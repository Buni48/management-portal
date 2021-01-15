from django.contrib import messages
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from management_portal.constants import DATETIME_TYPE
from .controllers import UserController

def authentication(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Does the authentification.
    If authentification is successful it redirects to the homepage.
    Otherwise it redirects to the login page.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the login page
    """
    if request.method == 'GET':
        return redirect('login')
    elif request.method == 'POST':
        username = str(request.POST['username'])
        password = str(request.POST['password'])
        user = auth_authenticate(
            request,
            username = username,
            password = password
        )
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Benutzername oder Passwort falsch!')
            return redirect('login')
    else:
        return redirect('login')

def login(request: WSGIRequest) -> HttpResponse:
    """
    When the login is called. Renders the login page form.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: login page form
    """
    return render(request, 'user_management/login.html')

def logout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Loggs out the user and redirects to the logged out page.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the logged out page
    """
    auth_logout(request)
    return redirect('user_management:logged_out')

def logged_out(request: WSGIRequest) -> HttpResponse:
    """
    When the logged out is called (usually after logout).
    Renders the logged out page.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: logged out page
    """
    return render(request, 'user_management/logged_out.html')

def settings(request: WSGIRequest) -> HttpResponse:
    """
    When the settings are called. Renders the user settings page.

    Parameters:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: user settings page
    """
    if not isinstance(request.user, AnonymousUser):
        request.user.last_login  = request.user.last_login.strftime(DATETIME_TYPE)
        request.user.date_joined = request.user.date_joined.strftime(DATETIME_TYPE)

    message = request.COOKIES.get('user_status_message')
    context = {
        'message': message,
    }

    return render(request, 'user_management/settings.html', context)

def change_profile(request: WSGIRequest) -> JsonResponse:
    """
    When the profile change is called as an ajax request.
    Saves the profile data sent if valid and complete and returns the status.

    Parameters:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id          = request.user.id
        username    = request.POST.get('username', '')
        email       = request.POST.get('email', '')
        first_name  = request.POST.get('first_name', '')
        last_name   = request.POST.get('last_name', '')
        status      = UserController.change_profile(
            id          = id,
            username    = username,
            email       = email,
            first_name  = first_name,
            last_name   = last_name,
        )
        response = JsonResponse(status.__dict__)

        if status.status:
            response.set_cookie('user_status_message', status.message, 7)

    return response

def change_password(request: WSGIRequest) -> JsonResponse:
    """
    When the password change is called as an ajax request.
    Changes the password sent if valid and complete and returns the status.

    Parameters:
    request (WSGIRequest): ajax save request

    Returns:
    JsonResponse: save status
    """
    response = JsonResponse({})
    if request.is_ajax:
        id              = request.user.id
        old_password    = request.POST.get('old_password', '')
        new_password_1  = request.POST.get('new_password_1', '')
        new_password_2  = request.POST.get('new_password_2', '')
        status = UserController.change_password(
            id              = id,
            old_password    = old_password,
            new_password_1  = new_password_1,
            new_password_2  = new_password_2,
        )
        response = JsonResponse(status.__dict__)

        if status.status:
            response.set_cookie('user_status_status' , status.status , 7)
            response.set_cookie('user_status_message', status.message, 7)

    return response
