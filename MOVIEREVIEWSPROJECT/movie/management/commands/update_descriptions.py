import os
from pathlib import Path
from google import genai
from google.genai import types
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Update movie descriptions using Gemini API"

    def handle(self, *args, **kwargs):
        # ✅ Construye la ruta absoluta hacia gemini.env si está en la raíz del proyecto
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_path = base_dir / 'gemini.env'
        
        # Carga las variables
        load_dotenv(env_path)

        # ✅ Inicializa el cliente (detecta GEMINI_API_KEY automáticamente desde os.environ)
        client = genai.Client()

        # ✅ Helper function to send prompt and get completion from Gemini
        def get_completion(prompt, model="gemini-3.5-flash"):
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                )
            )
            return response.text.strip()

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
            "debe incluir el género de la película y cualquier información adicional que sirva "
            "para crear un sistema de recomendación."
        )

        movies = Movie.objects.all()[:3]
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")
            try:
                prompt = (
                    f"{instruction} "
                    f"Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
                )

                print(f"Title: {movie.title}")
                print(f"Original Description: {movie.description}")

                updated_description = get_completion(prompt)

                print(f"Updated Description: {updated_description}")

                movie.description = updated_description
                movie.save()

                self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))

            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {str(e)}")

            