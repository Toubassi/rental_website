from django.db import models
from login.models import User, UserManager, LandLord
# Create your models here.
class MessageManager(models.Manager):
    def message_validator(self, PostData):
        errors = {}

        if len(PostData['message']) < 1:
            errors['message'] = "Message cannot be empty"
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
    objects = MessageManager()
    profile_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_written")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
