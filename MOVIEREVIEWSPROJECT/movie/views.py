from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Movie
def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'name': 'Andres Eusse', 'searchTerm': searchTerm, 'movies': movies})

def about(request):
    return render(request, 'about.html')

import matplotlib
import matplotlib.pyplot as plt
import io
import urllib, base64

matplotlib.use('Agg')

def statistics(request):
    movies = Movie.objects.all()
    
    # Chart 1: Movies by Year
    years_count = {}
    for movie in movies:
        year = str(movie.year) if movie.year else "None"
        if year in years_count:
            years_count[year] += 1
        else:
            years_count[year] = 1
            
    fig1, ax1 = plt.subplots()
    ax1.bar(years_count.keys(), years_count.values())
    ax1.set_title("Movies by Year")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Movies")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    string1 = base64.b64encode(buf1.read())
    uri1 = 'data:image/png;base64,' + urllib.parse.quote(string1)
    plt.close(fig1)
    
    # Chart 2: Movies by Genre (first genre)
    genres_count = {}
    for movie in movies:
        if movie.genre:
            first_genre = movie.genre.split(',')[0].strip()
        else:
            first_genre = "None"
            
        if first_genre in genres_count:
            genres_count[first_genre] += 1
        else:
            genres_count[first_genre] = 1

    fig2, ax2 = plt.subplots()
    ax2.bar(genres_count.keys(), genres_count.values())
    ax2.set_title("Movies by First Genre")
    ax2.set_xlabel("Genre")
    ax2.set_ylabel("Number of Movies")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    string2 = base64.b64encode(buf2.read())
    uri2 = 'data:image/png;base64,' + urllib.parse.quote(string2)
    plt.close(fig2)
    
    return render(request, 'statistics.html', {'graphic1': uri1, 'graphic2': uri2})

from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv
from .models import Movie

def recommendation(request):
    prompt = request.GET.get('prompt')
    best_movie = None
    max_similarity = -1

    if prompt:
        # Usamos try-except para manejar el error 429 por falta de saldo
        try:
            load_dotenv('../openAI.env')
            client = OpenAI(api_key=os.environ.get('openai_apikey', ''))

            response = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
        except Exception:
            # Fake embedding if quota fails
            prompt_emb = np.random.rand(1536).astype(np.float32)

        def cosine_similarity(a, b):
            if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
                return 0
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        for movie in Movie.objects.all():
            try:
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                similarity = cosine_similarity(prompt_emb, movie_emb)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie
            except Exception:
                pass

    return render(request, 'recommendation.html', {'prompt': prompt, 'best_movie': best_movie})