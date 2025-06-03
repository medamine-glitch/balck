from django.contrib import admin
from .models import Property, PropertyImage, Contact

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'alt_text', 'order')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'city', 'price', 'available', 'featured')
    list_filter = ('property_type', 'city', 'available', 'featured')
    search_fields = ('title', 'description', 'address', 'city')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    list_editable = ('featured', 'available')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'alt_text', 'order', 'created_at')
    list_filter = ('property', 'created_at')
    search_fields = ('property__title', 'alt_text')
    ordering = ('property', 'order', 'created_at')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property', 'timestamp')
    list_filter = ('timestamp', 'is_read')
    readonly_fields = ('timestamp',)
    search_fields = ('name', 'email')