from django.core.management.base import BaseCommand
from news.models import News
from datetime import datetime
import csv


class Command(BaseCommand):
    help = 'Load news from Fake.csv into the News model'

    def handle(self, *args, **kwargs):

        csv_file_path = 'news/management/commands/Fake.csv'

        created_count = 0
        updated_count = 0

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:

                reader = csv.DictReader(file)

                cont = 0

                for movie in reader:

                    if cont == 5:
                        break

                    date_value = datetime.strptime(
                        movie['date'],
                        '%B %d, %Y'
                    ).date()

                    obj, created = News.objects.update_or_create(
                        headline=movie['title'],
                        defaults={
                            'body': movie['text'],
                            'date': date_value,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    cont += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed. '
                    f'Created: {created_count}, '
                    f'Updated: {updated_count}'
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'File not found: {csv_file_path}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Unexpected error: {e}'
                )
            )