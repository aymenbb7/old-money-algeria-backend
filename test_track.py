import os
import django
import json
import urllib.request
from urllib.error import HTTPError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from orders.models import Order
from core.models import Wilaya

def test():
    # Ensure there's a Wilaya
    wilaya, _ = Wilaya.objects.get_or_create(code='16', defaults={'name': 'Alger', 'is_active': True})
    
    # Create an order
    order = Order.objects.create(
        guest_name="Test User",
        guest_phone="0555555555",
        wilaya=wilaya,
        address="Test Address",
        is_home_delivery=True,
        total_amount=1000
    )
    
    order_num = order.order_number
    print(f"Created order: {order_num}")
    
    # Call the API
    url = f"http://127.0.0.1:8001/api/v1/orders/track/{order_num}/"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print("API Response:")
            print(json.dumps(data, indent=2))
    except HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
