from django.shortcuts import render
from django.http import HttpResponse

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

from .models import Movie

# Create your views here.

def home(request):
    # return HttpResponse('<h1>Bienvenido a la página de inicio de Movie Reviews</h1>')
    # return render(request, 'home.html', {'name':'Juan García'})
    searchTerm = request.GET.get('searchMovie')
    
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    return render(request, 'home.html', {'name': 'Juan Garcia', 'searchTerm': searchTerm, 'movies': movies})

def about(request):
    # return HttpResponse('<h1>Acerca de Movie Reviews</h1><p>Esta es una aplicación para revisar películas.</p>')
    return render(request, 'about.html')

def get_graphic(counts, title, xlabel, ylabel):
    # Ancho de las barras
    bar_width = 0.5
    # Posiciones de las barras
    bar_positions = range(len(counts))

    # Crear la gráfica de barras
    plt.bar(bar_positions, counts.values(), width=bar_width, align='center')

    # Personalizar la gráfica
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(bar_positions, counts.keys(), rotation=90)

    # Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    return graphic.decode('utf-8')

def statistics_view(request):
    matplotlib.use('Agg')
    # Obtener todas las películas
    all_movies = Movie.objects.all()

    # Crear un diccionario para almacenar la cantidad de películas por año
    movie_counts_by_year = {}
    # Filtrar las películas por año y contar la cantidad de películas por año
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    # Crear un diccionario para almacenar la cantidad de películas por género
    movie_counts_by_genre = {}
    # Contar la cantidad de películas por género (solo el primer género de cada película)
    for movie in all_movies:
        if movie.genre:
            genre = movie.genre.split(',')[0].strip()
        else:
            genre = "None"
        if genre in movie_counts_by_genre:
            movie_counts_by_genre[genre] += 1
        else:
            movie_counts_by_genre[genre] = 1

    # Generar las gráficas en base64
    graphic_year = get_graphic(movie_counts_by_year, 'Movies per year', 'Year', 'Number of movies')
    graphic_genre = get_graphic(movie_counts_by_genre, 'Movies per genre', 'Genre', 'Number of movies')

    # Renderizar la plantilla statistics.html con las gráficas
    return render(request, 'statistics.html', {
        'graphic_year': graphic_year,
        'graphic_genre': graphic_genre,
    })
