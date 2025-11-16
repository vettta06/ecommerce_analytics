from django.shortcuts import render
from django.http import JsonResponse
from etl_pipeline.models import Product, SalesData, DailyMetrics

def dashboard_home(request):
    """
    Главная страница дашборда
    """
    return render(request, 'dashboard/home.html')

def analytics_view(request):
    """
    Страница аналитики с графиками
    """
    context = {
        'total_products': Product.objects.count(),
        'total_sales': SalesData.objects.count(),
    }
    return render(request, 'dashboard/analytics.html', context)