# Generated by Django 5.2 on 2025-06-01 22:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_alter_propertyimage_options_propertyimage_created_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['-created_at'], 'verbose_name': 'Property', 'verbose_name_plural': 'Properties'},
        ),
        migrations.RemoveField(
            model_name='property',
            name='rooms',
        ),
        migrations.AddField(
            model_name='property',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='properties', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='property',
            name='bedrooms',
            field=models.IntegerField(blank=True, null=True, verbose_name='Bedrooms'),
        ),
        migrations.AddField(
            model_name='property',
            name='listing_type',
            field=models.CharField(choices=[('sale', 'For Sale'), ('rent', 'For Rent')], default='sale', max_length=20, verbose_name='Listing Type'),
        ),
        migrations.AddField(
            model_name='property',
            name='location',
            field=models.CharField(default='Not specified', max_length=200, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='property',
            name='total_views',
            field=models.PositiveIntegerField(default=0, verbose_name='Total Views'),
        ),
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='property',
            name='bathrooms',
            field=models.IntegerField(blank=True, null=True, verbose_name='Bathrooms'),
        ),
        migrations.AlterField(
            model_name='property',
            name='city',
            field=models.CharField(max_length=100, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='property',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='property',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='Featured'),
        ),
        migrations.AlterField(
            model_name='property',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='properties/', verbose_name='Main Image'),
        ),
        migrations.AlterField(
            model_name='property',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(choices=[('house', 'House'), ('apartment', 'Apartment'), ('villa', 'Villa'), ('office', 'Office'), ('land', 'Land')], default='house', max_length=20, verbose_name='Property Type'),
        ),
        migrations.AlterField(
            model_name='property',
            name='size',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Size (m²)'),
        ),
        migrations.AlterField(
            model_name='property',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='property',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.CreateModel(
            name='PropertyInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone')),
                ('message', models.TextField(verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to='properties.property')),
            ],
            options={
                'verbose_name': 'Property Inquiry',
                'verbose_name_plural': 'Property Inquiries',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PropertyView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_viewed', models.DateTimeField(auto_now_add=True, verbose_name='First Viewed')),
                ('last_viewed', models.DateTimeField(auto_now=True, verbose_name='Last Viewed')),
                ('view_count', models.PositiveIntegerField(default=1, verbose_name='View Count')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='property_views', to='properties.property')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Property View',
                'verbose_name_plural': 'Property Views',
                'unique_together': {('property', 'user')},
            },
        ),
        migrations.AddField(
            model_name='property',
            name='viewed_by',
            field=models.ManyToManyField(related_name='viewed_properties', through='properties.PropertyView', to=settings.AUTH_USER_MODEL, verbose_name='Viewed By'),
        ),
    ]
