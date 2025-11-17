from rest_framework import serializers
from .models import DataSource, Product, SalesData, DailyMetrics


class DataSourceSerializer(serializers.ModelSerializer):
    """Сериализатор для источников данных."""

    class Meta:
        model = DataSource
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров."""

    class Meta:
        model = Product
        fields = "__all__"


class SalesDataSerializer(serializers.ModelSerializer):
    """Сериализатор для данных о продажах."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = SalesData
        fields = "__all__"


class DailyMetricsSerializer(serializers.ModelSerializer):
    """Сериализатор для ежедневных метрик."""

    class Meta:
        model = DailyMetrics
        fields = "__all__"
