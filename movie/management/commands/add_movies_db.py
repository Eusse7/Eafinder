from django.core.management.base import BaseCommand
from movie.models import Movie
import csv


class Command(BaseCommand):
    help = 'Load movies from movies_initial.csv into the Movie model'

    def handle(self, *args, **kwargs):

        csv_file_path = 'movie/management/commands/movies_initial.csv'

        created_count = 0
        updated_count = 0

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:

                reader = csv.DictReader(file)

                cont = 0 

                for movie in reader:

                    if cont == 100:
                        break

                    obj, created = Movie.objects.update_or_create(
                        title=movie['title'],
                        defaults={
                            'image': 'movie/images/default.jpg',
                            'genre': movie['genre'],
                            'year': movie['year'],
                            'description': movie['plot'],
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