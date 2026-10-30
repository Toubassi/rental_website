from django.shortcuts import render, redirect, HttpResponse
from .models import LandLord , Property , PropertyImage
from django.db import transaction, DatabaseError
from django.contrib import messages
from login.models import User

# Create your views here.
def dashboard(request):
    if 'username' not in request.session:
        return redirect('/login/')
    properties = Property.objects.filter(is_available=True)

    popular_properties = Property.objects.filter(
        is_available=True
    ).order_by('-view_count')[:3]

    context = {
        'properties': properties,
        'popular_properties': popular_properties
    }

    return render(request, 'dashboard.html', context)

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

    user = User.objects.filter(username=request.session['username']).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')

    landlord = LandLord.objects.filter(user=user).first()

    properties = Property.objects.none()

    if landlord:
        properties = Property.objects.filter(landlord=landlord).order_by('-created_at')

    total_listings = properties.count()
    available_listings = properties.filter(is_available=True).count()
    unavailable_listings = properties.filter(is_available=False).count()

    return render(request, 'my_accommodation.html', {
        'properties': properties,
        'account': user,
        'total_listings': total_listings,
        'available_listings': available_listings,
        'unavailable_listings': unavailable_listings
    })




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


def details(request, id):
    if 'username' not in request.session:
        return redirect('/login/')
    property = Property.objects.get(id=id)
    property.increase_views()
    context = {
        'property': property,
    }
    return render(request, 'details.html', context)

def all_properties(request):
    pass

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

        landlord = LandLord.objects.filter(user=user).first()

        if landlord is None:
            landlord = LandLord.objects.create(
                user=user,
                phone_num=int(request.POST['phone']),
                bio=request.POST['bio']
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


