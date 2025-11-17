import asyncio
import os
import django
from django.core.management.base import BaseCommand
from telegram_bot.bot import TelegramBot


class Command(BaseCommand):
    """Команда для запуска бота."""
    def handle(self, *args, **options):
        """
        Основной метод обработки команды
        """
        self.stdout.write(
            self.style.SUCCESS('🤖 Запуск Telegram бота...')
        )
        
        from django.conf import settings
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        
        if not token or token == 'your_bot_token_here':
            self.stdout.write(
                self.style.ERROR(
                    'TELEGRAM_BOT_TOKEN не настроен!\n'
                    'Добавьте в .env файл:\n'
                    'TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather\n\n'
                    ' Для тестирования используйте: python manage.py test_bot'
                )
            )
            return
        
        try:
            # Создаем экземпляр бота
            bot = TelegramBot()
            
            # Запускаем бота
            asyncio.run(bot.run())
            
        except TokenValidationError:
            self.stdout.write(
                self.style.ERROR(
                    'Невалидный токен Telegram бота!\n'
                    'Проверьте TELEGRAM_BOT_TOKEN в .env файле.\n'
                    'Токен должен выглядеть как: 1234567890:ABCdefGHIjklMnopQRstuVWXyz'
                )
            )
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('🛑 Остановка бота...')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка запуска бота: {str(e)}')
            )