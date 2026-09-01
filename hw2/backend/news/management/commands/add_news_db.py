import csv
import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from news.models import News


class Command(BaseCommand):
    help = "Puebla la base de datos de News con 5 noticias del dataset Fake.csv"

    def handle(self, *args, **options):
        csv_path = os.path.join(
            settings.BASE_DIR, "news", "management", "commands", "Fake.csv"
        )

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            count = 0
            for row in reader:
                if count >= 5:
                    break

                try:
                    date_value = datetime.strptime(
                        row["date"],
                        "%B %d, %Y",
                    ).date()
                except ValueError:
                    # Si alguna fecha viene en un formato distinto, la saltamos
                    continue

                News.objects.create(
                    headline=row["title"],
                    body=row["text"],
                    date=date_value,
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Se agregaron {count} noticias a la base de datos.")
        )