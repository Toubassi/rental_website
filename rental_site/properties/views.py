from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def accommodation(request):
    return render(request, 'my_accommodation.html')

def explore(request):
    return render(request, 'explore.html')

def details(request):
    return render(request, 'details.html')
