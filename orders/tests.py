from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Wilaya
from products.models import Product, ProductVariant
from orders.models import Order, Coupon

class CheckoutAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Setup Wilaya
        self.wilaya_active = Wilaya.objects.create(code="16", name="Alger", home_delivery_price=600, is_active=True)
        self.wilaya_inactive = Wilaya.objects.create(code="09", name="Blida", home_delivery_price=500, is_active=False)
        
        # Setup Product & Variant
        self.product = Product.objects.create(name="Test Shirt", price=5000, sku="TS-001")
        self.variant = ProductVariant.objects.create(product=self.product, size="M", stock=10)
        
        # Setup Coupons
        self.coupon_fixed = Coupon.objects.create(
            code="FIXED1000", discount_type="FIXED", value=1000, min_order_amount=2000, is_active=True
        )
        self.coupon_perc = Coupon.objects.create(
            code="PERC10", discount_type="PERCENTAGE", value=10, min_order_amount=2000, is_active=True
        )
        self.coupon_expired = Coupon.objects.create(
            code="EXPIRED", discount_type="FIXED", value=500, 
            expiration_date=timezone.now() - timedelta(days=1), is_active=True
        )

    def test_guest_checkout_success(self):
        payload = {
            "guest_name": "John Doe",
            "guest_phone": "0555555555",
            "wilaya_code": "16",
            "is_home_delivery": True,
            "items": [{"variant_id": self.variant.id, "quantity": 2}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_number", res.data)
        
        # Check totals (2 * 5000) + 600 delivery = 10600
        self.assertEqual(float(res.data['total_amount']), 10600.0)

    def test_coupon_percentage_applied(self):
        payload = {
            "guest_name": "John",
            "guest_phone": "0555",
            "wilaya_code": "16",
            "coupon_code": "PERC10",
            "items": [{"variant_id": self.variant.id, "quantity": 1}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Subtotal: 5000. 10% off = 500 discount. Total = 4500 + 600 = 5100.
        self.assertEqual(float(res.data['total_amount']), 5100.0)

    def test_coupon_fixed_applied(self):
        payload = {
            "guest_name": "John",
            "guest_phone": "0555",
            "wilaya_code": "16",
            "coupon_code": "FIXED1000",
            "items": [{"variant_id": self.variant.id, "quantity": 1}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Subtotal: 5000. 1000 off = 4000. Total = 4000 + 600 = 4600.
        self.assertEqual(float(res.data['total_amount']), 4600.0)

    def test_coupon_expired_rejected(self):
        payload = {
            "guest_name": "John",
            "guest_phone": "0555",
            "wilaya_code": "16",
            "coupon_code": "EXPIRED",
            "items": [{"variant_id": self.variant.id, "quantity": 1}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['error'], 'Coupon expired')

    def test_variant_stock_decreases(self):
        initial_stock = self.variant.stock
        payload = {
            "guest_name": "John",
            "guest_phone": "0555",
            "wilaya_code": "16",
            "items": [{"variant_id": self.variant.id, "quantity": 3}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, initial_stock - 3)

    def test_inactive_wilaya_rejected(self):
        payload = {
            "guest_name": "John",
            "guest_phone": "0555",
            "wilaya_code": "09", # Blida is inactive
            "items": [{"variant_id": self.variant.id, "quantity": 1}]
        }
        res = self.client.post('/api/v1/orders/checkout/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['error'], 'Delivery to this wilaya is currently disabled.')
