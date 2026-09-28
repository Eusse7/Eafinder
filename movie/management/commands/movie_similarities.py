import os
import numpy as np

from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv
from google import genai


class Command(BaseCommand):
    help = "Calculate movie similarities using Gemini embeddings"

    def handle(self, *args, **kwargs):

        # Cargar variables del archivo .env
        load_dotenv()

        api_key = os.getenv("gemini_api")

        if not api_key:
            self.stderr.write(
                self.style.ERROR(
                    "No se encontró 'gemini_api' en el archivo .env"
                )
            )
            return

        # Crear cliente de Gemini
        client = genai.Client(api_key=api_key)

        # ==========================================
        # SELECCIONAR LAS PELÍCULAS
        # ==========================================

        movie1 = Movie.objects.get(title="Interestelar")
        movie2 = Movie.objects.get(title="Project Hail Mary")

        self.stdout.write("")
        self.stdout.write("🎬 Películas seleccionadas:")
        self.stdout.write(f"1. {movie1.title}")
        self.stdout.write(f"2. {movie2.title}")

        # ==========================================
        # FUNCIÓN PARA GENERAR EMBEDDINGS
        # ==========================================

        def get_embedding(text):

            result = client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )

            return np.array(
                result.embeddings[0].values,
                dtype=np.float32
            )

        # ==========================================
        # SIMILITUD DE COSENO
        # ==========================================

        def cosine_similarity(a, b):

            denominator = (
                np.linalg.norm(a) *
                np.linalg.norm(b)
            )

            if denominator == 0:
                return 0.0

            return np.dot(a, b) / denominator

        # ==========================================
        # GENERAR EMBEDDINGS DE LAS PELÍCULAS
        # ==========================================

        self.stdout.write("")
        self.stdout.write(
            "Generando embeddings..."
        )

        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)

        self.stdout.write(
            "Embeddings generados correctamente."
        )

        # ==========================================
        # COMPARAR LAS DOS PELÍCULAS
        # ==========================================

        similarity = cosine_similarity(
            emb1,
            emb2
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"🎬 {movie1.title} vs "
                f"{movie2.title}: {similarity:.4f}"
            )
        )

        # ==========================================
        # PROMPT DE BÚSQUEDA
        # ==========================================

        prompt = (
            "película de ciencia ficción sobre "
            "viajes espaciales y supervivencia"
        )

        self.stdout.write("")
        self.stdout.write(
            f"📝 Prompt: {prompt}"
        )

        # Generar embedding del prompt
        prompt_emb = get_embedding(prompt)

        # ==========================================
        # COMPARAR PROMPT VS PELÍCULAS
        # ==========================================

        sim_prompt_movie1 = cosine_similarity(
            prompt_emb,
            emb1
        )

        sim_prompt_movie2 = cosine_similarity(
            prompt_emb,
            emb2
        )

        self.stdout.write("")

        self.stdout.write(
            f"📝 Similitud prompt vs "
            f"'{movie1.title}': "
            f"{sim_prompt_movie1:.4f}"
        )

        self.stdout.write(
            f"📝 Similitud prompt vs "
            f"'{movie2.title}': "
            f"{sim_prompt_movie2:.4f}"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "✅ Proceso de similitud terminado."
            )
        )