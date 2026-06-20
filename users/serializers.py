from rest_framework import serializers
from .models import User, CustomerProfile
from products.serializers import ProductSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'first_name', 'last_name']
        read_only_fields = ['id']

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    favorite_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'total_orders', 'total_spending', 'last_order_date', 'favorite_products']
