"""
Modelos de la aplicación movie.
"""
from django.db import models

# Create your models here.


class Movie(models.Model):
    """
    Modelo para representar una película en el sistema.
    """
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='movie/images/')
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)
    