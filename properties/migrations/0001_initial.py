from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('title_ar', models.CharField(blank=True, max_length=200, verbose_name='Titre (Arabe)')),
                ('description', models.TextField(verbose_name='Description')),
                ('description_ar', models.TextField(blank=True, verbose_name='Description (Arabe)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Prix')),
                ('property_type', models.CharField(choices=[('villa', 'Villa'), ('apartment', 'Appartement'), ('office', 'Bureau'), ('land', 'Terrain'), ('commercial', 'Commercial')], max_length=20, verbose_name='Type')),
                ('size', models.PositiveIntegerField(verbose_name='Superficie (m²)')),
                ('rooms', models.PositiveIntegerField(default=1, verbose_name='Nombre de chambres')),
                ('bathrooms', models.PositiveIntegerField(default=1, verbose_name='Salles de bain')),
                ('city', models.CharField(max_length=100, verbose_name='Ville')),
                ('address', models.CharField(max_length=300, verbose_name='Adresse')),
                ('image', models.ImageField(blank=True, upload_to='properties/', verbose_name='Image principale')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='Slug')),
                ('featured', models.BooleanField(default=False, verbose_name='Propriété vedette')),
                ('available', models.BooleanField(default=True, verbose_name='Disponible')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
            ],
            options={
                'verbose_name': 'Propriété',
                'verbose_name_plural': 'Propriétés',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='properties/', verbose_name='Image')),
                ('alt_text', models.CharField(blank=True, max_length=200, verbose_name='Texte alternatif')),
                ('property', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='images', to='properties.property')),
            ],
            options={
                'verbose_name': 'Image de propriété',
                'verbose_name_plural': 'Images de propriétés',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('message', models.TextField(verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='properties.property')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ['-created_at'],
            },
        ),
    ] 