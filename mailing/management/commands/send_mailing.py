from django.core.management import BaseCommand

from mailing.models import Mailing
from mailing.services import start_mailing


class Command(BaseCommand):
    help = "Запускает рассылку по ID через командную строку"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки для запуска")

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена")
            )
            return

        start_mailing(mailing)
