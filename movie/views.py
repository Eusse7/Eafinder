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