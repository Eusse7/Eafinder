import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie images in the database from local media folder"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        updated_count = 0

        for movie in movies:
            image_filename = f"m_{movie.title}.png"
            image_relative_path = os.path.join('movie', 'images', image_filename)
            
            # Normalizar slashes para asegurar compatibilidad
            image_relative_path = image_relative_path.replace('\\', '/')
            
            movie.image = image_relative_path
            movie.save()
            
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f"Updated image path for: {movie.title}"))

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies with local images."))
