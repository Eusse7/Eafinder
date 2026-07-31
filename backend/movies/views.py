from django.shortcuts import render
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