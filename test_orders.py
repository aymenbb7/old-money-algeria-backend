import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from orders.models import Order
from orders.serializers import OrderSerializer

orders = Order.objects.all()[:1]
if orders:
    order = orders[0]
    print(f"Order: {order.order_number}")
    serializer = OrderSerializer(order)
    print(json.dumps(serializer.data, indent=2))
else:
    print("No orders found.")
