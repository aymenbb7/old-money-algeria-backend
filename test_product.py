import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.base')
django.setup()

from products.models import Product, ProductVariant, Collection

try:
    c, _ = Collection.objects.get_or_create(name="Summer Collection", slug="summer-col")
    
    p = Product.objects.create(
        name="Test Product 2",
        slug="test-product-2",
        description="A test product",
        price=1500.00,
        status="PUBLISHED"
    )
    
    # Test our new view logic by manually calling what the view does
    c_val = "summer-col"
    from django.db.models import Q
    col = Collection.objects.filter(Q(slug=c_val) | Q(name__iexact=c_val)).first()
    if col:
        p.collections.add(col.id)
        
    v = ProductVariant.objects.create(
        product=p,
        size="M",
        color="Black",
        stock=10
    )
    print("Product created successfully with collection:", p.collections.first().name)
except Exception as e:
    print(f"Error creating product: {e}")
