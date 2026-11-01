from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from login.models import User, UserManager, LandLord, EMAIL_REGEX
# Create your models here.
class MessageManager(models.Manager):
    def message_validator(self, PostData, user):
        errors = {}

        if len(PostData.get('message', '').strip()) < 1:
            errors['message'] = "Message cannot be empty"
        if not user.email:
            errors['email'] = "Please add an email to your profile before contacting a landlord."
        return errors

    def contact_validator(self, PostData):
        # Checks the Contact page form before the email is sent
        errors = {}
        if not PostData.get('full_name', '').strip():
            errors['full_name'] = "Please enter your full name."
        if not EMAIL_REGEX.match(PostData.get('email', '').strip()):
            errors['email'] = "Please enter a valid email."
        if not PostData.get('subject', '').strip():
            errors['subject'] = "Please enter a subject."
        if len(PostData.get('message', '').strip()) < 10:
            errors['message'] = "The message must be at least 10 characters."
        return errors


class Property(models.Model):
    landlord = models.ForeignKey(LandLord, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    desc = models.TextField()
    monthly_rent = models.PositiveBigIntegerField()  #<-- blocks negative rent.
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def increase_views(self):
        self.view_count += 1
        self.save()

    def get_images(self):
        return self.propertyimage_set.all().order_by('created_at')

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to='properties/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Booking(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rental_type = models.CharField(max_length=20, default='monthly')

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, default='pending')

    agreed_price = models.PositiveBigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True,blank=True)
    objects = MessageManager()
    profile_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_written")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def send_notification(self):
        # Emails the HomeFinder inbox about this message. Returns True if Gmail accepted it.
        client = self.profile_user
        sent_at = f"{localtime(self.created_at):%d %b %Y, %H:%M}"
        body = (
            f"Client name: {client.name}\n"
            f"Client email: {client.email}\n"
            f"Accommodation: {self.property.title}\n"
            f"Date and time: {sent_at}\n\n"
            f"Message:\n{self.message}"
        )
        email = EmailMultiAlternatives(
            subject=f"New Support Message from {client.name} – HomeFinder",
            body=body,   # plain-text version, for email apps that don't show HTML
            to=[settings.HOMEFINDER_NOTIFY_EMAIL],
            reply_to=[client.email],
        )
        html = render_to_string('emails/new_message.html', {
            'client': client,
            'property': self.property,
            'message': self.message,
            'sent_at': sent_at,
        })
        email.attach_alternative(html, "text/html")   # the designed version Gmail shows
        try:
            email.send()
            return True
        except (OSError, ValueError):
            return False


    
