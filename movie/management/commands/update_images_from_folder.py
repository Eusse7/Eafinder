import os

from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie images from the media/movie/images/ folder"

    def handle(self, *args, **kwargs):
        images_folder = "media/movie/images/"

        # Verificar que la carpeta exista
        if not os.path.exists(images_folder):
            self.stderr.write(
                self.style.ERROR(
                    f"La carpeta '{images_folder}' no existe."
                )
            )
            return

        movies = Movie.objects.all()

        self.stdout.write(
            f"Se encontraron {movies.count()} películas."
        )

        updated_count = 0
        not_found_count = 0

        for movie in movies:
            image_filename = f"m_{movie.title}.png"
            image_path = os.path.join(images_folder, image_filename)

            # Verificar si existe la imagen
            if os.path.exists(image_path):

                # Ruta que Django guardará en el ImageField
                movie.image = os.path.join(
                    "movie",
                    "images",
                    image_filename
                )

                movie.save()

                updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imagen actualizada: {movie.title}"
                    )
                )

            else:
                not_found_count += 1

                self.stderr.write(
                    f"No se encontró imagen para: {movie.title}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso terminado. "
                f"{updated_count} películas actualizadas."
            )
        )

        if not_found_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"{not_found_count} películas no tienen imagen."
                )
            )