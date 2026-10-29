from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
import bcrypt
# Create your views here.
def home(request):
  return render(request, 'home.html')

def login(request):
  if request.method == "POST":
    try:
      user =  User.objects.get(email = request.POST['user_email'])
      if user:
        if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
          request.session['user_email'] = user.email
          return redirect('/properties/dashboard/')
    except:
      messages.error(request, "The email or password is incorrect")
      return redirect('/login/')
    request.session['user_email'] = user.email
    return redirect('/login/')
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
