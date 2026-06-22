import json
from django.db import transaction
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Collection, Review, ProductVariant, ProductImage
from .serializers import (
    ProductSerializer, ProductCreateUpdateSerializer,
    CollectionSerializer, ReviewSerializer, ProductImageSerializer
)
from rest_framework.decorators import action

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('images', 'variants', 'collections')
    lookup_field = 'slug'
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
        images_data = data.pop('images', None)
        image_urls = data.pop('image_urls', None)
        
        serializer = ProductCreateUpdateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        self._handle_collections(product, collections_data)
        self._handle_variants(product, variants_data)
        
        # In create, use image_urls array if provided
        urls_to_handle = image_urls if image_urls is not None else images_data
        self._handle_images(product, urls_to_handle)

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        product = self.get_object()
        data = request.data.copy() if hasattr(request.data, 'copy') else request.data
        collections_data = data.pop('collections', None)
        variants_data = data.pop('variants', None)
        # Completely ignore images and image_urls on update
        data.pop('images', None)
        data.pop('image_urls', None)
        
        serializer = ProductCreateUpdateSerializer(product, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        if collections_data is not None:
            product.collections.clear()
            self._handle_collections(product, collections_data)
            
        if variants_data is not None:
            product.variants.all().delete()
            self._handle_variants(product, variants_data)

        # Do not call _handle_images on update
        return Response(ProductSerializer(product).data)

    def _handle_images(self, product, images_data):
        if not images_data:
            product.images.all().delete()
            return
            
        if isinstance(images_data, str):
            try:
                images_data = json.loads(images_data)
            except:
                images_data = [u.strip() for u in images_data.replace('\n', ',').split(',') if u.strip()]
        elif not isinstance(images_data, list):
            images_data = [images_data]
            
        product.images.all().delete()
        for idx, img_url in enumerate(images_data):
            is_main = (idx == 0)
            is_hover = (idx == 1)
            ProductImage.objects.create(
                product=product,
                image_url=img_url,
                is_main=is_main,
                is_hover=is_hover
            )

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
        elif isinstance(variants_data, list) and len(variants_data) > 0 and isinstance(variants_data[0], str):
            try:
                variants_data = json.loads(variants_data[0])
            except:
                variants_data = []
                
        for variant in variants_data:
            if isinstance(variant, str):
                try:
                    variant = json.loads(variant)
                except:
                    continue
            size = variant.get('size')
            colors = variant.get('colors', [])
            stock = variant.get('stock', 0)
            
            if isinstance(colors, str):
                colors = [c.strip() for c in colors.split(',') if c.strip()]
                
            for color in colors:
                ProductVariant.objects.create(
                    product=product,
                    size=size,
                    color=color,
                    stock=stock
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

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        image_url = request.data.get('image_url')
        
        if not product_id or not image_url:
            return Response({'detail': 'product and image_url are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
        is_main = not product.images.filter(is_main=True).exists()
        
        img = ProductImage.objects.create(
            product=product,
            image_url=image_url,
            is_main=is_main
        )
        return Response(ProductImageSerializer(img).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='set-main')
    def set_main(self, request, pk=None):
        img = self.get_object()
        product = img.product
        
        # Set all to false
        product.images.all().update(is_main=False)
        
        # Set this one to true
        img.is_main = True
        img.save()
        
        return Response(ProductImageSerializer(img).data)
