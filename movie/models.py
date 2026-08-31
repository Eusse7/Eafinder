from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(
        upload_to='movie/images/',
        storage=FileSystemStorage(allow_overwrite=True),
        default='movie/images/default.jpg',
    )
    url = models.URLField(blank=True)
    genre = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title