import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from products.models import Product, ProductVariant, ProductImage

# Clean up
Product.objects.all().delete()

# Create product
p = Product.objects.create(
    name="Test API Product",
    slug="test-api-product",
    description="Full description",
    price="2500.00",
    status="PUBLISHED"
)

# Add variants exactly as requested
ProductVariant.objects.create(product=p, size="M", color="Noir", stock=10)
ProductVariant.objects.create(product=p, size="M", color="Vert", stock=10)
ProductVariant.objects.create(product=p, size="S", color="Red", stock=10)

# Mock a Cloudinary image by setting the database string manually
pi = ProductImage(product=p, is_main=True)
pi.image = "image/upload/v1234567/products/dummy_hjlkas.jpg"
pi.save()

print("Mock product inserted successfully.")
