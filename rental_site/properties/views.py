from django.shortcuts import render, redirect, HttpResponse
from .models import LandLord , Property , PropertyImage
from django.db import transaction, DatabaseError
from django.contrib import messages
from login.models import User

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
    properties = Property.objects.filter(is_available=True).order_by('-created_at')

    cards = []
    for property in properties:
        image = property.propertyimage_set.first()

        cards.append({
            'id': property.id,
            'title': property.title,
            'price': property.monthly_rent,
            'area': property.city,
            'summary': property.desc,
            'image_url': image.image_url.url if image else '',
            'type_label': 'Accommodation',
            'detail_url': '/details/',
        })

    return render(request, 'explore.html', {
        'cards': cards,
        'currency': '₪',
    })


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

        landlord = LandLord.objects.filter(user=user).first()

        if landlord is None:
            landlord = LandLord.objects.create(
                user=user,
                phone_num=int(request.POST['phone']),
                bio=''
                )

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
        return redirect('/explore/')

    return render(request, 'add_accommodation.html', {
        'account': user,
        'landlord': LandLord.objects.filter(user=user).first()
    })


