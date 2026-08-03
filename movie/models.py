from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250)
    image= models.ImageField(upload_to='movie/images/')
    url = models.URLField(blank=True)
