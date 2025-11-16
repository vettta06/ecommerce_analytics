import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from etl_pipeline.models import DataSource, Product, SalesData, DailyMetrics


class ETLService:
    """Базовый сервис для ETL-процессов. Обеспечивает сбор, преобразование и зарузку данных из внешних источников."""

    def __init__(self, data_source_name):
        """Инициализация ETL сервиса для конкретного источника данных."""
        try:
            self.data_source = DataSource.objects.get(name=data_source_name)
            self.last_sync = self.data_source.last_sync
        except DataSource.DoesNotExist:
            raise ValueError(f"Источник данных {data_source_name} не найден")

    def extract(self, start_date=None, end_date=None):
        """Извлечение данных из внешнего источника."""
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if not start_date and self.last_sync:
            start_date = self.last_sync.date()
        if not end_date:
            end_date = datetime.now().date()
        print(
            f"Извлечение данных из {self.data_source.name} с {start_date} по {end_date}"
        )
        mock_data = self._get_mock_data(start_date, end_date)
        return mock_data

    def transform(self, raw_data):
        """Преобразование и очистка сырых данных."""
        if not raw_data:
            return pd.DataFrame()
        df = pd.DataFrame(raw_data)
        df = self._clean_data(df)
        df = self._aggregate_data(df)
        print(f"Преобразовано {len(df)} записей")
        return df

    def load(self, transformed_data):
        """Загрузка преобразованных данных в целевую базу данных."""
        if transformed_data.empty:
            print("Нет данных для загрузки")
            return
        records_created = 0
        for _, row in transformed_data.iterrows():
            product, created = Product.objects.get_or_create(
                sku=row["sku"],
                defaults={
                    "name": row["product_name"],
                    "category": row["category"],
                    "price": row["price"],
                },
            )
            sales_data, created = SalesData.objects.get_or_create(
                product=product,
                date=row["date"],
                source=self.data_source,
                defaults={"quantity": row["quantity"], "revenue": row["revenue"]},
            )
            if created:
                records_created += 1
        self.data_source.last_sync = timezone.now()
        self.data_source.save()
        print(f"Загружено {records_created} новых записей продаж")
        self._update_daily_metrics()

    def run_etl(self, start_date=None, end_date=None):
        """Запуск полного etl-процесса."""
        print(f"Запуск ETL процесса для {self.data_source.name}")
        try:
            raw_data = self.extract(start_date, end_date)
            transformed_data = self.transform(raw_data)
            self.load(transformed_data)
            print("ETL процесс успешно завершен")
        except Exception as e:
            print(f"Ошибка в ETL процессе: {str(e)}")
            raise

    def _get_mock_data(self, start_date, end_date):
        """Генерация тестовых данных для демонстрации работы ETL."""
        mock_products = [
            {
                "sku": "PROD001",
                "name": "iPhone 14",
                "category": "Смартфоны",
                "price": 799.99,
            },
            {
                "sku": "PROD002",
                "name": "Samsung Galaxy",
                "category": "Смартфоны",
                "price": 699.99,
            },
            {
                "sku": "PROD003",
                "name": "MacBook Pro",
                "category": "Ноутбуки",
                "price": 1999.99,
            },
        ]
        mock_data = []
        current_date = start_date
        # Генерируем данные для каждого дня в периоде
        while current_date <= end_date:
            for product in mock_products:
                # Случайное количество продаж для тестирования
                import random

                quantity = random.randint(1, 10)
                revenue = product["price"] * quantity
                mock_data.append(
                    {
                        "sku": product["sku"],
                        "product_name": product["name"],
                        "category": product["category"],
                        "price": product["price"],
                        "date": current_date,
                        "quantity": quantity,
                        "revenue": revenue,
                    }
                )
            current_date = current_date + timedelta(days=1)
        return mock_data

    def _clean_data(self, df):
        """Очистка данных от некорректных значений и пропусков."""
        df = df.dropna()
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
        df = df[df["quantity"] > 0]
        df = df[df["price"] > 0]
        return df

    def _aggregate_data(self, df):
        """Агрегация данных для устранения дубликатов. Группирует данные по товару и дате."""
        aggregated = (
            df.groupby(["sku", "date", "product_name", "category", "price"])
            .agg({"quantity": "sum", "revenue": "sum"})
            .reset_index()
        )
        return aggregated

    def _update_daily_metrics(self):
        """Обновление ежедневных агрегированных метрик."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        sales_data = SalesData.objects.filter(date__gte=start_date, date__lte=end_date)
        for single_date in pd.date_range(start_date, end_date):
            date_sales = sales_data.filter(date=single_date.date())

            if date_sales.exists():
                total_revenue = sum(sale.revenue for sale in date_sales)
                total_orders = date_sales.count()
                products_sold = sum(sale.quantity for sale in date_sales)
                avg_order_value = (
                    total_revenue / total_orders if total_orders > 0 else 0
                )
                # Создаем или обновляем метрики дня
                DailyMetrics.objects.update_or_create(
                    date=single_date.date(),
                    defaults={
                        "total_revenue": total_revenue,
                        "total_orders": total_orders,
                        "avg_order_value": avg_order_value,
                        "products_sold": products_sold,
                    },
                )
        print("Агрегированные метрики обновлены")
        