from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages

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

def user_profile(request):
    return render(request, 'user-profile.html')


def admin_access(request):
    if 'username' not in request.session:
        return redirect('/')
    username = request.session['username']
    for user in User.objects.all():
        if user.username == username:
            if user.user_level == 1:
                return None
            return redirect('/dashboard/')

def adminDashboard(request):
    access = admin_access(request)
    if access:
        return access
    return render(request, 'admin-dashboard.html')

def admin_manage_users(request):
    access = admin_access(request)

    if access:
        return access
    return render(request, 'admin-manage-users.html')

def admin_manage_properties(request):
    access = admin_access(request)
    if access:
        return access
    return render(request, 'admin-manage-properties.html')

def admin_approve(request):
    access = admin_access(request)
    if access:
        return access
    return render(request, 'admin-approve.html')
