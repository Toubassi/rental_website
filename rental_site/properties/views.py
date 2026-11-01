from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import LandLord , Property , PropertyImage, Message, Booking
from django.db import transaction, DatabaseError
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from login.models import User, EMAIL_REGEX
from datetime import date
import bcrypt
from .ai_services import recommend_properties
from django.http import JsonResponse
from .ai_services import generate_property_description
from django.db.models import Max, Q

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
        errors = Message.objects.contact_validator(request.POST)
        if errors:
            for error in errors.values():
                messages.error(request, error)
            return redirect('contact')

        name = request.POST['full_name'].strip()
        email = request.POST['email'].strip()
        letter = EmailMessage(
            subject="HomeFinder Contact: " + request.POST['subject'].strip(),
            body=f"From: {name} <{email}>\n\n{request.POST['message'].strip()}",
            to=[settings.HOMEFINDER_NOTIFY_EMAIL],   # the site's own inbox
            reply_to=[email],                   # "Reply" answers the visitor
        )
        try:
            letter.send()
            messages.success(request, "Thanks, your message was sent. We'll reply by email soon.")
        except (OSError, ValueError):
            messages.error(request, "Sorry, the message could not be sent. Please try again later.")
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

    available = Property.objects.filter(is_available=True)
    properties = available

    min_price = request.GET.get('min_price', '').strip()
    max_price = (request.GET.get('max_price', '').strip()
                 or request.GET.get('max_top', '').strip())
    q = request.GET.get('q', '').strip()
    if q:
       properties = properties.filter(Q(city__icontains=q) | Q(title__icontains=q))
    sort = request.GET.get('sort', 'newest')

    if min_price.isdigit():
        properties = properties.filter(monthly_rent__gte=int(min_price))
    if max_price.isdigit():
        properties = properties.filter(monthly_rent__lte=int(max_price))

    sort_choices = [
        ('newest', 'Newest first'),
        ('popular', 'Most popular'),
        ('price_asc', 'Price: low to high'),
        ('price_desc', 'Price: high to low'),
    ]
    order = {
        'newest': ('-created_at',),
        'popular': ('-view_count', '-created_at'),
        'price_asc': ('monthly_rent', '-created_at'),
        'price_desc': ('-monthly_rent', '-created_at'),
    }
    properties = properties.order_by(*order.get(sort, order['newest']))

    top = available.aggregate(Max('monthly_rent'))['monthly_rent__max'] or 1000
    price_limit = ((int(top) // 100) + 1) * 100

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
    'filters': {'q': q, 'min_price': min_price, 'max_price': max_price, 'sort': sort},
    'sort_choices': sort_choices,
    'count': len(cards),
    'price_limit': price_limit,
})


def details(request, id):
    if 'username' not in request.session:
        return redirect('/login/')
    property = get_object_or_404(Property, id=id)
    property.increase_views()
    context = {
        'property': property,
        'images': property.get_images(),
        'landlord': property.landlord,
        'currency': '₪',
    }
    return render(request, 'details.html', context)

def send_message(request, id):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(username=request.session['username']).first()
    if user is None:
        request.session.flush()
        return redirect('/login/')

    property = get_object_or_404(Property, id=id)
    if request.method != 'POST':
        return redirect('details', id=id)

    errors = Message.objects.message_validator(request.POST, user)
    back = reverse('details', args=[id]) + '#message-form'   # back to the message box, so the result is in view
    if errors:
        for error in errors.values():
            messages.error(request, error)
        return redirect(back)

    message = Message.objects.create(
        message=request.POST['message'].strip(),
        profile_user=user,
        property=property,
    )
    if message.send_notification():
        messages.success(request, "Your message was sent. The provider will reply to your email.")
    else:
        messages.warning(request, "Your message was saved, but the email notification could not be sent.")
    return redirect(back)

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

############# Admins #############3

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
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        is_available = request.POST['is_available']
        photos = request.FILES.getlist('photos')

        phone_digits = ''.join(ch for ch in request.POST.get('phone', '') if ch.isdigit())
        rent_text = str(rent_value).strip()
        problems = []
        if not rent_text.isdigit():
            problems.append('Please enter the monthly rent as a number.')
        if LandLord.objects.filter(user=user).first() is None and not phone_digits:
            problems.append('Please enter a phone number.')
        if problems:
            for problem in problems:
                messages.error(request, problem)
            return redirect('add_accommodation')

        landlord = LandLord.objects.filter(user=user).first()

        if landlord is None:
            landlord = LandLord.objects.create(
                user=user,
                phone_num=int(phone_digits),
                bio=request.POST.get('bio', '')
                )

        try:
            latitude = float(latitude)
            longitude = float(longitude)

            if latitude < -90 or latitude > 90:
                latitude = None
                longitude = None

            if longitude < -180 or longitude > 180:
                latitude = None
                longitude = None

        except (ValueError, TypeError):
            latitude = None
            longitude = None

        property = Property.objects.create(
            landlord=landlord,
            title=title,
            desc=desc,
            monthly_rent=int(rent_value),
            city=city,
            address=address,
            latitude=latitude,
            longitude=longitude,
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

def delete_property(request, id):
    access = admin_access(request)

    if access:
        return access

    if request.method == 'POST':
        property = Property.objects.filter(id=id).first()

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
            if request.method != 'POST':
             return redirect('/admin-dashboard/')

    user = User.objects.filter(id=id).first()
    if user is None:
        messages.error(request, 'User not found.')
        return redirect('/admin-dashboard/')

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


##### making a booking ##############

def create_booking(request, property_id):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(username=request.session['username']).first()
    if user is None:
        request.session.flush()
        return redirect('/login/')

    property = get_object_or_404(Property, id=property_id)

    if not property.is_available:
        messages.error(request, "This property is unavailable.")
        return redirect(f'/details/{property_id}/')

    if user.id == property.landlord.user.id:
        messages.error(request, "You cannot book your own property.")
        return redirect(f'/details/{property_id}/')
    
    if request.method != 'POST':
        return redirect(f'/details/{property_id}/')
    ######## we dont want a booking to be created when the link is visited through url

    rental_type = request.POST.get('rental_type')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if not rental_type or not start_date or not end_date:
        messages.error(request, "Please fill in all booking fields.")
        return redirect(f'/details/{property_id}/')

    if rental_type != 'monthly' and rental_type != 'flexible':
        messages.error(request, "Invalid rental type.")
        return redirect(f'/details/{property_id}/')


    ################ not allowing past dates/invalid
    try:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
    except ValueError:
        messages.error(request, "Please enter valid dates.")
        return redirect(f'/details/{property_id}/')


    if end_date <= start_date:
        messages.error(request, "The end date must be after the start date.")
        return redirect(f'/details/{property_id}/')

    if start_date < date.today():
        messages.error(request, "You cannot book dates in the past.")
        return redirect(f'/details/{property_id}/')

    if rental_type == 'monthly':
        agreed_price = property.monthly_rent
    else:
        daily_price = property.monthly_rent / 30
        number_of_days = (end_date - start_date).days
        agreed_price = round(daily_price * number_of_days)
    
    Booking.objects.create(
        property=property, 
        user=user,
        rental_type=rental_type,
        start_date=start_date,
        end_date=end_date,
        agreed_price=agreed_price
        )

    messages.success(request, "Your booking request was submitted successfully")
    return redirect(f'/details/{property_id}/')

def my_booking_requests(request):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(
        username=request.session['username']
    ).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')

    landlord = LandLord.objects.filter(user=user).first()

    if landlord is None:
        messages.error(request, "You are not registered as a landlord.")
        return redirect('/dashboard/')

    bookings = Booking.objects.filter(
        property__landlord=landlord
        ).order_by('-created_at')

    context = {
        'bookings': bookings
        }

    return render(request, 'my-booking-requests.html', context)

def update_booking_status(request, booking_id):

    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(
        username=request.session['username']
    ).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')

    landlord = LandLord.objects.filter(user=user).first()

    if landlord is None:
        return redirect('/dashboard/')

    if request.method != 'POST':
        return redirect('/my-booking-requests/')

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        property__landlord=landlord
    )

    new_status = request.POST.get('status')

    if new_status != 'approved' and new_status != 'rejected':
        messages.error(request, "Invalid booking action.")
        return redirect('/my-booking-requests/')

    if booking.status != 'pending':
        messages.error(request, "This booking has already been processed.")
        return redirect('/my-booking-requests/')

    booking.status = new_status
    booking.save()

    messages.success(request, "Booking status updated successfully!")

    return redirect('/my-booking-requests/')
  
def admin_user_detail(request, id):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    current = User.objects.filter(username=username).first()
    if not current or current.user_level != 1:
        return redirect('/dashboard/')
    target = get_object_or_404(User, id=id)

    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        if not new_username or not new_email:
            messages.error(request, 'Username and email are required.')
        elif User.objects.filter(username=new_username).exclude(id=target.id).exists():
            messages.error(request, 'That username is already taken.')
        elif User.objects.filter(email=new_email).exclude(id=target.id).exists():
            messages.error(request, 'That email is already used.')
        else:
            target.username = new_username
            target.email = new_email
            target.save()
            if target.id == current.id:
                request.session['username'] = new_username
            messages.success(request, 'User updated.')
        return redirect('admin-user-detail', id=target.id)

    return render(request, 'admin-user-detail.html', {'target': target})

#################### Ai here ###################################

def ai_recommendations(request):
    if 'username' not in request.session:
        return redirect('/login/')

    user = User.objects.filter(
        username=request.session['username']
    ).first()

    if user is None:
        request.session.flush()
        return redirect('/login/')

    return render(request, 'ai_recommendations.html')


def ai_recommendations(request):
    if 'username' not in request.session:
        return redirect('login')
    if request.method == 'POST':

        city = request.POST.get('city', '').strip()
        budget = request.POST.get('budget', '').strip()
        accommodation_type = request.POST.get('accommodation_type', '')
        bedrooms = request.POST.get('bedrooms', '')
        move_in_date = request.POST.get('move_in_date', '')
        preferences = request.POST.get('preferences', '').strip()

        # Validate required information
        if not city or not budget:
            return render(request, 'ai_recommendations.html', {
                'error': 'Please enter your preferred city and budget.'
            })

        try:
            budget = int(budget)
            if budget <= 0:
                raise ValueError
        except ValueError:
            return render(request, 'ai_recommendations.html', {
                'error': 'Please enter a valid monthly budget.'
            })

        # Retrieve available properties within the user's budget
        available_properties = Property.objects.filter(
            is_available=True,
            city__icontains=city,
            monthly_rent__lte=budget
        )

        # Prepare property information for Gemini
        property_data = []

        for property in available_properties:
            property_data.append({
                'id': property.id,
                'title': property.title,
                'city': property.city,
                'description': property.desc,
                'monthly_rent': property.monthly_rent
            })

        user_preferences = {
            'city': city,
            'budget': budget,
            'accommodation_type': accommodation_type,
            'bedrooms': bedrooms,
            'move_in_date': move_in_date,
            'additional_preferences': preferences
        }

        recommendations = []

        if property_data:
            try:
                ai_response = recommend_properties(
                    user_preferences,
                    property_data
                )

                # Only accept IDs belonging to our original database results
                for recommendation in ai_response.get('recommendations', []):
                    property_id = recommendation.get('property_id')

                    for property in available_properties:
                        if property.id == property_id:
                            recommendations.append({
                                'property': property,
                                'reason': recommendation.get('reason', '')
                            })
                            break

            except Exception as e:
                print("AI recommendation error:", e)
                return render(request, 'ai_recommendations.html', {
                    'error': 'We could not generate recommendations. Please try again.'
                })

        return render(request, 'ai_recommendations.html', {
            'recommendations': recommendations,
            'submitted': True,
            'preferences': user_preferences
        })

    return render(request, 'ai_recommendations.html')

def generate_description(request):
    if 'username' not in request.session:
        return JsonResponse({
            'error': 'Please log in first.'
        }, status=401)

    if request.method != 'POST':
        return JsonResponse({
            'error': 'Invalid request method.'
        }, status=405)

    title = request.POST.get('title', '').strip()
    city = request.POST.get('city', '').strip()
    address = request.POST.get('address', '').strip()
    rent = request.POST.get('monthly_rent', '').strip()

    if not title or not city or not address or not rent:
        return JsonResponse({
            'error': 'Please fill in the title, city, address, and rent first.'
        }, status=400)

    try:
        rent = int(rent)
        if rent <= 0:
            raise ValueError
    except ValueError:
        return JsonResponse({
            'error': 'Please enter a valid monthly rent.'
        }, status=400)

    property_info = {
        'title': title,
        'city': city,
        'address': address,
        'monthly_rent': rent
    }

    try:
        description = generate_property_description(property_info)

        if not description:
            raise ValueError('Empty AI response')

        return JsonResponse({
            'description': description
        })

    except Exception as e:
        print('Description generation error:', e)

        return JsonResponse({
            'error': 'Could not generate a description. Please try again.'
        }, status=500)