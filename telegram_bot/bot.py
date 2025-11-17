from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from django.conf import settings
from etl_pipeline.models import SalesData, DailyMetrics, Product
from django.db.models import Sum, Count
from datetime import datetime, timedelta



class TelegramBot:
    """Бот для уведомлений и быстрых отчётов по аналитике."""

    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self._register_handlers()
 
    def _register_handlers(self):
        """Регистрация обработчиков команд."""
        self.dp.message.register(self.start_handler, Command("start"))
        self.dp.message.register(self.stats_handler, Command("stats"))
        self.dp.message.register(self.today_handler, Command("today"))
        self.dp.message.register(self.products_handler, Command("products"))
        
    async def start_handler(self, message: types.Message):
        """Обработчик команды /start."""
        welcome_text = """
Добро пожаловать в E-commerce Analytics Bot!

Доступные команды:
/start - Начало работы
/stats - Общая статистика
/today - Статистика за сегодня
/products - Топ товаров
        """
        await message.answer(welcome_text)
    
    async def stats_handler(self, message: types.Message):
        """Обработчик команды /stats."""
        try:
            total_products = Product.objects.count()
            total_sales = SalesData.objects.count()
            total_revenue = SalesData.objects.aaggregate(
                Sum('revenue')
            )['revenue__sum'] or 0
            week_ago = datetime.now().date() - timedelta(days=7)
            weekly_sales = SalesData.objects.filter(
                date__gte=week_ago
            ).aggregate(
                sales_count=Count('id'),
                week_revenue=Sum('revenue')
            )
            stats_text = f"""
📊 ОБЩАЯ СТАТИСТИКА

Товаров в системе: {total_products}\
Всего продаж: {total_sales}
Общая выручка: {total_revenue:,.0f} руб.

ЗА ПОСЛЕДНЮЮ НЕДЕЛЮ:
Продаж: {weekly_sales['sales_count'] or 0}
Выручка: {weekly_sales['week_revenue'] or 0:,.0f} руб.
            """
            await message.answer(stats_text)
        except Exception as e:
            await message.answer(f"Ошибка при получении статистики: {str(e)}")

    async def today_handler(self, message: types.Message):
        """Обработчик окманды /today."""
        try:
            today = datetime.now().date()
            today_metrics = DailyMetrics.objects.filter(date=today).first()
            if today_metrics:
                today_text = f"""
📅 СТАТИСТИКА ЗА СЕГОДНЯ ({today})

Выручка: {today_metrics.total_revenue:,.0f} руб.
Заказов: {today_metrics.total_orders}
Товаров продано: {today_metrics.products_sold}
Средний чек: {today_metrics.avg_order_value:,.0f} руб.
                """
            else:
                today_text = f"📅 На {today} данных пока нет"
            await message.answer(today_text)
        except Exception as e:
            await message.answer(f" Ошибка при получении данных за сегодня: {str(e)}")
       
    async def products_handler(self, message: types.Message):
        """Обработчик команд /products."""
        try:
            top_products = SalesData.objects.values(
                'product__name'
            ).annotate(
                total_revenue=Sum('revenue'),
                total_sold=Sum('quantity')
            ).order_by('-total_revenue')[:5]
            if top_products:
                products_text = "🏆 ТОП-5 ТОВАРОВ ПО ВЫРУЧКЕ:\n\n"                
                for i, product in enumerate(top_products, 1):
                    products_text += f"{i}. {product['product__name']}\n"
                    products_text += f"  {product['total_revenue']:,.0f} руб.\n"
                    products_text += f"  {product['total_sold']} шт.\n\n"
            else:
                products_text = "Товаров пока нет в системе"
        except Exception as e:
            await message.answer(f"Ошибка при получении топа товаров: {str(e)}")
     
    async def send_daily_report(self, chat_id: int):
        """Отправка ежедневного отчёта."""
        try:
            yesterday = datetime.now().date() - timedelta(days=1)
            metrics = DailyMetrics.objects.filter(date=yesterday).first()            
            if metrics:
                report_text = f"""
📊 ЕЖЕДНЕВНЫЙ ОТЧЕТ ЗА {yesterday}

Выручка: {metrics.total_revenue:,.0f} руб.
Заказов: {metrics.total_orders}
Товаров продано: {metrics.products_sold}
Средний чек: {metrics.avg_order_value:,.0f} руб.
                """
            else:
                report_text = f"📊 На {yesterday} данных нет"
            await self.bot.send_message(chat_id, report_text)
 
        except Exception as e:
            print(f"Ошибка отправки ежедневного отчета: {e}")

    async def run(self):
        """Запуск бота."""
        print("Запущен")
        await self.dp.start_polling(self.bot)

