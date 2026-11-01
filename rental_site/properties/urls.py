from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('accommodation/', views.accommodation, name='accommodation'),
    path('explore/', views.explore, name='explore'),

    path('ai-recommendations/', views.ai_recommendations, name='ai-recommendations'),
    path('generate-description/', views.generate_description, name='generate_description'),

    path('details/<int:id>/', views.details, name='details'),
    path('details/<int:id>/message/', views.send_message, name='send_message'),
    path('property/<int:property_id>/review/', views.add_review, name='add_review'),
    path('properties/', views.all_properties, name='all-properties'),
    path('profile/', views.user_profile, name='profile'),

    path('booking/<int:property_id>/', views.create_booking, name='create_booking'),
    path('my-booking-requests/', views.my_booking_requests, name='my_booking_requests'),
    path('notifications/', views.get_notifications,  name='get_notifications'),
    path('update-booking/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),

    path('admin-dashboard/', views.adminDashboard, name='admin-dashboard'),
    path('admin-manage-users/', views.admin_manage_users, name='admin-manage-users'),
    path('admin-manage-properties/', views.admin_manage_properties, name='admin-manage-properties'),
    path('admin-property-toggle/<int:id>/', views.toggle_property_availability, name='admin-property-toggle'),
    path('admin-property-delete/<int:id>/', views.delete_property, name='admin-property-delete'),
    path('admin-approve/', views.admin_approve, name='admin-approve'),
    path('add-accommodation/', views.add_accommodation, name='add_accommodation'),
    path('admin-user-toggle/<int:id>/', views.toggle_user_level, name='admin-user-toggle'),
    path('admin-user-delete/<int:id>/', views.delete_user, name='admin-user-delete'),
    path('admin-user/<int:id>/', views.admin_user_detail, name='admin-user-detail'),


]