from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    return render(request, 'home.html', {"name" : "Juan Jimenez Cardona"})

def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, "about.html")
