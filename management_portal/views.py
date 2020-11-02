from django.shortcuts import render, redirect

def index(request):
    return redirect('home')

def home(request):
    return render(request, 'home.html')

def login(request):
    return redirect('user_management:login')

def logout(request):
    return redirect('user_management:logout')

def loggedOut(request):
    return redirect('user_management:logged_out')
