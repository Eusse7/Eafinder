from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def about(request):
    return HttpResponse('<h1>Welcome to About Page</h1>')

def home(request):
    context = {
        'name': 'Sebastian Villegas',
    }
    return render(request, 'homepage/home.html', context)