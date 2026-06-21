import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.base")
django.setup()

from django.test import RequestFactory
from products.views import ProductViewSet
from products.models import Product, Collection
from rest_framework.test import force_authenticate
from users.models import User
import json

factory = RequestFactory()
col, _ = Collection.objects.get_or_create(name="Test Collection", slug="test-collection")
user, _ = User.objects.get_or_create(email='admin@test.com', is_staff=True, is_superuser=True)

data = {
    'name': 'API Test Product 3',
    'description': 'Desc',
    'price': '10.00',
    'status': 'DRAFT',
    'collections': ['test-collection', col.id]  
}

request = factory.post('/api/v1/products/', data=data, content_type='application/json')
force_authenticate(request, user=user)

view = ProductViewSet.as_view({'post': 'create'})
response = view(request)
print("Status:", response.status_code)
if response.status_code == 201:
    prod = Product.objects.get(id=response.data['id'])
    print("Collections assigned:")
    for c in prod.collections.all():
        print("- ", c.name)
else:
    print(response.data)
