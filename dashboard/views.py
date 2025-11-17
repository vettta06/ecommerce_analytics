from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from etl_pipeline.models import DailyMetrics, Product, SalesData


def dashboard_home(request):
    """Главная страница дашборда."""
    context = {
        "total_products": Product.objects.count(),
        "total_sales": SalesData.objects.count(),
    }
    return render(request, "dashboard/home.html", context)


def analytics_view(request):
    """Страница аналитики с графиками."""
    context = {
        "total_products": Product.objects.count(),
        "total_sales": SalesData.objects.count(),
    }
    return render(request, "dashboard/analytics.html", context)


def sales_revenue_chart_data(request):
    """API endpoint для данных графика выручки по дням."""
    # Получаем данные за последние 30 дней
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    metrics = DailyMetrics.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).order_by("date")
    data = {
        "labels": [metric.date.strftime("%Y-%m-%d") for metric in metrics],
        "revenue": [float(metric.total_revenue) for metric in metrics],
        "orders": [metric.total_orders for metric in metrics],
    }
    return JsonResponse(data)


def top_products_chart_data(request):
    """API endpoint для данных топа товаров по выручке."""
    top_products = (
        SalesData.objects.values("product__name")
        .annotate(total_revenue=sum("revenue"), total_sold=sum("quantity"))
        .order_by("-total_revenue")[:10]
    )
    data = {
        "products": [item["product__name"] for item in top_products],
        "revenue": [float(item["total_revenue"]) for item in top_products],
        "sold": [item["total_sold"] for item in top_products],
    }
    return JsonResponse(data)


def category_sales_data(request):
    """API endpoint для данных продаж по категориям."""
    category_data = (
        SalesData.objects.values("product__category")
        .annotate(total_revenue=sum("revenue"), total_quantity=sum("quantity"))
        .order_by("-total_revenue")
    )
    data = {
        "categories": [item["product__category"] for item in category_data],
        "revenue": [float(item["total_revenue"]) for item in category_data],
        "quantity": [item["total_quantity"] for item in category_data],
    }
    return JsonResponse(data)
