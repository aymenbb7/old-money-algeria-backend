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

def dashboard_wilayas(request):
    return render(request, 'dashboard/wilayas.html')

def dashboard_customers(request):
    return render(request, 'dashboard/customers.html')

def dashboard_coupons(request):
    return render(request, 'dashboard/coupons.html')
