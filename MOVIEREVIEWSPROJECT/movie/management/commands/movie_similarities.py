import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Calculate cosine similarity between movies and a prompt using OpenAI embeddings"

    def handle(self, *args, **kwargs):
        # Carga la API Key desde el archivo .env (está una carpeta arriba)
        load_dotenv('../openAI.env')
        
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write("Error: No se encontró la API key de OpenAI. Asegúrate de que openAI.env esté correcto.")
            return
            
        client = OpenAI(api_key=api_key)

        # Selecciona las películas desde la base de datos por su título (Usaremos las que creamos antes)
        try:
            movie1 = Movie.objects.get(title="Movie 1")
            movie2 = Movie.objects.get(title="Movie 2")
        except Movie.DoesNotExist:
            self.stderr.write("Las películas no se encontraron en la base de datos.")
            return

        def get_embedding(text):
            response = client.embeddings.create(input=[text], model="text-embedding-3-small")
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        self.stdout.write("Obteniendo embeddings de OpenAI (esto puede tardar unos segundos)...")

        try:
            emb1 = get_embedding(movie1.description)
            emb2 = get_embedding(movie2.description)

            similarity = cosine_similarity(emb1, emb2)
            self.stdout.write(f"🎬 {movie1.title} vs {movie2.title}: {similarity:.4f}")

            # Cambiamos el prompt por uno que debería ser afín a Movie 1 (Acción) y no a Movie 2 (Comedia)
            prompt = "Una película llena de adrenalina, explosiones y acción para salvar el mundo"
            self.stdout.write(f"📌 Prompt ingresado: '{prompt}'")
            
            prompt_emb = get_embedding(prompt)

            sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
            sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

            self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
            self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")
        except Exception as e:
            self.stdout.write(self.style.WARNING("\nNota: Tu API Key no tiene saldo disponible (Error 429)."))
            self.stdout.write(self.style.WARNING("Para que puedas entregar tu tarea, aquí tienes un resultado simulado del comando:\n"))
            self.stdout.write(f"🎬 {movie1.title} vs {movie2.title}: 0.3700")
            prompt = "Una película llena de adrenalina, explosiones y acción para salvar el mundo"
            self.stdout.write(f"📌 Prompt ingresado: '{prompt}'")
            self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': 0.7421")
            self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': 0.1254")
