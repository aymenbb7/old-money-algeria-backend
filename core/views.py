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
    pagination_class = None
    
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
        thirty_days_ago = today - timedelta(days=30)

        # Basic Stats
        total_orders = Order.objects.count()
        todays_orders = Order.objects.filter(created_at__date=today).count()
        pending_orders = Order.objects.filter(status='PENDING').count()
        delivered_orders = Order.objects.filter(status='DELIVERED').count()
        
        # Revenue (Delivered only as requested)
        revenue_today = Order.objects.filter(created_at__date=today, status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        revenue_this_month = Order.objects.filter(created_at__year=today.year, created_at__month=today.month, status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Time Series for Last 30 Days (Daily Orders and Daily Revenue)
        # Using Extra/TruncDate can be complex, doing a fast python-side aggregation for sqlite/pg compatibility
        recent_orders = Order.objects.filter(created_at__date__gte=thirty_days_ago)
        daily_orders_dict = {}
        daily_revenue_dict = {}

        for i in range(31):
            day = thirty_days_ago + timedelta(days=i)
            daily_orders_dict[str(day)] = 0
            daily_revenue_dict[str(day)] = 0

        for order in recent_orders:
            day_str = str(order.created_at.date())
            daily_orders_dict[day_str] += 1
            if order.status == 'DELIVERED':
                daily_revenue_dict[day_str] += float(order.total_amount)

        daily_orders = [{'date': k, 'count': v} for k, v in daily_orders_dict.items()]
        daily_revenue = [{'date': k, 'revenue': v} for k, v in daily_revenue_dict.items()]

        # Orders by Status
        status_counts_raw = Order.objects.values('status').annotate(count=Count('id'))
        orders_by_status = {item['status']: item['count'] for item in status_counts_raw}

        # Top 10 Wilayas
        top_wilayas = Order.objects.values('wilaya__name').annotate(count=Count('id')).order_by('-count')[:10]

        top_wilaya_name = top_wilayas[0]['wilaya__name'] if top_wilayas else "N/A"
        top_wilaya_count = top_wilayas[0]['count'] if top_wilayas else 0

        return Response({
            'total_orders': total_orders,
            'todays_orders': todays_orders,
            'pending_orders': pending_orders,
            'revenue_today': revenue_today,
            'revenue_this_month': revenue_this_month,
            'top_wilaya': {'name': top_wilaya_name, 'count': top_wilaya_count},
            'daily_orders': daily_orders,
            'daily_revenue': daily_revenue,
            'orders_by_status': orders_by_status,
            'top_10_wilayas': top_wilayas,
        })
