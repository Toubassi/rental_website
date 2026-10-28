from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard),
    path('about/', views.about, name='about'),
    path('contact/', views.contact),
    path('accommodation/', views.accommodation),
    path('explore/', views.explore),
    path('details/', views.details),
]