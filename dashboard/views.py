from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def dashboard_login(request):
    return render(request, 'dashboard/login.html')

def dashboard_index(request):
    return render(request, 'dashboard/index.html')

def dashboard_orders(request):
    return render(request, 'dashboard/orders.html')

def dashboard_products(request):
    return render(request, 'dashboard/products.html')

def dashboard_collections(request):
    return render(request, 'dashboard/collections.html')

def dashboard_wilayas(request):
    return render(request, 'dashboard/wilayas.html')

def dashboard_settings(request):
    return render(request, 'dashboard/settings.html')

def dashboard_customers(request):
    return render(request, 'dashboard/customers.html')

def dashboard_coupons(request):
    return render(request, 'dashboard/coupons.html')

def dashboard_homepage(request):
    return render(request, 'dashboard/homepage.html')

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, WebPushSubscription
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Notification.objects.all()

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'ok'})

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        data = request.data
        endpoint = data.get('endpoint')
        p256dh = data.get('p256dh')
        auth = data.get('auth')

        if not all([endpoint, p256dh, auth]):
            return Response({'error': 'Missing push subscription fields'}, status=status.HTTP_400_BAD_REQUEST)

        WebPushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': p256dh,
                'auth': auth
            }
        )
        return Response({'status': 'subscribed'})
