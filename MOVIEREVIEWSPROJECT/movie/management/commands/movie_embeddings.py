import os
from pathlib import Path
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from google import genai
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_path = base_dir / 'gemini.env'
        load_dotenv(env_path)

        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('gemini_apikey')
        client = genai.Client(api_key=api_key)

        # ✅ Fetch all movies from the database
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        def get_embedding(text):
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            return np.array(response.embeddings[0].values, dtype=np.float32)

        # ✅ Iterate through movies and generate embeddings
        for movie in movies:
            try:
                emb = get_embedding(movie.description)
                # ✅ Store embedding as binary in the database
                movie.emb = emb.tobytes()
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Embedding stored for: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"Failed to generate embedding for {movie.title}: {e}")

        self.stdout.write(self.style.SUCCESS("Finished generating embeddings for all movies"))