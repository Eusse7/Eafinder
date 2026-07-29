from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    # return HttpResponse('<h1>Bienvenido a la página de inicio de Movie Reviews</h1>')
    return render(request, 'home.html', {'name':'Juan García'})

def about(request):
    return HttpResponse('<h1>Acerca de Movie Reviews</h1><p>Esta es una aplicación para revisar películas.</p>')