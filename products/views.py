from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Collection, Review
from .serializers import (
    ProductSerializer, ProductCreateUpdateSerializer,
    CollectionSerializer, ReviewSerializer
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('images', 'variants', 'collections')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured', 'is_bestseller', 'is_new_arrival', 'collections__slug']
    search_fields = ['name', 'description', 'sku', 'tags']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

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
