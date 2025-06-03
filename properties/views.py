# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Property, Contact, PropertyView
from .forms import PropertySearchForm, ContactForm, PropertyInquiryForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from dashboard.models import ContactSubmission

def home(request):
    featured_properties = Property.objects.filter(featured=True, available=True)[:6]
    total_properties = Property.objects.filter(available=True).count()
    
    # Stats (you can make these dynamic)
    stats = {
        'properties_sold': 150,
        'satisfied_clients': 200,
        'years_experience': 15,
        'total_properties': total_properties,
    }
    
    context = {
        'featured_properties': featured_properties,
        'stats': stats,
        'search_form': PropertySearchForm(),
    }
    return render(request, 'home.html', context)

def property_list(request):
    properties = Property.objects.all()
    search_form = PropertySearchForm(request.GET)
    
    if search_form.is_valid():
        city = search_form.cleaned_data.get('city')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        
        if city:
            properties = properties.filter(city__icontains=city)
        if property_type:
            properties = properties.filter(property_type=property_type)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        if bedrooms:
            properties = properties.filter(bedrooms=bedrooms)
    
    paginator = Paginator(properties, 9)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    # Create a query dict without the page parameter
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'property_types': Property.PROPERTY_TYPES,
        'query_string': query_dict.urlencode()
    }
    return render(request, 'properties/property_list.html', context)

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    # Track the view
    property.increment_views(request.user)
    
    # Get similar properties
    similar_properties = Property.objects.filter(
        Q(property_type=property.property_type) | 
        Q(city=property.city)
    ).exclude(id=property.id)[:3]
    
    if request.method == 'POST':
        inquiry_form = PropertyInquiryForm(request.POST)
        if inquiry_form.is_valid():
            inquiry = inquiry_form.save(commit=False)
            inquiry.property = property
            inquiry.save()
            messages.success(request, _('Your inquiry has been sent successfully.'))
            return redirect('properties:property_detail', pk=pk)
    else:
        inquiry_form = PropertyInquiryForm()
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
        'inquiry_form': inquiry_form,
    }
    return render(request, 'properties/property_detail.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, _('Veuillez vous connecter pour envoyer un message.'))
            return redirect('accounts:login')
        
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.name = request.user.get_full_name()
            contact.email = request.user.email
            contact.save()
            
            # Also save to dashboard model
            ContactSubmission.objects.create(
                name=contact.name,
                email=contact.email,
                phone=contact.phone,
                message=contact.message
            )
            
            messages.success(request, _('Votre message a été envoyé avec succès!'))
            return redirect('contact')
    else:
        form = ContactForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'contact.html', context)

def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        property_id = request.POST.get('property_id')
        
        try:
            property = Property.objects.get(id=property_id) if property_id else None
            Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message,
                property=property
            )
            messages.success(request, _('Votre message a été envoyé avec succès.'))
            return JsonResponse({'status': 'success'})
        except Exception as e:
            messages.error(request, _('Une erreur est survenue. Veuillez réessayer.'))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': _('Méthode non autorisée')}, status=405)

@login_required
def contact_property(request, pk):
    property = get_object_or_404(Property, id=pk)
    
    if request.method == 'POST':
        name = request.user.get_full_name() or request.user.username
        email = request.user.email
        phone_number = request.user.profile.phone_number if hasattr(request.user, 'profile') else None
        message = request.POST.get('message')
        
        contact = ContactSubmission.objects.create(
            property=property,
            name=name,
            email=email,
            phone_number=phone_number,
            message=message
        )
        
        messages.success(request, _('Your message has been sent successfully!'))
        return redirect('properties:property_detail', pk=pk)
    
    return redirect('properties:property_detail', pk=pk)

@login_required
def my_properties(request):
    properties = Property.objects.filter(agent=request.user)
    viewed_properties = PropertyView.objects.filter(user=request.user).select_related('property')
    
    context = {
        'properties': properties,
        'viewed_properties': viewed_properties,
    }
    return render(request, 'properties/my_properties.html', context) 