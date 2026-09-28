from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import os
import numpy as np

from dotenv import load_dotenv
from google import genai
from google.genai import types
from movie.models import Movie
# Create your views here.

def home(request):
   # return HttpResponse('<h1> Welcome to my page </h1>')
   # return render(request, 'home.html')
   #return render(request, 'home.html', {'name': 'Yesid Hurtado Montoya'})
    searchTerm = request.GET.get('searchMovie')

    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()

    return render(
        request,
        'home.html',
        {
            'searchTerm': searchTerm,
            'movies': movies
        }
    )


def statistics_view(request):
    matplotlib.use('Agg')
    # Gráfica de películas por año
    all_movies = Movie.objects.all()
    movie_counts_by_year = {}
    for movie in all_movies:
        print(movie.genre)
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    year_graphic = generate_bar_chart(movie_counts_by_year, 'Year', 'Number of movies')

    # Gráfica de películas por género
    movie_counts_by_genre = {}
    for movie in all_movies:
        # Obtener el primer género
        genres = movie.genre.split(',')[0].strip() if movie.genre else "None"
        if genres in movie_counts_by_genre:
            movie_counts_by_genre[genres] += 1
        else:
            movie_counts_by_genre[genres] = 1

    genre_graphic = generate_bar_chart(movie_counts_by_genre, 'Genre', 'Number of movies')

    return render(request, 'statistics.html', {'year_graphic': year_graphic, 'genre_graphic': genre_graphic})

def generate_bar_chart(data, xlabel, ylabel):
    keys = [str(key) for key in data.keys()]
    plt.bar(keys, data.values())
    plt.title('Movies Distribution')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return graphic

def about(request):
   return render(request, 'about.html', {'name': 'Yesid Hurtado Montoya'})

def signup(request):
    email = request.GET.get('email') 
    return render(request, 'signup.html', {'email':email})

def movie_recommendation(request):

    recommendation = None
    similarity_value = None
    prompt = ""

    if request.method == "POST":

        prompt = request.POST.get("prompt", "").strip()

        if prompt:

            load_dotenv()

            api_key = os.getenv("gemini_api")

            client = genai.Client(api_key=api_key)

            # Generar embedding del texto escrito por el usuario
            result = client.models.embed_content(
                model="gemini-embedding-2",
                contents=prompt,
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )

            prompt_emb = np.array(
                result.embeddings[0].values,
                dtype=np.float32
            )

            # Función para calcular similitud coseno
            def cosine_similarity(a, b):

                denominator = (
                    np.linalg.norm(a) *
                    np.linalg.norm(b)
                )

                if denominator == 0:
                    return 0.0

                return np.dot(a, b) / denominator

            best_movie = None
            max_similarity = -1

            # Comparar contra todas las películas
            for movie in Movie.objects.all():

                if not movie.emb:
                    continue

                movie_emb = np.frombuffer(
                    movie.emb,
                    dtype=np.float32
                )

                # Evitar comparar embeddings de dimensiones diferentes
                if len(movie_emb) != len(prompt_emb):
                    continue

                similarity = cosine_similarity(
                    prompt_emb,
                    movie_emb
                )

                if similarity > max_similarity:

                    max_similarity = similarity
                    best_movie = movie

            recommendation = best_movie
            similarity_value = max_similarity

    return render(
        request,
        "recommendation.html",
        {
            "recommendation": recommendation,
            "similarity": similarity_value,
            "prompt": prompt,
        }
    )