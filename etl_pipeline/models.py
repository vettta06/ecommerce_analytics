from django.db import models


class DataSource(models.Model):
    """Модель для хранения информации об источниках данных."""

    name = models.CharField(max_length=100, verbose_name="Название источника")
    api_endpoint = models.URLField(verbose_name="API endpoint", blank=True)
    api_key = models.CharField(max_length=255, blank=True, verbose_name="API ключ")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    last_sync = models.DateTimeField(
        null=True, blank=True, verbose_name="Последняя синхронизация"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    def __str__(self):
        return f"{self.name} ({'активен' if self.is_active else 'неактивен'})"

    class Meta:
        verbose_name = "Источник данных"
        verbose_name_plural = "Источники данных"


class Product(models.Model):
    """Модель товара для анализа продаж."""

    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU")
    name = models.CharField(max_length=255, verbose_name="Название товара")
    category = models.CharField(max_length=100, verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return f"{self.name} ({self.sku})"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["category"]),
        ]


class SalesData(models.Model):
    """Модель для хранения данных о продажах."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    date = models.DateField(verbose_name="Дата продажи")
    quantity = models.IntegerField(verbose_name="Количество")
    revenue = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Выручка"
    )
    source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, verbose_name="Источник"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    def save(self, *args, **kwargs):
        """Автоматически вычисляем выручку если не задана"""
        if not self.revenue and self.product and self.quantity:
            self.revenue = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.date} - {self.quantity} шт."

    class Meta:
        verbose_name = "Данные о продажах"
        verbose_name_plural = "Данные о продажах"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["product"]),
            models.Index(fields=["source"]),
        ]
        unique_together = ["product", "date", "source"]


class DailyMetrics(models.Model):
    """Агрегированные метрики по дням для быстрого доступа."""

    date = models.DateField(unique=True, verbose_name="Дата")
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Общая выручка"
    )
    total_orders = models.IntegerField(default=0, verbose_name="Всего заказов")
    avg_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Средний чек"
    )
    products_sold = models.IntegerField(default=0, verbose_name="Товаров продано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return f"Метрики за {self.date}"

    class Meta:
        verbose_name = "Ежедневные метрики"
        verbose_name_plural = "Ежедневные метрики"
        ordering = ["-date"]
