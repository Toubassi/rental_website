from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('accommodation/', views.accommodation, name='accommodation'),
    path('explore/', views.explore, name='explore'),
    path('details/', views.details, name='details'),
    path('profile/', views.user_profile, name='profile'),
]