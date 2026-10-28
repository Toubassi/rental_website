from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
def dashboard(request):
    return HttpResponse('dashboard')