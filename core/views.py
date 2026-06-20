from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Wilaya, StoreSettings, HomepageContent
from .serializers import WilayaSerializer, StoreSettingsSerializer, HomepageContentSerializer
from orders.models import Order
from products.models import Product, ProductVariant

class WilayaViewSet(viewsets.ModelViewSet):
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    # To support bulk edit as requested
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request, *args, **kwargs)
        
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StoreSettingsViewSet(viewsets.ModelViewSet):
    queryset = StoreSettings.objects.all()
    serializer_class = StoreSettingsSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def list(self, request, *args, **kwargs):
        settings = StoreSettings.objects.first()
        if not settings:
            settings = StoreSettings.objects.create()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

class HomepageContentViewSet(viewsets.ModelViewSet):
    queryset = HomepageContent.objects.all()
    serializer_class = HomepageContentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def list(self, request, *args, **kwargs):
        content = HomepageContent.objects.first()
        if not content:
            content = HomepageContent.objects.create()
        serializer = self.get_serializer(content)
        return Response(serializer.data)

class AnalyticsAPIView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)

        # Revenue
        revenue_today = Order.objects.filter(created_at__date=today, status__in=['DELIVERED', 'SHIPPED', 'CONFIRMED']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        revenue_this_month = Order.objects.filter(created_at__year=today.year, created_at__month=today.month, status__in=['DELIVERED', 'SHIPPED', 'CONFIRMED']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Orders
        total_orders = Order.objects.count()
        todays_orders = Order.objects.filter(created_at__date=today).count()
        pending_orders = Order.objects.filter(status='PENDING').count()
        delivered_orders = Order.objects.filter(status='DELIVERED').count()
        
        # Products
        total_products = Product.objects.count()

        return Response({
            'revenue_today': revenue_today,
            'revenue_this_month': revenue_this_month,
            'total_orders': total_orders,
            'todays_orders': todays_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_products': total_products,
        })
