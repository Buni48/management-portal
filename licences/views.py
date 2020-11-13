from django.shortcuts import render, redirect

def index(request):
    return redirect('licences_list')

def licencesList(request):
    return render(request, 'licences/list.html')
