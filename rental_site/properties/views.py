from django.shortcuts import render, redirect, get_object_or_404
from .models import LandLord , Property , PropertyImage
from django.db import transaction, DatabaseError
from django.contrib import messages
from login.models import User, EMAIL_REGEX
import bcrypt

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
    # About Us is for visitors only: logged-in users go to their dashboard
    if 'username' in request.session:
        return redirect('/dashboard/')
    return render(request, 'about.html')

def contact(request):
    # Contact is open to everyone: visitors and logged-in users
    if request.method == 'POST':
        messages.success(request, "Thanks, we received your message.")
        return redirect('contact')
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
    if 'username' not in request.session:
        return redirect('login')
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
    property = get_object_or_404(Property, id=id)
    property.increase_views()
    context = {
        'property': property,
    }
    return render(request, 'details.html', context)

def all_properties(request):
    return redirect('explore')


def user_profile(request):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(username=request.session['username']).first()
    if user is None:
        request.session.flush()
        return redirect('/login/')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            name = request.POST.get('full_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip().lower()
            dob = request.POST.get('date_of_birth', '')
            avatar = request.FILES.get('avatar')

            errors = []
            if not name:
                errors.append("Please enter your full name.")
            if not username:
                errors.append("Please enter a username.")
            elif User.objects.filter(username=username).exclude(id=user.id).exists():
                errors.append("This username is already taken.")
            if not EMAIL_REGEX.match(email):
                errors.append("Please enter a valid email.")
            elif User.objects.filter(email=email).exclude(id=user.id).exists():
                errors.append("This email is already used.")
            if not dob:
                errors.append("Please enter your date of birth.")
            if avatar:
                if not avatar.content_type.startswith('image/'):
                    errors.append("The profile picture must be an image.")
                elif avatar.size > 2 * 1024 * 1024:
                    errors.append("The picture must be smaller than 2 MB.")

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                user.name = name
                user.username = username
                user.email = email
                user.dob = dob
                if avatar:
                    user.avatar = avatar
                user.save()
                request.session['username'] = username
                messages.success(request, "Your profile was updated.")
            return redirect('profile')

        elif form_type == 'password':
            current = request.POST.get('current_password', '')
            new = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')

            if not bcrypt.checkpw(current.encode(), user.password.encode()):
                messages.error(request, "Your current password is incorrect.")
            elif len(new) < 8:
                messages.error(request, "The new password must be at least 8 characters.")
            elif new != confirm:
                messages.error(request, "The new passwords do not match.")
            else:
                user.password = bcrypt.hashpw(new.encode(), bcrypt.gensalt()).decode()
                user.save()
                messages.success(request, "Your password was changed.")
            return redirect('profile')

    return render(request, 'user-profile.html', {'profile_user': user})


def admin_access(request):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(username = request.session['username']).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')

    if user.user_level != 1:
        return redirect('/dashboard/')

    return None
    
def adminDashboard(request):
    access = admin_access(request)
    if access:
        return access

    total_users = User.objects.count()

    total_properties = Property.objects.count()

    available_listings = Property.objects.filter(is_available=True).count()

    rented_listings = Property.objects.filter(is_available = False).count()


    users = User.objects.all()
    properties = Property.objects.all().order_by('-created_at')

    context = {
        'users': users,
        'properties': properties,
        'total_users': total_users,
        'total_properties': total_properties,
        'available_listings': available_listings,
        'rented_listings': rented_listings,
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

    properties = Property.objects.all().order_by('-created_at')
    context = {
        'properties': properties,
    }
    return render(request, 'admin-manage-properties.html', context)

def toggle_property_availability(request, id):
    access = admin_access(request)

    if access:
        return access

    if request.method == 'POST':
        property = Property.objects.filter(id=id).first()

        if property is None:
            messages.error(request, 'Property not found.')
            return redirect('/admin-manage-properties/')

        property.is_available = not property.is_available
        property.save()

        if property.is_available:
            messages.success(request, 'Property is now available.')
        else:
            messages.success(request, 'Property is now unavailable.')

    return redirect('/admin-dashboard/')

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

def delete_property(request, id):
    access = admin_access(request)

    if access:
        return access

    if request.method == 'POST':
        property = Property.objects.get(id=id)

        if property is None:
            messages.error(request, 'Property not found.')
            return redirect('/admin-dashboard/')

        property.delete()

        messages.success(request, 'Property deleted successfully!')

    return redirect('/admin-dashboard/')

def toggle_user_level(request, id):
    access = admin_access(request)

    if access:
        return access

    if request.method == 'POST':
        user = User.objects.filter(id=id).first()

        if user is None:
            messages.error(request, 'User not found.')
            return redirect('/admin-dashboard/')

        # Prevent changing your own admin privileges
        current_user = User.objects.filter(
            username=request.session['username']
        ).first()

        if user.id == current_user.id:
            messages.error(request, 'You cannot change your own role.')
            return redirect('/admin-dashboard/')

        # Prevent removing the last administrator
        if user.user_level == 1:
            admin_count = User.objects.filter(user_level=1).count()

            if admin_count == 1:
                messages.error(request, 'You cannot remove the last administrator.')
                return redirect('/admin-dashboard/')

        user.user_level = 0 if user.user_level == 1 else 1
        user.save()

        if user.user_level == 1:
            messages.success(request, 'User promoted to administrator.')
        else:
            messages.success(request, 'User demoted to normal user.')

    return redirect('/admin-dashboard/')

def delete_user(request, id):
    access = admin_access(request)

    if access:
        return access

    if request.method == 'POST':
        user = User.objects.get(id=id)

    current_user = User.objects.filter(username=request.session['username']).first()

    if user.id == current_user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('/admin-dashboard/')

    if user.user_level == 1:
        admin_count = User.objects.filter(user_level=1).count()

        if admin_count == 1:
            messages.error(request, 'You cannot delete the last administrator.')
            return redirect('/admin-dashboard/')

    user.delete()

    messages.success(request, 'User deleted successfully.')

    return redirect('/admin-dashboard/')
