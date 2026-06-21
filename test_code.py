from products.models import Product, ProductImage
import json

with open("dummy.jpg", "wb") as f:
    f.write(b"this is a dummy image for testing")

p = Product.objects.create(name="Test Cloud", slug="test-cloud", description="t", price=10)

from django.core.files import File
with open("dummy.jpg", "rb") as f:
    pi = ProductImage.objects.create(product=p, is_main=True, image=File(f))

print("Created ProductImage URL:", pi.image.url)

from products.serializers import ProductSerializer
print(ProductSerializer(p).data['images'])

import os
os.remove("dummy.jpg")
