from django.db import models
import re
from datetime import date

# Create your models here.

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
  def userValidator(self, postData):
    errors = {}

    email = postData.get('email', '').strip()
    username = postData.get('username', '').strip()
    bday = postData.get('bday', '').strip()    
    password = postData.get('password', "").strip()
    confirm_password = postData.get('confirm_password', '').strip()

    if not EMAIL_REGEX.match(postData["email"]):
      errors['email'] = "Invalid email address."

    if User.objects.filter(email):
      errors['email'] = 'This username is already in use.'

    if User.objects.filter(username):
      errors['username'] = 'This username is already taken.'

    if len(password) < 8:
      errors['password'] = 'Password must be at least 8 characters.'

    if not bday:
      errors['bday'] = 'Please enter a birthdate.'
    else:
      try:
        birthdate = date.fromisoformat(bday)
        today = date.today()
        if birthdate >= today:
          errors['bday'] = 'You must be born to register'
        elif birthdate > date.today().replace(year=date.today().year - 17):
          errors['bday'] = 'You must be at least 17 years old to register.'
      except ValueError:
        errors['bday'] = 'Please enter a valid birthdate.'
    if password != confirm_password:
      errors['confirm_password'] = 'Passwords do not match.'
    return errors

    
class User(models.Model):
  name = models.CharField(max_length=255)
  username = models.CharField(max_length=255, unique=True)
  email = models.EmailField(unique=True)
  dob = models.DateField()
  password = models.CharField(max_length=255)
  user_level = models.IntegerField(default=1)
  objects = UserManager()
  created_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)

