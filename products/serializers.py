from rest_framework import serializers
from .models import Collection, Product, ProductImage, ProductVariant, Review

class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    image = serializers.CharField(source='image_url', allow_null=True, required=False)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url', 'hero_image_url', 'product_count', 'display_order']

    def get_product_count(self, obj):
        return obj.products.count()

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='image_url')

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_main', 'is_hover']

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
