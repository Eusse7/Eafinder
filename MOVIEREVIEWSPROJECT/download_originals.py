import os
import requests
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereviews.settings')
django.setup()

from movie.models import Movie

movies_urls = {
    "Crepúsculo": "https://m.media-amazon.com/images/M/MV5BMTQ2NzUxMTAxN15BMl5BanBnXkFtZTcwMzEyMTIwMg@@._V1_.jpg",
    "Yo antes de ti": "https://m.media-amazon.com/images/M/MV5BMTQ2NjE4NDE2NV5BMl5BanBnXkFtZTgwOTcwNDE5NzE@._V1_.jpg",
    "Enola Holmes": "https://m.media-amazon.com/images/M/MV5BZjNkNzk0ZjEtM2M1ZC00MmMxLTlmOWMtNjg0YzhhOWExNjNlXkEyXkFqcGc@._V1_.jpg",
    "Violet y Finch": "https://m.media-amazon.com/images/M/MV5BMGUyM2ZiZmUtMWY0ZC00NTIzLWI4ZjMtZTJiNzQ3Yjk3ZTlhXkEyXkFqcGc@._V1_.jpg",
    "El llamado salvaje": "https://m.media-amazon.com/images/M/MV5BZDA1ZmQ2OGMtZDhkMC00ZjRkLWE3ZTMtMzcwYWZhNGJiNmI3XkEyXkFqcGc@._V1_.jpg",
    "Demon slayer": "https://m.media-amazon.com/images/M/MV5BODI2NjdlYWItMTE1ZC00YzI2LTg0YjYtNjdhZTIxNmYwMWExXkEyXkFqcGc@._V1_.jpg",
    "Son como niños 2": "https://m.media-amazon.com/images/M/MV5BMTQ4NTI0NjI0OF5BMl5BanBnXkFtZTcwMjE0Njk4OQ@@._V1_.jpg",
    "Spider-Man Un nuevo dia": "https://m.media-amazon.com/images/M/MV5BZDEyN2NhMjgtMjdhNi00MmNlLWE5YTgtZGE4MzNjMTRlMGEwXkEyXkFqcGdeQXVyNDUyOTg3Njg@._V1_.jpg",
    "Avengers Endgame": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_.jpg"
}

movies = Movie.objects.all()
images_folder = os.path.join('media', 'movie', 'images')
os.makedirs(images_folder, exist_ok=True)

for m in movies:
    if m.title in movies_urls:
        print(f"Downloading {m.title}...")
        try:
            r = requests.get(movies_urls[m.title], stream=True)
            if r.status_code == 200:
                safe_title = "".join(c for c in m.title if c.isalnum() or c in (' ', '_', '-')).strip()
                filename = f"orig_{safe_title}.jpg"
                file_path = os.path.join(images_folder, filename)
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                m.image = f"movie/images/{filename}"
                m.save()
                print(f"Successfully updated {m.title}")
            else:
                print(f"Failed to download {m.title}, status: {r.status_code}")
        except Exception as e:
            print(f"Error for {m.title}: {e}")
    else:
        # Keep Ice Age as is since it already has the correct image
        print(f"Skipping {m.title}")

print("Done!")
