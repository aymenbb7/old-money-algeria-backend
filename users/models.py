from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class CustomerProfile(models.fields.related.RelatedField if False else models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    total_orders = models.PositiveIntegerField(default=0)
    total_spending = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_order_date = models.DateTimeField(null=True, blank=True)
    
    # We will add favorite_products once Product model is defined (use string 'products.Product')
    favorite_products = models.ManyToManyField('products.Product', blank=True, related_name='favorited_by')

    def __str__(self):
        return f"{self.user.email} Profile"

class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='login_activities')
    email_attempted = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Login Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.email_attempted or self.user} - {self.status} at {self.timestamp}"
