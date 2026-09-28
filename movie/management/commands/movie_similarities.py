import os
from pathlib import Path
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from google import genai
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using Gemini embeddings"

    def handle(self, *args, **kwargs):
        # ✅ Construye la ruta absoluta hacia gemini.env si está en la raíz del proyecto
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_path = base_dir / 'gemini.env'
        
        # Carga las variables
        load_dotenv(env_path)

        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('gemini_apikey')
        client = genai.Client(api_key=api_key)

        # ✅ Buscar películas en la base de datos
        try:
            movie1 = Movie.objects.get(title="La Odisea")
            movie2 = Movie.objects.get(title="Marty Supreme")
        except Movie.DoesNotExist as e:
            self.stderr.write(f"Película no encontrada: {e}")
            return

        # ✅ Función auxiliar para obtener embeddings con Gemini
        def get_embedding(text):
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            return np.array(response.embeddings[0].values, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        try:
            # ✅ Generar embeddings de ambas películas
            emb1 = get_embedding(movie1.description)
            emb2 = get_embedding(movie2.description)

            # ✅ Calcular similitud del coseno entre películas
            similarity = cosine_similarity(emb1, emb2)
            self.stdout.write(f"🎬 Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

            # ✅ Comparar contra un prompt
            prompt = "película sobre la Segunda Guerra Mundial"
            prompt_emb = get_embedding(prompt)

            sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
            sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

            self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
            self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")

        except Exception as e:
            self.stderr.write(f"Error al generar embeddings: {str(e)}")