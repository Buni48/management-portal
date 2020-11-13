from django.contrib import messages
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect

def authentication(request: WSGIRequest) -> HttpResponse:
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
    return render(request, 'user_management/login.html')

def logout(request: WSGIRequest) -> HttpResponse:
    auth_logout(request)
    return redirect('user_management:logged_out')

def loggedOut(request: WSGIRequest) -> HttpResponse:
    return render(request, 'user_management/logged_out.html')

def settings(request: WSGIRequest) -> HttpResponse:
    return render(request, 'user_management/settings.html')
