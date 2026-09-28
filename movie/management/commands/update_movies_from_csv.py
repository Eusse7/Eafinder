import os
import csv

from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):

    help = "Update movie descriptions in the database from a CSV file"

    def handle(self, *args, **kwargs):

        csv_file = "C:\\Users\\hyesi\\OneDrive\\Desktop\\QUINTO SEMESTRE\\proyecto_integrador\\semana4\\taller02\\moviereviewsproject\\movie\\management\\commands\\updated_movie_descriptions.csv"

        if not os.path.exists(csv_file):
            self.stderr.write(
                f"CSV file '{csv_file}' not found."
            )
            return

        updated_count = 0

        with open(csv_file, mode="r", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                title = row["Title"]
                new_description = row["Updated Description"]

                try:

                    movie = Movie.objects.get(title=title)

                    movie.description = new_description
                    movie.save()

                    updated_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated: {title}"
                        )
                    )

                except Movie.DoesNotExist:

                    self.stderr.write(
                        f"Movie not found: {title}"
                    )

                except Exception as e:

                    self.stderr.write(
                        f"Failed to update {title}: {str(e)}"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished updating {updated_count} movies from CSV."
            )
        )