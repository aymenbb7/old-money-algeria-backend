from rest_framework import serializers
from .models import Order, OrderItem, Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'product_name', 'size', 'color', 'price_at_time', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_number', 'total_amount', 'discount_amount', 'subtotal', 'delivery_price']
