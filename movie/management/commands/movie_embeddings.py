import os
import time
import numpy as np

from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv
from google import genai
from google.genai import types


class Command(BaseCommand):
    help = "Generate and store Gemini embeddings for all movies"

    def handle(self, *args, **kwargs):

        # ==========================================
        # CARGAR API KEY
        # ==========================================

        load_dotenv()

        api_key = os.getenv("gemini_api")

        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "No se encontró 'gemini_api' en el archivo .env"
                )
            )
            return

        # ==========================================
        # CREAR CLIENTE GEMINI
        # ==========================================

        client = genai.Client(api_key=api_key)

        movies = Movie.objects.all()

        self.stdout.write(
            f"Found {movies.count()} movies in the database"
        )

        updated_count = 0

        # ==========================================
        # RECORRER PELÍCULAS
        # ==========================================

        for movie in movies:

            if not movie.description:
                self.stderr.write(
                    f"Movie without description: {movie.title}"
                )
                continue

            try:

                self.stdout.write(
                    f"Generating embedding for: {movie.title}"
                )

                # ==================================
                # GENERAR EMBEDDING CON GEMINI
                # ==================================

                result = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=movie.description,
                    config=types.EmbedContentConfig(
                        output_dimensionality=768
                    )
                )

                embedding = np.array(
                    result.embeddings[0].values,
                    dtype=np.float32
                )

                # ==================================
                # CONVERTIR A BINARIO
                # ==================================

                movie.emb = embedding.tobytes()

                # ==================================
                # GUARDAR EN LA BASE DE DATOS
                # ==================================

                movie.save(
                    update_fields=["emb"]
                )

                updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"👌 Embedding stored for: {movie.title}"
                    )
                )

                # Pequeña pausa para evitar demasiadas
                # solicitudes seguidas
                time.sleep(0.5)

            except Exception as e:

                self.stderr.write(
                    self.style.ERROR(
                        f"Failed for {movie.title}: {str(e)}"
                    )
                )

        # ==========================================
        # RESULTADO FINAL
        # ==========================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"🌟 Finished generating embeddings. "
                f"{updated_count} movies updated."
            )
        )