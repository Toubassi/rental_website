from django.db import models
from django.contrib.auth.hashers import make_password
import re
from datetime import date, datetime

# Create your models here.

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
  def userValidator(self, postData):
    errors = {}

    name = postData.get('name', '').strip()
    email = postData.get('email', '').strip().lower()
    username = postData.get('username', '').strip()
    dob = postData.get('dob', '').strip()
    password = postData.get('password', '')          # passwords are NOT stripped
    confirm_password = postData.get('confirm_password', '')

    if not name:
      errors['name'] = 'Please enter your full name.'

    if not EMAIL_REGEX.match(email):
      errors['email'] = 'Invalid email address.'
    elif User.objects.filter(email=email).exists():
      errors['email'] = 'An account with this email already exists.'

    if not username:
      errors['username'] = 'Please choose a username.'
    elif User.objects.filter(username=username).exists():
      errors['username'] = 'This username is already taken.'

    if len(password) < 8:
      errors['password'] = 'Password must be at least 8 characters.'

    if not dob:
      errors['dob'] = 'Please enter a birthdate.'
    else:
      try:
        birthdate = datetime.strptime(dob, '%d/%m/%Y').date()    # the form sends DD/MM/YYYY
        today = date.today()
        if birthdate > today:
          errors['dob'] = 'Date of birth cannot be in the future.'
        elif birthdate.year < 1900:
          errors['dob'] = 'Please enter a valid birthdate.'
        elif birthdate > today.replace(year=today.year - 17):
          errors['dob'] = 'You must be at least 17 years old to register.'
      except ValueError:
        errors['dob'] = 'Please enter a valid birthdate.'

    if password != confirm_password:
      errors['confirm_password'] = 'Passwords do not match.'
    return errors

  def register(self, postData):
    # Only these fields are saved. user_level is never read from the form,
    # so it stays at the model default (1 = normal user).
    return self.create(
      name=postData['name'].strip(),
      username=postData['username'].strip(),
      email=postData['email'].strip().lower(),
      dob=date.fromisoformat(postData['dob'].strip()),
      password=make_password(postData['password']),   # Django's hasher: salted hash, never plain text
    )


class User(models.Model):
  name = models.CharField(max_length=255)
  username = models.CharField(max_length=255, unique=True)
  email = models.EmailField(unique=True)
  dob = models.DateField()
  avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
  password = models.CharField(max_length=255)
  user_level = models.IntegerField(default=1)
  objects = UserManager()
  created_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)

class LandLord(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord')
  phone_num = models.IntegerField()
  bio = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  update_at = models.DateTimeField(auto_now=True)