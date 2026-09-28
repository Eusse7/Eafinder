import numpy as np

from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Show the embedding of a movie"

    def handle(self, *args, **kwargs):

        movie = Movie.objects.order_by("?").first()

        if not movie:
            self.stderr.write(
                self.style.ERROR(
                    "No hay películas en la base de datos."
                )
            )
            return

        if not movie.emb:
            self.stderr.write(
                self.style.ERROR(
                    f"La película '{movie.title}' "
                    "no tiene embedding."
                )
            )
            return

        embedding_vector = np.frombuffer(
            movie.emb,
            dtype=np.float32
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"🎬 Película: {movie.title}"
            )
        )

        self.stdout.write(
            f"📐 Dimensiones: {len(embedding_vector)}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Primeros 10 valores del embedding:"
        )

        self.stdout.write(
            str(embedding_vector[:10])
        )

        self.stdout.write("")