from django.db import models

class Wilaya(models.Model):
    code = models.CharField(max_length=2, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    home_delivery_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    bureau_delivery_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    delivery_days = models.CharField(max_length=50, default="2-4 days")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class StoreSettings(models.Model):
    # Singleton Model
    store_name = models.CharField(max_length=100, default="Old Money Algeria")
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    tiktok_url = models.URLField(blank=True, null=True)
    meta_pixel_id = models.CharField(max_length=50, blank=True, null=True)
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    free_delivery_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount above which delivery is free.")

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        if not self.pk and StoreSettings.objects.exists():
            # if you'll not check for self.pk 
            # then error will also raised in update of exists model
            raise Exception('StoreSettings can only have one instance.')
        super().save(*args, **kwargs)

class HomepageContent(models.Model):
    # Singleton Model
    hero_title = models.CharField(max_length=255, blank=True, null=True)
    hero_subtitle = models.TextField(blank=True, null=True)
    hero_image_url = models.URLField(max_length=1000, blank=True, null=True)
    hero_button_text = models.CharField(max_length=50, blank=True, null=True)
    hero_button_link = models.CharField(max_length=255, blank=True, null=True)

    # Could be extended with many-to-many or JSON fields for multiple sliders/promos,
    # but keeping it simple for the singleton.
    promotional_banner_text = models.CharField(max_length=255, blank=True, null=True)
    promotional_banner_active = models.BooleanField(default=False)

    collections_hero_title = models.CharField(max_length=255, blank=True, null=True)
    collections_hero_image_url = models.URLField(max_length=1000, blank=True, null=True)

    ICON_CHOICES = [
        ('CROWN', 'Crown'),
        ('TRUCK', 'Truck'),
        ('DIAMOND', 'Diamond'),
    ]
    prop1_icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='CROWN')
    prop1_title = models.CharField(max_length=255, default='Qualité Premium')
    prop1_text = models.TextField(default="Des matières nobles sélectionnées pour durer et affirmer votre statut.")
    
    prop2_icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='TRUCK')
    prop2_title = models.CharField(max_length=255, default='Livraison 58 Wilayas')
    prop2_text = models.TextField(default="Payez en espèces à la livraison. Nous expédions partout en Algérie.")
    
    prop3_icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='DIAMOND')
    prop3_title = models.CharField(max_length=255, default='Élégance Intemporelle')
    prop3_text = models.TextField(default="Des coupes minimalistes inspirées par l'esthétique Old Money.")

    class Meta:
        verbose_name = "Homepage Content"
        verbose_name_plural = "Homepage Content"

    def __str__(self):
        return "Homepage Content Configuration"
        
    def save(self, *args, **kwargs):
        if not self.pk and HomepageContent.objects.exists():
            raise Exception('HomepageContent can only have one instance.')
        super().save(*args, **kwargs)

class HomepageSection(models.Model):
    SECTION_TYPES = [
        ('NOUVEAUTES', 'Nouveautés'),
        ('BESTSELLERS', 'Bestsellers'),
        ('RECOMMANDATIONS', 'Recommandations'),
        ('CUSTOM', 'Custom'),
    ]
    title = models.CharField(max_length=255)
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES, default='CUSTOM')
    products = models.ManyToManyField('products.Product', blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title
