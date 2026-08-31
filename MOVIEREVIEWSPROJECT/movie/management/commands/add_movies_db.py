import csv
import os
from django.core.management.base import BaseCommand
from movie.models import Movie
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate the movies database from movies_initial.csv'

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, 'movie', 'management', 'commands', 'movies_initial.csv')
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Movie.objects.create(
                    title=row['title'],
                    genre=row['genre'],
                    year=int(row['year']) if row['year'] else None,
                    description=row['description'],
                    image='movie/images/default.jpg'
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded movies'))
