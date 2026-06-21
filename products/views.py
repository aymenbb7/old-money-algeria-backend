import json
from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Collection, Review, ProductVariant, ProductImage
from .serializers import (
    ProductSerializer, ProductCreateUpdateSerializer,
    CollectionSerializer, ReviewSerializer
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('images', 'variants', 'collections')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured', 'is_bestseller', 'is_new_arrival', 'collections__slug']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ProductCreateUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Handle Categories/Collections
        collections_data = data.get('collections')
        if collections_data:
            if isinstance(collections_data, str):
                collections_data = json.loads(collections_data)
            
            from django.db.models import Q
            for c_val in collections_data:
                try:
                    c_id = int(c_val)
                    product.collections.add(c_id)
                except (ValueError, TypeError):
                    col = Collection.objects.filter(Q(slug=c_val) | Q(name__iexact=c_val)).first()
                    if col:
                        product.collections.add(col.id)

        # Handle Variants
        variants_data = data.get('variants')
        if variants_data:
            if isinstance(variants_data, str):
                variants_data = json.loads(variants_data)
            for variant in variants_data:
                ProductVariant.objects.create(
                    product=product,
                    size=variant.get('size'),
                    color=variant.get('color'),
                    stock=variant.get('stock', 0)
                )

        # Handle Images
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_main=(idx == 0) # First image is main
            )

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'is_approved', 'is_featured']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
