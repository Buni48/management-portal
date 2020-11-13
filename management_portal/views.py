from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def home(request):
    return render(request, 'home.html')

def login(request):
    return redirect('user_management:login')

def logout(request):
    return redirect('user_management:logout')
