from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    # return HttpResponse("<h1>Welcome to the Movie Reviews Home Page!</h1>")
    return render(request, 'home.html', {'name':'Greg Lim'})

def about(request):
    return HttpResponse("<h1>About Movie Reviews</h1><p>This is a platform to share and read movie reviews.</p>")