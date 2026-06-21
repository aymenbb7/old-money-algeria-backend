import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.base")
django.setup()

from django.test import RequestFactory
from products.views import ProductViewSet
from products.models import Product, Collection
from rest_framework.test import force_authenticate
from users.models import User

factory = RequestFactory()
col, _ = Collection.objects.get_or_create(name="Test Collection", slug="test-collection")
user, _ = User.objects.get_or_create(email='admin@test.com', is_staff=True, is_superuser=True)

data = {
    'name': 'API Test Product 4',
    'description': 'Desc',
    'price': '10.00',
    'status': 'DRAFT',
    'collections': ['test-collection', col.id],
    'variants': json.dumps([{"size": "M", "color": "Black", "stock": 10}])
}

request = factory.post('/api/v1/products/', data=data)
force_authenticate(request, user=user)

view = ProductViewSet.as_view({'post': 'create'})
try:
    response = view(request)
    print("Status:", response.status_code)
    if response.status_code == 201:
        prod = Product.objects.get(id=response.data['id'])
        print("Success! Variants count:", prod.variants.count())
    else:
        print("Error Response:", response.data)
except Exception as e:
    print("Exception during view execution:", e)
