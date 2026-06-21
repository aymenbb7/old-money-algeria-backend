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
        data = request.data.copy() if hasattr(request.data, 'copy') else request.data
        collections_data = data.pop('collections', None)
        variants_data = data.pop('variants', None)
        
        serializer = ProductCreateUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        self._handle_collections(product, collections_data)
        self._handle_variants(product, variants_data)
        
        # Handle Images
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_main=(idx == 0) # First image is main
            )

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        product = self.get_object()
        data = request.data.copy() if hasattr(request.data, 'copy') else request.data
        collections_data = data.pop('collections', None)
        variants_data = data.pop('variants', None)
        
        serializer = ProductCreateUpdateSerializer(product, data=data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        if collections_data is not None:
            self._handle_collections(product, collections_data)
            
        if variants_data is not None:
            # For simplicity, if variants are provided on update, we replace them.
            product.variants.all().delete()
            self._handle_variants(product, variants_data)

        # Handle Images if provided
        images = request.FILES.getlist('images')
        if images:
            for idx, img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    is_main=False
                )

        return Response(ProductSerializer(product).data)

    def _handle_collections(self, product, collections_data):
        if not collections_data:
            return
            
        # Ensure it's a list
        if isinstance(collections_data, str):
            try:
                collections_data = json.loads(collections_data)
            except:
                collections_data = [collections_data]
        if not isinstance(collections_data, list):
            collections_data = [collections_data]

        from django.db.models import Q
        pk_list = []
        for c_val in collections_data:
            try:
                c_id = int(c_val)
                pk_list.append(c_id)
            except (ValueError, TypeError):
                col = Collection.objects.filter(Q(slug=c_val) | Q(name__iexact=c_val)).first()
                if col:
                    pk_list.append(col.id)
        
        if pk_list:
            product.collections.set(pk_list)

    def _handle_variants(self, product, variants_data):
        if not variants_data:
            return
            
        if isinstance(variants_data, str):
            try:
                variants_data = json.loads(variants_data)
            except:
                variants_data = []
                
        for variant in variants_data:
            ProductVariant.objects.create(
                product=product,
                size=variant.get('size'),
                color=variant.get('color'),
                stock=variant.get('stock', 0)
            )

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
