from django.shortcuts import render, redirect

def index(request):
    return redirect('customers_list')

def customerList(request):
    return render(request, 'customers/list.html')
