from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import WilayaViewSet, StoreSettingsViewSet, HomepageContentViewSet, AnalyticsAPIView, HomepageSectionViewSet, ImageUploadView
from products.views import ProductViewSet, CollectionViewSet, ReviewViewSet
from orders.views import OrderViewSet, CouponViewSet
from users.views import UserViewSet, CustomerProfileViewSet

router = DefaultRouter()
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

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # API Routes
    path('api/v1/', include(router.urls)),
    
    # Custom Analytics Route
    path('api/v1/analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    
    # Custom Image Upload Route
    path('api/v1/upload-image/', ImageUploadView.as_view(), name='upload_image'),
    
    # Auth Routes
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom Dashboard Route (will be handled by dashboard app)
    path('admin/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
