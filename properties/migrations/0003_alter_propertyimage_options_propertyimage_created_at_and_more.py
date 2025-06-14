# Generated by Django 5.2 on 2025-06-01 18:56

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0002_alter_contact_options_remove_contact_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='propertyimage',
            options={'ordering': ['order', 'created_at'], 'verbose_name': 'Image de propriété', 'verbose_name_plural': 'Images de propriétés'},
        ),
        migrations.AddField(
            model_name='propertyimage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date de création'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='propertyimage',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Ordre'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='alt_text',
            field=models.CharField(blank=True, max_length=255, verbose_name='Texte alternatif'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='image',
            field=models.ImageField(upload_to='properties/images/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.property', verbose_name='Propriété'),
        ),
    ]
