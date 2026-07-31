from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    # return HttpResponse("<h1>Welcome to the Movie Reviews Home Page!</h1>")
    return render(request, 'home.html', {'name':'Jhon Jairo Pulgarin'})

def about(request):
    return render(request, 'about.html')