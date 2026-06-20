from django.db import models
from django.utils.crypto import get_random_string

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiration_date = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
    )

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Guest / Customer Info
    guest_name = models.CharField(max_length=255)
    guest_phone = models.CharField(max_length=20)
    guest_email = models.EmailField(blank=True, null=True)
    
    # Delivery Info
    wilaya = models.ForeignKey('core.Wilaya', on_delete=models.RESTRICT)
    commune = models.CharField(max_length=150)
    address = models.TextField()
    is_home_delivery = models.BooleanField(default=True)
    delivery_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Order Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Notes & Tracking
    internal_notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery_company = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = "OMA-" + get_random_string(8).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True)
    
    # Snapshots at time of order
    product_name = models.CharField(max_length=200)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.order.order_number})"
