import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Asigna la imagen correspondiente desde media/movie/images/ a cada película en la base de datos"

    def handle(self, *args, **kwargs):
        # 📂 Ruta de la carpeta de imágenes
        images_folder = os.path.join('media', 'movie', 'images')

        # ✅ Verificar si la carpeta existe
        if not os.path.exists(images_folder):
            self.stderr.write(f"La carpeta '{images_folder}' no existe.")
            return

        # 📋 Obtener la lista de archivos existentes en la carpeta
        existing_files = os.listdir(images_folder)
        self.stdout.write(f"Se encontraron {len(existing_files)} archivos en '{images_folder}'.")

        # 🎬 Obtener todas las películas de la base de datos
        movies = Movie.objects.all()
        self.stdout.write(f"Procesando {movies.count()} películas desde la base de datos...\n")

        updated_count = 0
        not_found_count = 0

        for movie in movies:
            # 🧼 Saneamiento del título (mismo formato usado al guardar las imágenes)
            safe_title = "".join(c for c in movie.title if c.isalnum() or c in (' ', '_', '-')).strip()
            
            # Nombre esperado del archivo
            expected_filename = f"m_{safe_title}.png"
            full_path = os.path.join(images_folder, expected_filename)

            # Si el archivo exacto existe
            if os.path.exists(full_path):
                relative_db_path = os.path.join('movie/images', expected_filename)
                movie.image = relative_db_path
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Actualizada: '{movie.title}' -> {relative_db_path}"))
            else:
                # 🔍 Búsqueda flexible por si el archivo no tiene el prefijo 'm_' o usa otra extensión (.jpg, .png)
                matched_file = None
                for file in existing_files:
                    if safe_title.lower() in file.lower():
                        matched_file = file
                        break

                if matched_file:
                    relative_db_path = os.path.join('movie/images', matched_file)
                    movie.image = relative_db_path
                    movie.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✔ Coincidencia encontrada: '{movie.title}' -> {relative_db_path}"))
                else:
                    not_found_count += 1
                    self.stderr.write(f"✖ No se encontró imagen para: '{movie.title}' (Esperado: {expected_filename})")

        self.stdout.write(self.style.SUCCESS(
            f"\nProceso finalizado: {updated_count} películas actualizadas, {not_found_count} sin imagen encontrada."
        ))