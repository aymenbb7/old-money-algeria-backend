from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_index, name='dashboard_index'),
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('orders/', views.dashboard_orders, name='dashboard_orders'),
    path('products/', views.dashboard_products, name='dashboard_products'),
    path('wilayas/', views.dashboard_wilayas, name='dashboard_wilayas'),
    path('customers/', views.dashboard_customers, name='dashboard_customers'),
    path('coupons/', views.dashboard_coupons, name='dashboard_coupons'),
]
