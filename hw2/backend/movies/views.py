import base64
import io
import urllib

import matplotlib
import matplotlib.pyplot as plt

from django.shortcuts import render
from .models import Movie
from django.http import HttpResponse

from . import models

# Create your views here.
def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = models.Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = models.Movie.objects.all()

    context = {
        'searchItem' : searchTerm,
        'movies'     : movies,
    }

    return render(request, 'movies/home.html', context)

def statistics_view(request):
    matplotlib.use('Agg')

    # Obtener todas las películas
    all_movies = Movie.objects.all()

    # --- Gráfica por año ---
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))

    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    # --- Gráfica por género (solo el primer género) ---
    movie_counts_by_genre = {}
    for movie in all_movies:
        if movie.genre:
            first_genre = movie.genre.split(',')[0].strip()
        else:
            first_genre = "None"
        movie_counts_by_genre[first_genre] = movie_counts_by_genre.get(first_genre, 0) + 1

    bar_positions_genre = range(len(movie_counts_by_genre))

    plt.bar(bar_positions_genre, movie_counts_by_genre.values(), width=bar_width, align='center', color='green')
    plt.title('Movies per genre (first only)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions_genre, movie_counts_by_genre.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()

    image_png_genre = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_png_genre)
    graphic_genre = graphic_genre.decode('utf-8')

    return render(request, 'movies/statistics.html', {
        'graphic': graphic,
        'graphic_genre': graphic_genre,
    })