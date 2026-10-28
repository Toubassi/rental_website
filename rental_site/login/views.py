from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages

# Create your views here.
def home(request):
  return render(request, 'home.html')

def login(request):
  return render(request, 'login.html')

def register(request):
  if request.method == 'POST':
    errors = User.objects.userValidator(request.POST)
    if errors:
      for key, value in errors.items():
        messages.error(request, value)
      return redirect('/register/')

    # register() saves the user and hashes the password with Django's make_password
    user = User.objects.register(request.POST)
    request.session['username'] = user.username
    return redirect('/home/')
  return render(request, 'registration.html')
