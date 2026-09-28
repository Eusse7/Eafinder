import os
import requests

from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate images with Pollinations for the first 10 movies"

    def handle(self, *args, **kwargs):
        # Cargar variables del archivo .env
        load_dotenv()

        api_key = os.getenv("pollinations_api")

        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "No se encontró 'pollinations_api' en el archivo .env"
                )
            )
            return

        # Carpeta donde se guardarán las imágenes
        images_folder = "media/movie/images/"
        os.makedirs(images_folder, exist_ok=True)

        # Obtener solamente las primeras 10 películas
        movies = Movie.objects.all()[:10]

        self.stdout.write(
            f"Se encontraron {movies.count()} películas para procesar."
        )

        generated_count = 0

        for movie in movies:
            self.stdout.write(
                f"Generando imagen para: {movie.title}"
            )

            try:
                image_relative_path = self.generate_and_download_image(
                    api_key,
                    movie.title,
                    images_folder
                )

                # Actualizar la imagen en la base de datos
                movie.image = image_relative_path
                movie.save()

                generated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imagen guardada: {movie.title}"
                    )
                )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Error con {movie.title}: {str(e)}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso terminado. "
                f"{generated_count} de 10 imágenes generadas."
            )
        )

    def generate_and_download_image(
        self,
        api_key,
        movie_title,
        save_folder
    ):
        # Prompt para generar el póster
        prompt = (
            f"Professional cinematic movie poster for the movie "
            f"'{movie_title}', dramatic composition, "
            f"cinematic lighting, high quality, "
            f"professional film poster, no text"
        )

        # Codificar el prompt para utilizarlo en la URL
        encoded_prompt = requests.utils.quote(prompt)

        url = (
            f"https://gen.pollinations.ai/image/"
            f"{encoded_prompt}"
        )

        # Solicitar la imagen
        response = requests.get(
            url,
            params={
                "model": "flux",
                "width": 512,
                "height": 768
            },
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            timeout=120
        )

        response.raise_for_status()

        # Nombre del archivo
        image_filename = f"m_{movie_title}.png"

        # Ruta completa donde se guardará
        image_path = os.path.join(
            save_folder,
            image_filename
        )

        # Guardar la imagen
        with open(image_path, "wb") as file:
            file.write(response.content)

        # Esta es la ruta que Django guarda en ImageField
        return os.path.join(
            "movie",
            "images",
            image_filename
        )