from django.shortcuts import render, redirect

def index(request):
    return redirect('updates_list')

def updatesList(request):
    return render(request, 'updates/list.html')
