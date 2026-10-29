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

    path('admin-dashboard/', views.adminDashboard, name='admin-dashboard'),
    path('admin-manage-users/', views.admin_manage_users, name='admin-manage-users'),
    path('admin-manage-properties/', views.admin_manage_properties, name='admin-manage-properties'),
    path('admin-approve/', views.admin_approve, name='admin-approve'),
    path('add-accommodation/', views.add_accommodation, name='add_accommodation'),
]