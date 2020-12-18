from django.contrib import messages
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

def authentication(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Does the authentification.
    If authentification is successful it redirects to the homepage.
    Otherwise it redirects to the login page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the login page
    """
    if request.method == 'GET':
        return redirect('login')
    elif request.method == 'POST':
        username = str(request.POST['username'])
        password = str(request.POST['password'])
        user = auth_authenticate(request, username=username, password=password)
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

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: login page form
    """
    return render(request, 'user_management/login.html')

def logout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Loggs out the user and redirects to the logged out page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponseRedirect: redirection to the logged out page
    """
    auth_logout(request)
    return redirect('user_management:logged_out')

def loggedOut(request: WSGIRequest) -> HttpResponse:
    """
    When the logged out is called (usually after logout).
    Renders the logged out page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: logged out page
    """
    return render(request, 'user_management/logged_out.html')

def settings(request: WSGIRequest) -> HttpResponse:
    """
    When the settings are called. Renders the user settings page.

    Attributes:
    request (WSGIRequest): url request of the user

    Returns:
    HttpResponse: user settings page
    """
    return render(request, 'user_management/settings.html')
