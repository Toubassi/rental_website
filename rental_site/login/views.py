from django.shortcuts import render, redirect
from .models import UserManager, User
from django.contrib import messages
import bcrypt

# Create your views here.
def index(request):
  return render(request, 'index.html')

def login(request):
  return render(request, 'login.html')

def register(request):
  if request.method == 'POST':
    errors = User.objects.userValidator(request.POST)
    if errors:
      for key, value in errors.items():
        messages.error(request, value)
      return redirect('/register/')

    if User.objects.count() == 0:
      level = 0
    else:
      level = 1

    name = request.POST['name']
    username = request.POST['username']
    email = request.POST['email']
    dob = request.POST['dob']
    password = request.POST['password']
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    User.objects.create(
      name = name,
      username=username,
      dob=dob,
      email=email,
      password=hashed_pw,
    )
    request.session['username']
    return redirect('/home/')
  return render(request, 'registration.html')