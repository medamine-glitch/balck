from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from django.utils.translation import gettext_lazy as _

from properties.models import Property, PropertyImage
from .models import WebsiteSettings, DashboardUser

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PropertyForm(forms.ModelForm):
    additional_images = MultipleFileField(
        required=False,
        label=_('Additional Images'),
        help_text=_('You can select multiple images at once')
    )

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'listing_type',
            'price', 'bedrooms', 'bathrooms', 'size', 'location',
            'city', 'address', 'image', 'featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'listing_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('property_type', css_class='form-group col-md-4 mb-3'),
                Column('listing_type', css_class='form-group col-md-4 mb-3'),
                Column('price', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('bedrooms', css_class='form-group col-md-4 mb-3'),
                Column('bathrooms', css_class='form-group col-md-4 mb-3'),
                Column('size', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('location', css_class='form-group col-md-6 mb-3'),
                Column('city', css_class='form-group col-md-6 mb-3'),
            ),
            'address',
            Row(
                Column('image', css_class='form-group col-md-6 mb-3'),
                Column('additional_images', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('featured', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', _('Save'), css_class='btn btn-success')
        )

    def save(self, commit=True):
        property = super().save(commit=commit)
        
        if commit:
            # Handle additional images
            if self.cleaned_data.get('additional_images'):
                for image in self.cleaned_data['additional_images']:
                    PropertyImage.objects.create(
                        property=property,
                        image=image
                    )
        
        return property

class WebsiteSettingsForm(forms.ModelForm):
    class Meta:
        model = WebsiteSettings
        fields = '__all__'
        widgets = {
            'site_description': forms.Textarea(attrs={'rows': 4}),
            'contact_address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('site_name', css_class='form-group col-md-6 mb-3'),
                Column('maintenance_mode', css_class='form-group col-md-6 mb-3'),
            ),
            'site_description',
            Row(
                Column('contact_email', css_class='form-group col-md-6 mb-3'),
                Column('contact_phone', css_class='form-group col-md-6 mb-3'),
            ),
            'contact_address',
            Row(
                Column('facebook_url', css_class='form-group col-md-6 mb-3'),
                Column('instagram_url', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('linkedin_url', css_class='form-group col-md-6 mb-3'),
                Column('youtube_url', css_class='form-group col-md-6 mb-3'),
            ),
            'google_analytics_id',
            Submit('submit', _('Mettre à jour'), css_class='btn btn-success')
        )

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label=_('Prénom'))
    last_name = forms.CharField(max_length=30, required=False, label=_('Nom'))
    email = forms.EmailField(required=True, label=_('Email'))

    class Meta:
        model = DashboardUser
        fields = ['avatar', 'phone', 'department']

    def __init__(self, *args, instance=None, profile=None, **kwargs):
        self.profile = profile
        if instance:
            kwargs['initial'] = {
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email
            }
        super().__init__(*args, instance=profile, **kwargs)

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile