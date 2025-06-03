from django.contrib import admin
from .models import PropertyView, ContactSubmission, WebsiteSettings, DashboardUser

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ('property', 'ip_address', 'timestamp')
    list_filter = ('timestamp', 'property__city')
    readonly_fields = ('timestamp',)

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'property', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not WebsiteSettings.objects.exists()

@admin.register(DashboardUser)
class DashboardUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'department', 'last_login_ip')