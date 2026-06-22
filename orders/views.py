from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Coupon
from .serializers import OrderSerializer, CouponSerializer
from products.models import ProductVariant
from core.models import Wilaya

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'wilaya', 'is_home_delivery']
    search_fields = ['order_number', 'guest_name', 'guest_phone']
    ordering_fields = ['created_at', 'total_amount']

    def get_permissions(self):
        if self.action in ['create', 'checkout', 'track']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @transaction.atomic
    def checkout(self, request):
        data = request.data
        
        wilaya_code = data.get('wilaya_code') or data.get('wilaya')
        items_data = data.get('items', [])
        coupon_code = data.get('coupon_code')
        
        is_home_delivery = data.get('is_home_delivery')
        if is_home_delivery is None:
            delivery_type = data.get('delivery_type', 'HOME')
            is_home_delivery = (delivery_type == 'HOME')
        
        if not items_data:
            return Response({'error': 'La commande doit contenir au moins un article.'}, status=status.HTTP_400_BAD_REQUEST)
            
        wilaya = get_object_or_404(Wilaya, code=wilaya_code)
        if not wilaya.is_active:
            return Response({'error': 'La livraison vers cette wilaya est actuellement désactivée.'}, status=status.HTTP_400_BAD_REQUEST)

        address = data.get('address') or data.get('delivery_address', '')

        # Create Order Shell
        order = Order(
            guest_name=data.get('guest_name'),
            guest_phone=data.get('guest_phone'),
            guest_email=data.get('guest_email'),
            wilaya=wilaya,
            commune=data.get('commune', ''),
            address=address,
            is_home_delivery=is_home_delivery,
            customer_notes=data.get('customer_notes', '')
        )
        
        if request.user.is_authenticated:
            order.customer = request.user
            
        order.save()

        subtotal = 0
        
        # Process Items and Stock
        for item in items_data:
            variant = get_object_or_404(ProductVariant, id=item.get('variant_id'))
            qty = item.get('quantity', 1)
            
            if variant.stock < qty:
                # Rollback handled by transaction.atomic
                return Response({'error': f'Stock insuffisant pour le variant {variant}'}, status=status.HTTP_400_BAD_REQUEST)
                
            variant.stock -= qty
            variant.save()
            
            # Use discount price if available
            price = variant.product.discount_price if variant.product.discount_price else variant.product.price
            
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                size=variant.size,
                color=variant.color,
                price_at_time=price,
                quantity=qty
            )
            subtotal += (price * qty)

        order.subtotal = subtotal
        
        # Calculate Delivery
        delivery_price = wilaya.home_delivery_price if is_home_delivery else wilaya.bureau_delivery_price
        order.delivery_price = delivery_price
        
        # Apply Coupon
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.expiration_date and coupon.expiration_date < timezone.now():
                    return Response({'error': 'Ce code promo a expiré'}, status=status.HTTP_400_BAD_REQUEST)
                if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
                    return Response({'error': 'La limite d\'utilisation de ce code promo a été atteinte'}, status=status.HTTP_400_BAD_REQUEST)
                if subtotal < coupon.min_order_amount:
                    return Response({'error': f'Le montant minimum de commande pour ce code est {coupon.min_order_amount} DZD'}, status=status.HTTP_400_BAD_REQUEST)
                
                if coupon.discount_type == 'FIXED':
                    discount_amount = coupon.value
                elif coupon.discount_type == 'PERCENTAGE':
                    discount_amount = subtotal * (coupon.value / 100)
                    
                coupon.times_used += 1
                coupon.save()
                
                order.coupon = coupon
            except Coupon.DoesNotExist:
                return Response({'error': 'Code promo invalide'}, status=status.HTTP_400_BAD_REQUEST)

        order.discount_amount = discount_amount
        order.total_amount = (subtotal - discount_amount) + delivery_price
        order.save()

        return Response({
            'order_number': order.order_number,
            'total_amount': order.total_amount,
            'status': order.status
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'status updated', 'new_status': order.status})
        return Response({'error': 'invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='track/(?P<order_number>[^/.]+)', permission_classes=[permissions.AllowAny])
    def track(self, request, order_number=None):
        order = get_object_or_404(Order, order_number__iexact=order_number)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code']

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active(self, request):
        now = timezone.now()
        coupons = Coupon.objects.filter(is_active=True).exclude(
            expiration_date__lt=now
        )
        serializer = self.get_serializer(coupons, many=True)
        return Response({'results': serializer.data})
