import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereviews.settings')
django.setup()

from movie.models import Movie

movies = Movie.objects.all()
for m in movies:
    safe_title = "".join(c for c in m.title if c.isalnum() or c in (' ', '_', '-')).strip()
    image_filename = f"m_{safe_title}.png"
    image_path = os.path.join('media', 'movie', 'images', image_filename)
    if os.path.exists(image_path):
        m.image = f'movie/images/{image_filename}'
        m.save()
        print(f"Restored image for {m.title}")
