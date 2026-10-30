from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from django.db import IntegrityError
import bcrypt
from datetime import datetime


# Create your views here.
def home(request):
  return render(request, 'home.html')

def login(request):
  if request.method == "POST":
      
      email = request.POST['username']
      password = request.POST['password']

      try:
        user = User.objects.get(email=email)
      except User.DoesNotExist:
        messages.error(request, 'wrong email or password.')
        return redirect('login')
      
      try:
        correct_pass = bcrypt.checkpw(password.encode(), user.password.encode())
      except ValueError:
        correct_pass = False

      if not correct_pass:
        messages.error(request, 'wrong email or passowrd.')
        return redirect('login')

      request.session['username'] = user.username
      return redirect('dashboard')
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

    name = request.POST['name'].strip()
    username = request.POST['username'].strip()
    email = request.POST['email'].strip().lower()
    dob = datetime.strptime(request.POST['dob'].strip(), '%d/%m/%Y').date()   # DD/MM/YYYY -> a real date
    password = request.POST['password']
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
      User.objects.create(
        name = name,
        username=username,
        dob=dob,
        email=email,
        password=hashed_pw,
        user_level=level,
      )
    except IntegrityError:
      # two identical submits at the same moment: the database refuses the second one
      messages.error(request, 'That username or email is already registered.')
      return redirect('/register/')

    request.session['username'] = username
    return redirect('/dashboard/')
  return render(request, 'registration.html')

def logout(request):
  request.session.flush()
  return redirect('/')
