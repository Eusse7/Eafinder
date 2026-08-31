import os
import csv
from django.core.management.base import BaseCommand
from news.models import News
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate News database from Fake.csv or with dummy data'

    def handle(self, *args, **kwargs):
        filepath = 'Fake.csv'
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    # Assuming format: title, text, subject, date
                    headline = row[0]
                    body = row[1]
                    try:
                        date = timezone.datetime.strptime(row[3].strip(), '%B %d, %Y').date()
                    except:
                        date = timezone.now().date()
                    
                    News.objects.create(headline=headline, body=body, date=date)
            self.stdout.write(self.style.SUCCESS('Successfully imported news from Fake.csv'))
        else:
            self.stdout.write(self.style.WARNING('Fake.csv not found, generating dummy news'))
            News.objects.create(headline='Nuevo Estreno de Cine', body='Se espera una gran recepción del público en taquilla.', date=timezone.now().date())
            News.objects.create(headline='Actor famoso gana premio', body='El reconocimiento fue otorgado por su gran trayectoria.', date=timezone.now().date())
            News.objects.create(headline='Festival de Cine Independiente', body='El evento reunió a los mejores directores del momento.', date=timezone.now().date())
            self.stdout.write(self.style.SUCCESS('Successfully created dummy news'))
