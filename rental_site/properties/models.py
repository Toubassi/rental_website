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
    monthly_rent = models.IntegerField()
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    message = models.TextField()
    objects = MessageManager()
    profile_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_written")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
