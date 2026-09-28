from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"), 
    path(
        "recommendation/",
        views.movie_recommendation,
        name="movie_recommendation"
    ), 
]