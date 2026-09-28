import os
import time

from google import genai

from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):

    help = "Update the first movie description using Gemini API"

    def handle(self, *args, **kwargs):

        # Cargar variables desde .env
        load_dotenv()

        # Obtener API Key
        api_key = os.getenv("gemini_api")

        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "No se encontró gemini_api en el archivo .env"
                )
            )
            return

        # Crear cliente de Gemini
        client = genai.Client(api_key=api_key)

        # Obtener solamente la primera película
        movie = Movie.objects.first()

        if not movie:
            self.stderr.write(
                self.style.ERROR("No hay películas en la base de datos.")
            )
            return

        self.stdout.write(
            f"Processing: {movie.title}"
        )

        self.stdout.write(
            f"Original Description: {movie.description}"
        )

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir "
            "de forma clara, concisa y precisa cualquier película en menos "
            "de 200 palabras. La descripción debe incluir el género de la "
            "película y cualquier información adicional que sirva para "
            "crear un sistema de recomendación."
        )

        prompt = (
            f"{instruction}\n\n"
            f"Título de la película: {movie.title}\n"
            f"Descripción actual: {movie.description}\n\n"
            "Escribe una nueva descripción mejorada. "
            "Devuelve únicamente la descripción, sin explicaciones adicionales. En texto plano, sin formato HTML ni Markdown."
        )

        # Intentar hasta 3 veces si Gemini está temporalmente ocupado
        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                updated_description = response.text.strip()

                # Reemplazar la descripción
                movie.description = updated_description
                movie.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Description updated successfully: {movie.title}"
                    )
                )

                self.stdout.write(
                    f"New Description: {updated_description}"
                )

                return

            except Exception as e:

                self.stderr.write(
                    f"Attempt {attempt + 1}/3 failed: {str(e)}"
                )

                if attempt < 2:
                    self.stdout.write(
                        "Retrying in 5 seconds..."
                    )
                    time.sleep(5)

        self.stderr.write(
            self.style.ERROR(
                f"Could not update {movie.title}"
            )
        )