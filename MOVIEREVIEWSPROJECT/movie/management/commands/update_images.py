import os
from pathlib import Path
from PIL import Image
from huggingface_hub import InferenceClient
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate images using Hugging Face official client"

    def handle(self, *args, **kwargs):
        # ✅ Construye la ruta absoluta hacia gemini.env si está en la raíz del proyecto
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_path = base_dir / 'gemini.env'
        
        # Carga las variables
        load_dotenv(env_path)

        hf_token = os.environ.get('HF_TOKEN')
        if not hf_token:
            self.stderr.write("HF_TOKEN no encontrada en las variables de entorno.")
            return

        # ✅ Cliente oficial de Hugging Face
        client = InferenceClient(token=hf_token)

        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        movies = Movie.objects.all()[:10] # Limitar a las primeras 10 películas para pruebas
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                prompt = f"Movie poster of {movie.title}, highly detailed, cinematic"
                
                # ✅ Generación de imagen con el cliente oficial
                image = client.text_to_image(
                    prompt,
                    model="black-forest-labs/FLUX.1-schnell"
                )

                safe_title = "".join(c for c in movie.title if c.isalnum() or c in (' ', '_', '-')).strip()
                image_filename = f"m_{safe_title}.png"
                image_path_full = os.path.join(images_folder, image_filename)

                # ✅ Guardar directamente el objeto de imagen
                image.save(image_path_full)

                # ✅ Actualizar en la base de datos
                movie.image = os.path.join('movie/images', image_filename)
                movie.save()

                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))

            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            