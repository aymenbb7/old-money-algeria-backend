import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.base")
django.setup()

from django.test import RequestFactory
from core.views import HomepageBannerViewSet, LookbookViewSet

factory = RequestFactory()

request = factory.get('/api/v1/homepage/banners/')
view = HomepageBannerViewSet.as_view({'get': 'list'})
response = view(request)
print("Banners:", response.data)

request = factory.get('/api/v1/lookbook/')
view = LookbookViewSet.as_view({'get': 'list'})
response = view(request)
print("Lookbook:", response.data)
