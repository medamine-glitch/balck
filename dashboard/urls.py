from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    
    # Property Management
    path('properties/', views.property_management, name='property_management'),
    path('properties/add/', views.add_property, name='add_property'),
    path('properties/edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('properties/delete/<int:pk>/', views.delete_property, name='delete_property'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # Contact Management
    path('contacts/', views.contact_management, name='contact_management'),
    path('contacts/mark-read/<int:pk>/', views.mark_contact_read, name='mark_contact_read'),
    path('contacts/delete/<int:pk>/', views.delete_contact, name='delete_contact'),
    
    # Settings
    path('settings/', views.website_settings, name='website_settings'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # API endpoints
    path('api/property-stats/', views.api_property_stats, name='api_property_stats'),
    path('api/toggle-featured/', views.api_toggle_featured, name='api_toggle_featured'),
    path('api/toggle-availability/', views.api_toggle_availability, name='api_toggle_availability'),
]