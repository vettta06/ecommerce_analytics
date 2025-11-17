from django.core.management.base import BaseCommand
from etl_pipeline.services.etl_service import ETLService


class Command(BaseCommand):
    """Команда для запуска ETL процесса из комнадной строки."""

    help = "Запуск ETL процесса для сбора и обработки данных"

    def add_arguments(self, parser):
        """Добавление аргументов командной строки для настройки ETL процесса."""
        parser.add_argument(
            "--source", type=str, help="Название источника данных", default="mock_api"
        )
        parser.add_argument(
            "--start-date",
            type=str,
            help="Дата начала периода (YYYY-MM-DD)",
        )
        parser.add_argument(
            "--end-date",
            type=str,
            help="Дата окончания периода (YYYY-MM-DD)",
        )

    def handle(self, *args, **options):
        """Основной метод обработки команды."""
        source_name = options["source"]
        start_date = options["start_date"]
        end_date = options["end_date"]
        self.stdout.write(
            self.style.SUCCESS(f"Запуск ETL процесса для источника: {source_name}")
        )
        try:
            elt_service = ETLService(source_name)
            elt_service.run_etl(start_date, end_date)
            self.stdout.write(self.style.SUCCESS("ETL процесс успешно завершен"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка в ETL процессе: {str(e)}"))
