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


class R2PresignedUploadView(views.APIView):
    """
    Return a presigned PUT URL so the browser can upload an image directly to
    Cloudflare R2 without routing the bytes through the Django/Render server.

    POST body (JSON):
        filename     : original file name (used only to determine extension)
        content_type : MIME type — must be an allowed image type
        size_bytes   : compressed file size in bytes (validated server-side)

    Response (200):
        upload_url   : presigned PUT URL (valid 5 minutes)
        public_url   : permanent public URL the browser should save as image_url
        key          : storage key inside the bucket
    """
    permission_classes = [permissions.IsAdminUser]

    ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

    def post(self, request):
        import uuid as _uuid
        import os as _os
        import boto3
        from botocore.config import Config as BotocoreConfig
        from django.conf import settings as dj_settings

        filename     = request.data.get('filename', 'image.jpg')
        content_type = request.data.get('content_type', 'image/jpeg')
        try:
            size_bytes = int(request.data.get('size_bytes', 0))
        except (ValueError, TypeError):
            size_bytes = 0

        if content_type not in self.ALLOWED_TYPES:
            return Response(
                {'error': f'File type not allowed: {content_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if size_bytes > self.MAX_SIZE_BYTES:
            return Response(
                {'error': 'File too large (max 10 MB after compression)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Read R2 credentials from env (preferred) or Django settings
        def _cfg(key):
            return _os.getenv(key, '') or getattr(dj_settings, key, '')

        account_id = _cfg('R2_ACCOUNT_ID')
        access_key = _cfg('R2_ACCESS_KEY_ID')
        secret_key = _cfg('R2_SECRET_ACCESS_KEY')
        bucket     = _cfg('R2_BUCKET_NAME')
        pub_base   = _cfg('R2_PUBLIC_URL')

        if not all([account_id, access_key, secret_key, bucket]):
            # Not configured — browser will fall back to legacy upload path
            return Response(
                {'error': 'R2 storage is not configured on this server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Build unique object key
        ext_map = {
            'image/jpeg': '.jpg',
            'image/png':  '.png',
            'image/webp': '.webp',
            'image/gif':  '.gif',
        }
        ext = ext_map.get(content_type, '.jpg')
        key = f"products/{_uuid.uuid4().hex}{ext}"

        try:
            r2 = boto3.client(
                's3',
                endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=BotocoreConfig(signature_version='s3v4'),
                region_name='auto',
            )
            upload_url = r2.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket':      bucket,
                    'Key':         key,
                    'ContentType': content_type,
                },
                ExpiresIn=300,  # 5 minutes
            )
        except Exception as e:
            logger.error("R2 presign error: %s", e, exc_info=True)
            return Response(
                {'error': f'Could not generate upload URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Derive permanent public URL
        if pub_base:
            public_url = f"{pub_base.rstrip('/')}/{key}"
        else:
            # Fallback: strip query-string from presigned URL
            public_url = upload_url.split('?')[0]

        return Response({
            'upload_url': upload_url,
            'public_url': public_url,
            'key':        key,
        }, status=status.HTTP_200_OK)

