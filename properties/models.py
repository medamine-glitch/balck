from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', _('House')),
        ('apartment', _('Apartment')),
        ('villa', _('Villa')),
        ('office', _('Office')),
        ('land', _('Land')),
    ]
    
    LISTING_TYPES = [
        ('sale', _('For Sale')),
        ('rent', _('For Rent')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    title_ar = models.CharField(_('Titre (Arabe)'), max_length=200, blank=True)
    description = models.TextField(_('Description'))
    description_ar = models.TextField(_('Description (Arabe)'), blank=True)
    price = models.DecimalField(_('Price'), max_digits=12, decimal_places=2)
    property_type = models.CharField(_('Property Type'), max_length=20, choices=PROPERTY_TYPES, default='house')
    listing_type = models.CharField(_('Listing Type'), max_length=20, choices=LISTING_TYPES, default='sale')
    size = models.DecimalField(_('Size (m²)'), max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(_('Bedrooms'), null=True, blank=True)
    bathrooms = models.IntegerField(_('Bathrooms'), null=True, blank=True)
    location = models.CharField(_('Location'), max_length=200, default='Not specified')
    city = models.CharField(_('City'), max_length=100)
    address = models.CharField(_('Address'), max_length=255)
    image = models.ImageField(_('Main Image'), upload_to='properties/', null=True, blank=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    featured = models.BooleanField(_('Featured'), default=False)
    available = models.BooleanField(_('Disponible'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='properties', null=True, blank=True)
    
    # View tracking fields
    total_views = models.PositiveIntegerField(_('Total Views'), default=0)
    viewed_by = models.ManyToManyField(
        User,
        through='PropertyView',
        related_name='viewed_properties',
        verbose_name=_('Viewed By')
    )

    class Meta:
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('properties:property_detail', args=[str(self.id)])

    def increment_views(self, user=None):
        """Increment the view count and record the viewer if authenticated"""
        self.total_views += 1
        self.save()
        
        if user and user.is_authenticated:
            view, created = PropertyView.objects.get_or_create(
                property=self,
                user=user,
                defaults={'last_viewed': timezone.now()}
            )
            if not created:
                view.view_count += 1
                view.last_viewed = timezone.now()
                view.save()

class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Propriété')
    )
    image = models.ImageField(
        upload_to='properties/images/',
        verbose_name=_('Image')
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Texte alternatif')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ordre')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date de création')
    )

    class Meta:
        verbose_name = _('Image de propriété')
        verbose_name_plural = _('Images de propriétés')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.property.title}"

class Contact(models.Model):
    name = models.CharField(_('Nom'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Téléphone'), max_length=20, blank=True)
    message = models.TextField(_('Message'))
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts',
        verbose_name=_('Propriété')
    )
    timestamp = models.DateTimeField(_('Date'), default=timezone.now)
    is_read = models.BooleanField(_('Lu'), default=False)
    
    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.name} - {self.email}"

class PropertyView(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_viewed = models.DateTimeField(_('First Viewed'), auto_now_add=True)
    last_viewed = models.DateTimeField(_('Last Viewed'), auto_now=True)
    view_count = models.PositiveIntegerField(_('View Count'), default=1)

    class Meta:
        unique_together = ['property', 'user']
        verbose_name = _('Property View')
        verbose_name_plural = _('Property Views')

    def __str__(self):
        return f"{self.user.username} viewed {self.property.title}"

class PropertyInquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Property Inquiry')
        verbose_name_plural = _('Property Inquiries')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry from {self.name} for {self.property.title}"