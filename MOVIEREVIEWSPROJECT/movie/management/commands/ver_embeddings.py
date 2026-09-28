import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
	help = "Visualize the embedding of a randomly selected movie"

	def handle(self, *args, **kwargs):
		movie = Movie.objects.order_by('?').first()

		if movie is None:
			self.stderr.write(self.style.ERROR("No hay películas en la base de datos."))
			return

		if not movie.emb:
			self.stderr.write(
				self.style.ERROR(f"La película '{movie.title}' no tiene embedding almacenado.")
			)
			return

		embedding = np.frombuffer(movie.emb, dtype=np.float32)

		self.stdout.write(self.style.SUCCESS("Embedding seleccionado al azar"))
		self.stdout.write(f"Película: {movie.title}")
		self.stdout.write(f"Dimensiones: {embedding.size}")
		self.stdout.write(f"Primeros 20 valores: {embedding[:20]}")
		self.stdout.write(f"Últimos 5 valores: {embedding[-5:]}")
