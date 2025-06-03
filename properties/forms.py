from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.utils.translation import gettext_lazy as _
from .models import Contact, Property, PropertyImage, PropertyInquiry

class PropertySearchForm(forms.Form):
    city = forms.CharField(
        label=_('Ville'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Entrez une ville')})
    )
    property_type = forms.ChoiceField(
        label=_('Type de bien'),
        choices=[('', _('Tous les types'))] + Property.PROPERTY_TYPES,
        required=False
    )
    min_price = forms.DecimalField(
        label=_('Prix minimum'),
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': _('Prix minimum')})
    )
    max_price = forms.DecimalField(
        label=_('Prix maximum'),
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': _('Prix maximum')})
    )
    bedrooms = forms.IntegerField(
        label=_('Nombre de chambres'),
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': _('Nombre de chambres')})
    )

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': _('Votre message')
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.user = user
        
        if user and user.is_authenticated:
            self.helper.layout = Layout(
                'message',
                Submit('submit', _('Envoyer le message'), css_class='btn btn-success w-100')
            )
        else:
            self.helper.layout = Layout(
                'message',
                Row(
                    Column(
                        Submit('submit', _('Se connecter pour envoyer'), css_class='btn btn-primary w-100'),
                        css_class='col-12'
                    )
                )
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            instance.name = self.user.get_full_name()
            instance.email = self.user.email
            if hasattr(self.user, 'profile') and self.user.profile.phone:
                instance.phone = self.user.profile.phone
        if commit:
            instance.save()
        return instance

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
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-6 mb-3'),
                Column('description', css_class='form-group col-md-6 mb-3'),
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
            ),
            Row(
                Column('featured', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', _('Enregistrer'), css_class='btn btn-success')
        )

    def save(self, commit=True):
        property = super().save(commit=commit)
        
        # Handle additional images
        if self.cleaned_data.get('additional_images'):
            for image in self.cleaned_data['additional_images']:
                PropertyImage.objects.create(
                    property=property,
                    image=image
                )
        
        return property

class PropertyInquiryForm(forms.ModelForm):
    class Meta:
        model = PropertyInquiry
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your email')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your phone number')
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Your message')
            })
        }