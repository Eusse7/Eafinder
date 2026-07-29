from django.shortcuts import render
from django.http import HttpResponse

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

    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})

def about(request):
    # return HttpResponse('<h1>Acerca de Movie Reviews</h1><p>Esta es una aplicación para revisar películas.</p>')
    return render(request, 'about.html')