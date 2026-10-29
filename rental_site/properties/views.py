from django.shortcuts import render, redirect
from django.contrib import messages
from login.models import User, LandLord
from .models import Property, PropertyImage


# Create your views here.
def dashboard(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'dashboard.html')

def about(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'about.html')

def contact(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'contact.html')

def accommodation(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'my_accommodation.html')

def explore(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'explore.html')

def details(request):
    if 'username' not in request.session:
        return redirect('/login/')
    return render(request, 'details.html')

def user_profile(request):
    if 'username' not in request.session:
        return redirect('/login/')
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

    users = User.objects.all()
    properties = Property.objects.all().order_by('created_at')

    context = {
        'users': users,
        'properties': properties,
    }
    return render(request, 'admin-dashboard.html', context)

def admin_manage_users(request):
    access = admin_access(request)

    if access:
        return access

    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'admin-manage-users.html', context)

def admin_manage_properties(request):
    access = admin_access(request)
    if access:
        return access

    properties = Property.objects.all().order_by('created_at')
    context = {
        'properties': properties,
    }
    return render(request, 'admin-manage-properties.html', context)

def admin_approve(request):
    access = admin_access(request)
    if access:
        return access
    return render(request, 'admin-approve.html')

def add_accommodation(request):

    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(username=request.session['username']).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')
    
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        rent_value = request.POST['monthly_rent']
        city = request.POST['city']
        address = request.POST['address']
        is_available = request.POST['is_available']
        photos = request.FILES.getlist('photos')

        landlord = LandLord.objects.get(user=user)

        property = Property.objects.create(
            landlord=landlord,
            title=title,
            desc=desc,
            monthly_rent=int(rent_value),
            city=city,
            address=address,
            is_available=(is_available == 'yes')
        )
        for photo in photos:
            PropertyImage.objects.create(
            property=property,
            image_url=photo
            )
        messages.success(request, 'Accommodation added successfully!')
        return redirect('/accommodation/')

    return render(request, 'add_accommodation.html', {
        'account': user,
        'landlord': LandLord.objects.filter(user=user).first()
    })


def add_accommodation_success(request):
    # the success page is only shown for a listing that was really saved by this person
    user_id = request.session.get('user_id')
    property_id = request.session.get('added_property_id')
    new_property = None
    if user_id and property_id:
        new_property = Property.objects.filter(id=property_id, landlord__user__id=user_id).first()
    if new_property is None:
        return redirect('add_accommodation')
    return render(request, 'add_accommodation_success.html', {'new_property': new_property, 'account': new_property.landlord.user})
