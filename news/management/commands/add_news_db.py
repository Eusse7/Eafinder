import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from news.models import News


class Command(BaseCommand):
    help = 'Load the first 5 news from Fake.csv into the News model'

    def handle(self, *args, **kwargs):
        csv_file_path = 'news/management/commands/Fake.csv'

        cont = 0
        with open(csv_file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for news in reader:
                if cont >= 5:
                    break

                headline = news['title'].strip()

                # La fecha viene como texto (ej: 'December 31, 2017'),
                # se transforma al formato de fecha antes de guardarla.
                date_value = datetime.strptime(
                    news['date'].strip(),
                    '%B %d, %Y'
                ).date()

                exist = News.objects.filter(headline=headline).first()
                if not exist:
                    News.objects.create(
                        headline=headline,
                        body=news['text'].strip(),
                        date=date_value,
                    )
                else:
                    exist.body = news['text'].strip()
                    exist.date = date_value
                    exist.save()

                cont += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {cont} news to the database')
        )
