import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.base')
django.setup()

from products.models import Product, ProductVariant

try:
    p = Product.objects.create(
        name="Test Product",
        slug="test-product",
        description="A test product",
        price=1500.00,
        sku="TEST-001",
        status="PUBLISHED"
    )
    v = ProductVariant.objects.create(
        product=p,
        size="M",
        color="Black",
        stock=10
    )
    print("Product created successfully.")
except Exception as e:
    print(f"Error creating product: {e}")
