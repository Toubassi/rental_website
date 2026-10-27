from django.urls import path
from . import views

urlpatterns = [
    path('', views.index), #landing page

    path('login/', views.login),
    path('register/', views.register),
]