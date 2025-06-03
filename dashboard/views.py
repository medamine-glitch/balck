# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
from django.urls import reverse

from properties.models import Property, Contact, PropertyImage
from .models import PropertyView, ContactSubmission, WebsiteSettings, DashboardUser
from .forms import PropertyForm, WebsiteSettingsForm, UserProfileForm

def is_superuser(user):
    return user.is_superuser

def dashboard_login(request):
    # If user is already authenticated and is superuser, redirect to dashboard
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard:overview')
    # If user is authenticated but not superuser, redirect to home
    elif request.user.is_authenticated:
        messages.error(request, _('Vous n\'avez pas accès au tableau de bord.'))
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, _('Connexion réussie!'))
            return redirect('dashboard:overview')
        else:
            messages.error(request, _('Identifiants invalides ou accès non autorisé.'))
    
    return render(request, 'dashboard/login.html')

@login_required
def dashboard_logout(request):
    logout(request)
    messages.success(request, _('Déconnexion réussie!'))
    return redirect('home')

@login_required
@user_passes_test(is_superuser)
def dashboard_overview(request):
    # Basic property stats
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(available=True).count()
    featured_properties = Property.objects.filter(featured=True).count()
    
    # Views in last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    views_last_30_days = PropertyView.objects.filter(timestamp__gte=thirty_days_ago).count()
    
    # Contact stats
    total_contacts = ContactSubmission.objects.count()
    unread_contacts = ContactSubmission.objects.filter(is_read=False).count()
    
    # Most viewed properties
    most_viewed = Property.objects.annotate(
        view_count=Count('views', filter=Q(views__timestamp__gte=thirty_days_ago))
    ).order_by('-view_count')[:5]
    
    # Recent contacts
    recent_contacts = ContactSubmission.objects.all().order_by('-timestamp')[:5]
    
    # Views chart data
    daily_views = PropertyView.objects.filter(
        timestamp__gte=thirty_days_ago
    ).annotate(
        day=TruncDate('timestamp')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    chart_data = {
        'labels': [view['day'].strftime('%d/%m') for view in daily_views],
        'data': [view['count'] for view in daily_views]
    }
    
    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'featured_properties': featured_properties,
        'active_properties': available_properties,  # Same as available for now
        'views_last_30_days': views_last_30_days,
        'total_contacts': total_contacts,
        'unread_contacts': unread_contacts,
        'most_viewed': most_viewed,
        'recent_contacts': recent_contacts,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'dashboard/overview.html', context)

@login_required
@user_passes_test(is_superuser)
def property_management(request):
    properties = Property.objects.all()
    
    # Handle search and filters
    search = request.GET.get('search')
    property_type = request.GET.get('type')
    status = request.GET.get('status')
    
    if search:
        properties = properties.filter(
            Q(title__icontains=search) |
            Q(title_ar__icontains=search) |
            Q(city__icontains=search) |
            Q(address__icontains=search)
        )
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if status:
        if status == 'available':
            properties = properties.filter(available=True)
        elif status == 'unavailable':
            properties = properties.filter(available=False)
        elif status == 'featured':
            properties = properties.filter(featured=True)
    
    # Pagination
    paginator = Paginator(properties, 10)  # Show 10 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'property_type': property_type,
        'status': status,
        'property_types': Property.PROPERTY_TYPES,
    }
    return render(request, 'dashboard/property_management.html', context)

@login_required
@user_passes_test(is_superuser)
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save()
            messages.success(request, _('La propriété a été ajoutée avec succès.'))
            return redirect('dashboard:property_management')
        else:
            messages.error(request, _('Veuillez corriger les erreurs ci-dessous.'))
    else:
        form = PropertyForm()
    
    return render(request, 'dashboard/add_property.html', {'form': form})

@login_required
@user_passes_test(is_superuser)
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            
            # Handle image deletion if requested
            images_to_delete = request.POST.getlist('delete_images')
            if images_to_delete:
                PropertyImage.objects.filter(id__in=images_to_delete, property=property).delete()
            
            messages.success(request, _('La propriété a été modifiée avec succès.'))
            return redirect('dashboard:property_management')
        else:
            messages.error(request, _('Veuillez corriger les erreurs ci-dessous.'))
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'dashboard/edit_property.html', {
        'form': form,
        'property': property,
        'additional_images': property.images.all()
    })

@login_required
@user_passes_test(is_superuser)
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        property.delete()
        messages.success(request, _('La propriété a été supprimée avec succès.'))
        return redirect('dashboard:property_management')
    
    return render(request, 'dashboard/delete_property.html', {'property': property})

@login_required
@user_passes_test(is_superuser)
def analytics(request):
    # Time period filter
    period = request.GET.get('period', '30')
    days = int(period)
    start_date = timezone.now() - timedelta(days=days)
    
    # Properties with view counts
    properties_analytics = Property.objects.annotate(
        view_count=Count('views', filter=Q(views__timestamp__gte=start_date))
    ).order_by('-view_count')[:20]
    
    # Views by day
    daily_views = PropertyView.objects.filter(
        timestamp__gte=start_date
    ).annotate(
        day=TruncDate('timestamp')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Property types performance
    type_performance = Property.objects.values('property_type').annotate(
        view_count=Count('views', filter=Q(views__timestamp__gte=start_date)),
        property_count=Count('id')
    ).order_by('-view_count')
    
    # City performance
    city_performance = Property.objects.values('city').annotate(
        view_count=Count('views', filter=Q(views__timestamp__gte=start_date)),
        property_count=Count('id')
    ).order_by('-view_count')[:10]
    
    # Prepare chart data
    daily_chart = {
        'labels': [view['day'].strftime('%d/%m') for view in daily_views],
        'data': [view['count'] for view in daily_views]
    }
    
    # Convert property type labels to strings before JSON serialization
    type_chart = {
        'labels': [str(dict(Property.PROPERTY_TYPES).get(tp['property_type'], tp['property_type'])) 
                  for tp in type_performance],
        'data': [tp['view_count'] for tp in type_performance]
    }
    
    city_chart = {
        'labels': [str(city['city']) for city in city_performance],
        'data': [city['view_count'] for city in city_performance]
    }
    
    # Convert QuerySet to list for template
    properties_list = [{
        'id': prop.id,
        'title': str(prop.title),
        'type': str(prop.get_property_type_display()),
        'city': str(prop.city),
        'price': float(prop.price),
        'view_count': prop.view_count,
        'available': prop.available,
        'featured': prop.featured,
    } for prop in properties_analytics]
    
    type_performance_list = [{
        'type': str(dict(Property.PROPERTY_TYPES).get(tp['property_type'], tp['property_type'])),
        'view_count': tp['view_count'],
        'property_count': tp['property_count']
    } for tp in type_performance]
    
    city_performance_list = [{
        'city': str(cp['city']),
        'view_count': cp['view_count'],
        'property_count': cp['property_count']
    } for cp in city_performance]
    
    context = {
        'properties_analytics': properties_list,
        'daily_chart': json.dumps(daily_chart),
        'type_chart': json.dumps(type_chart),
        'city_chart': json.dumps(city_chart),
        'type_performance': type_performance_list,
        'city_performance': city_performance_list,
        'period': period,
        'total_views': PropertyView.objects.filter(timestamp__gte=start_date).count(),
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
@user_passes_test(is_superuser)
def contact_management(request):
    if not request.user.is_superuser:
        return redirect('dashboard:login')
    
    contacts = ContactSubmission.objects.all().order_by('-timestamp')
    
    # Mark as read functionality
    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        action = request.POST.get('action')
        
        if contact_id and action:
            contact = get_object_or_404(ContactSubmission, id=contact_id)
            if action == 'mark_read':
                contact.is_read = True
                contact.save()
                messages.success(request, _('Contact marqué comme lu.'))
            elif action == 'mark_unread':
                contact.is_read = False
                contact.save()
                messages.success(request, _('Contact marqué comme non lu.'))
    
    # Pagination
    paginator = Paginator(contacts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': ContactSubmission.objects.filter(is_read=False).count(),
    }
    
    return render(request, 'dashboard/contact_management.html', context)

@login_required
@user_passes_test(is_superuser)
def website_settings(request):
    if not request.user.is_superuser:
        return redirect('dashboard:login')
    
    settings_obj, created = WebsiteSettings.objects.get_or_create(
        defaults={
            'site_name': 'ImmoLux',
            'contact_email': 'contact@immolux.ma',
            'contact_phone': '+212 5 22 xx xx xx',
            'contact_address': '123 Avenue Hassan II, Casablanca'
        }
    )
    
    if request.method == 'POST':
        form = WebsiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, _('Paramètres mis à jour avec succès!'))
            return redirect('dashboard:website_settings')
    else:
        form = WebsiteSettingsForm(instance=settings_obj)
    
    return render(request, 'dashboard/website_settings.html', {'form': form})

@login_required
@user_passes_test(is_superuser)
def user_profile(request):
    profile, created = DashboardUser.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profil mis à jour avec succès!'))
            return redirect('dashboard:user_profile')
    else:
        form = UserProfileForm(instance=request.user, profile=profile)
    
    return render(request, 'dashboard/user_profile.html', {'form': form})

# API endpoints for AJAX requests
@login_required
def api_property_stats(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    property_id = request.GET.get('property_id')
    if property_id:
        property = get_object_or_404(Property, id=property_id)
        views_count = property.views.count()
        contacts_count = ContactSubmission.objects.filter(property=property).count()
        
        return JsonResponse({
            'views': views_count,
            'contacts': contacts_count,
            'title': property.title
        })
    
    return JsonResponse({'error': 'Property ID required'}, status=400)

@login_required
def api_toggle_featured(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        property = get_object_or_404(Property, id=property_id)
        property.featured = not property.featured
        property.save()
        
        return JsonResponse({
            'success': True,
            'featured': property.featured
        })
    
    return JsonResponse({'error': 'POST required'}, status=400)

@login_required
def api_toggle_availability(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        property = get_object_or_404(Property, id=property_id)
        property.available = not property.available
        property.save()
        
        return JsonResponse({
            'success': True,
            'available': property.available
        })
    
    return JsonResponse({'error': 'POST required'}, status=400)

@login_required
def mark_contact_read(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'success': False})
    
    contact = get_object_or_404(ContactSubmission, pk=pk)
    contact.is_read = True
    contact.save()
    
    # Check if request is AJAX (modern way)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        messages.success(request, _('Contact marqué comme lu.'))
        return redirect('dashboard:contact_management')

@login_required
def delete_contact(request, pk):
    if not request.user.is_superuser:
        return redirect('dashboard:login')
    
    contact = get_object_or_404(ContactSubmission, pk=pk)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, _('Contact supprimé avec succès!'))
        return redirect('dashboard:contact_management')
    
    return redirect('dashboard:contact_management')

@login_required
def change_password(request):
    if not request.user.is_superuser:
        return redirect('dashboard:login')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, _('Ancien mot de passe incorrect.'))
        elif new_password1 != new_password2:
            messages.error(request, _('Les nouveaux mots de passe ne correspondent pas.'))
        else:
            request.user.set_password(new_password1)
            request.user.save()
            messages.success(request, _('Mot de passe modifié avec succès!'))
            return redirect('dashboard:login')
    
    return redirect('dashboard:user_profile')
