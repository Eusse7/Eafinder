import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
import random

class Command(BaseCommand):
    help = "Visualizar los embeddings de una película seleccionada al azar"

    def handle(self, *args, **kwargs):
        movies = list(Movie.objects.all())
        if not movies:
            self.stderr.write("No hay películas en la base de datos.")
            return

        random_movie = random.choice(movies)
        
        # Recuperar el array desde el binario
        embedding_vector = np.frombuffer(random_movie.emb, dtype=np.float32)
        
        self.stdout.write(self.style.SUCCESS(f"Película seleccionada: {random_movie.title}"))
        self.stdout.write("Primeros 10 valores del vector de embedding:")
        self.stdout.write(str(embedding_vector[:10]))
        self.stdout.write(f"Longitud total del vector: {len(embedding_vector)}")
