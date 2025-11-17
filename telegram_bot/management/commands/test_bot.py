from django.core.management.base import BaseCommand
from etl_pipeline.models import SalesData, DailyMetrics, Product
from django.db.models import Sum, Count
from datetime import datetime, timedelta


class Command(BaseCommand):
    """
    Тестовая команда для проверки функциональности бота без реального Telegram
    """
    help = 'Тест функциональности бота (без реального Telegram)'
    
    def handle(self, *args, **options):
        """
        Показывает статистику в консоли
        """
        self.stdout.write(
            self.style.SUCCESS('🤖 Тест функциональности Telegram бота')
        )
        
        try:
            # Общая статистика
            total_products = Product.objects.count()
            total_sales = SalesData.objects.count()
            total_revenue = SalesData.objects.aggregate(
                total=Sum('revenue')
            )['total'] or 0
            
            # Статистика за неделю
            week_ago = datetime.now().date() - timedelta(days=7)
            weekly_data = SalesData.objects.filter(
                date__gte=week_ago
            ).aggregate(
                sales_count=Count('id'),
                week_revenue=Sum('revenue')
            )
            
            # Топ товаров
            top_products = SalesData.objects.values(
                'product__name'
            ).annotate(
                total_revenue=Sum('revenue'),
                total_sold=Sum('quantity')
            ).order_by('-total_revenue')[:3]
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write("📊 ОБЩАЯ СТАТИСТИКА (как в боте)")
            self.stdout.write("="*50)
            
            self.stdout.write(f"Товаров в системе: {total_products}")
            self.stdout.write(f"Всего продаж: {total_sales}")
            self.stdout.write(f"Общая выручка: {total_revenue:,.0f} руб.")
            
            self.stdout.write(f"\n📈 ЗА ПОСЛЕДНЮЮ НЕДЕЛЮ:")
            self.stdout.write(f"Продаж: {weekly_data['sales_count'] or 0}")
            self.stdout.write(f"Выручка: {weekly_data['week_revenue'] or 0:,.0f} руб.")
            
            self.stdout.write(f"\nТОП ТОВАРОВ:")
            for i, product in enumerate(top_products, 1):
                self.stdout.write(f"{i}. {product['product__name']}")
                self.stdout.write(f"   {product['total_revenue']:,.0f} руб.")
                self.stdout.write(f"   {product['total_sold']} шт.")
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write(
                self.style.SUCCESS('Функциональность бота проверена!')
            )
            self.stdout.write(
                "💡 Для реального бота создайте токен через @BotFather"
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {str(e)}')
            )