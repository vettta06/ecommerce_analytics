from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Avg
from .models import DataSource, Product, SalesData, DailyMetrics
from .serializers import (
    DataSourceSerializer, ProductSerializer, 
    SalesDataSerializer, DailyMetricsSerializer
)


class DataSourceViewSet(viewsets.ModelViewSet):
    """API endpoint для управления источниками данных."""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint для управления товарами."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class SalesDataViewSet(viewsets.ModelViewSet):
    """API endpoint для данных о продажах."""
    queryset = SalesData.objects.select_related('product', 'source').all()
    serializer_class = SalesDataSerializer


class DailyMetricsViewSet(viewsets.ModelViewSet):
    """API endpoint для ежедневной метрики."""
    queryset = DailyMetrics.objects.all()
    serializer_class = DailyMetricsSerializer


@api_view(['GET'])
def sales_summary(request):
    """API endpoint для сводной статистики продаж."""
    summary = {
        'total_products': Product.objects.count(),
        'total_sales': SalesData.objects.count(),
        'total_revenue': SalesData.objects.aggregate(Sum('revenue'))['revenue__sum'] or 0,
        'avg_sale_value': SalesData.objects.aggregate(Avg('revenue'))['revenue__avg'] or 0,
    }
    return Response(summary)
