from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard),
    path('about/', views.about, name='about'),
    path('contact/', views.contact),
    path('explore/', views.explore)
]