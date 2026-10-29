from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="index"), #landing page
    path('home/', views.home, name="home"),

    path('login/', views.login,  name="login"),
    path('register/', views.register, name="register"),

    path('logout/', views.logout)
]