from rest_framework import serializers
from .models import Collection, Product, ProductImage, ProductVariant, Review

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'is_hover']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'stock']

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'customer', 'customer_name', 'rating', 'review_text', 'is_approved', 'created_at']
        read_only_fields = ['is_approved']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
