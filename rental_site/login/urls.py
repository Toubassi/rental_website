from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,  name="index"), #landing page

    path('login/', views.login,  name="login"),
    path('register/', views.register, name="register"),
]