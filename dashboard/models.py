from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class PropertyView(models.Model):
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('Propriété')
    )
    ip_address = models.GenericIPAddressField(_('Adresse IP'))
    user_agent = models.CharField(_('User Agent'), max_length=255, blank=True)
    session_key = models.CharField(_('Clé de session'), max_length=40, blank=True)
    timestamp = models.DateTimeField(_('Date'), default=timezone.now)

    class Meta:
        verbose_name = _('Vue de propriété')
        verbose_name_plural = _('Vues de propriétés')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.property.title} - {self.timestamp}"

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    property = models.ForeignKey('properties.Property', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class WebsiteSettings(models.Model):
    site_name = models.CharField(_('Nom du site'), max_length=100)
    site_description = models.TextField(_('Description du site'), blank=True)
    maintenance_mode = models.BooleanField(_('Mode maintenance'), default=False)
    contact_email = models.EmailField(_('Email de contact'))
    contact_phone = models.CharField(_('Téléphone de contact'), max_length=20)
    contact_address = models.TextField(_('Adresse de contact'))
    facebook_url = models.URLField(_('URL Facebook'), blank=True)
    instagram_url = models.URLField(_('URL Instagram'), blank=True)
    linkedin_url = models.URLField(_('URL LinkedIn'), blank=True)
    youtube_url = models.URLField(_('URL YouTube'), blank=True)
    google_analytics_id = models.CharField(
        _('ID Google Analytics'),
        max_length=50,
        blank=True
    )

    class Meta:
        verbose_name = _('Paramètres du site')
        verbose_name_plural = _('Paramètres du site')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and WebsiteSettings.objects.exists():
            return WebsiteSettings.objects.first()
        return super().save(*args, **kwargs)

class DashboardUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Utilisateur')
    )
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    phone = models.CharField(_('Téléphone'), max_length=20, blank=True)
    department = models.CharField(_('Département'), max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(
        _('Dernière IP de connexion'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Utilisateur dashboard')
        verbose_name_plural = _('Utilisateurs dashboard')

    def __str__(self):
        return self.user.get_full_name() or self.user.username