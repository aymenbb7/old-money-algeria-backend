from rest_framework import viewsets, permissions, views, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Wilaya, StoreSettings, HomepageContent, HomepageSection
from .serializers import WilayaSerializer, StoreSettingsSerializer, HomepageContentSerializer, HomepageSectionSerializer
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
        return Response({'results': [serializer.data]})

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
        return Response({'results': [serializer.data]})

class HomepageSectionViewSet(viewsets.ModelViewSet):
    queryset = HomepageSection.objects.all()
    serializer_class = HomepageSectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active', 'section_type']
    ordering_fields = ['display_order']
    ordering = ['display_order']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

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

from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
import logging
import traceback

logger = logging.getLogger(__name__)

class ImageUploadView(views.APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request):
        import cloudinary
        config = cloudinary.config()
        return Response({
            'cloud_name': config.cloud_name,
            'api_key_configured': bool(config.api_key),
            'api_secret_configured': bool(config.api_secret),
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided in request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['image']
        try:
            res = cloudinary.uploader.unsigned_upload(
                file_obj,
                upload_preset="old_money_algeria",
                folder="old_money_algeria"
            )
            secure_url = res.get('secure_url')
            return Response({'url': secure_url}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Cloudinary upload failed: %s", str(e), exc_info=True)
            tb = traceback.format_exc()
            print("CLOUDINARY UPLOAD ERROR:", tb)
            return Response({
                'error': str(e),
                'traceback': tb
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
