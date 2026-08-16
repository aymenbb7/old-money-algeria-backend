from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import WilayaViewSet, StoreSettingsViewSet, HomepageContentViewSet, AnalyticsAPIView, HomepageSectionViewSet, ImageUploadView, R2PresignedUploadView
from products.views import ProductViewSet, CollectionViewSet, ReviewViewSet, ProductImageViewSet
from orders.views import OrderViewSet, CouponViewSet
from users.views import UserViewSet, CustomerProfileViewSet
from dashboard.views import NotificationViewSet

router = DefaultRouter()
router.register(r'products/images', ProductImageViewSet, basename='product-images')
router.register(r'products', ProductViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'wilayas', WilayaViewSet)
router.register(r'store-settings', StoreSettingsViewSet)
router.register(r'settings', StoreSettingsViewSet, basename='settings')
router.register(r'homepage-content', HomepageContentViewSet)
router.register(r'homepage/banners', HomepageContentViewSet, basename='banners')
router.register(r'homepage/sections', HomepageSectionViewSet, basename='sections')
router.register(r'users', UserViewSet)
router.register(r'customers', CustomerProfileViewSet)
router.register(r'dashboard/notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # API Routes
    path('api/v1/', include(router.urls)),
    
    # Custom Analytics Route
    path('api/v1/analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    
    # Image Upload Routes
    # Legacy Cloudinary server-side upload (kept for backward compat / development)
    path('api/v1/upload-image/', ImageUploadView.as_view(), name='upload_image'),
    # R2 presigned URL — browser uploads directly to R2, no bytes through Django
    path('api/v1/r2-presign/', R2PresignedUploadView.as_view(), name='r2_presign'),
    
    # Auth Routes
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom Dashboard Route (will be handled by dashboard app)
    path('admin/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
