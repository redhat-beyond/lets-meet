from django.db import models


class Event(models.Model):

    class Colors(models.TextChoices):
        RED = "#FF0000", "Red"
        PINK = "#FFC0CB", "Pink"
        ORANGE = "#FFA500", "Orange"
        YELLOW = "#FFFF00", "Yellow"
        PURPLE = "#800080", "Purple"
        GREEN = "#008000", "Green"
        BLUE = "#0000FF", "Blue"
        BROWN = "#A52A2A", "Brown"
        WHITE = "#FFFFFF", "White"
        GRAY = "#808080", "Gray"
        BLACK = "#000000", "Black"

    title = models.CharField(max_length=50)
    location = models.CharField(blank=True, max_length=50)
    description = models.TextField(blank=True)
    date_time_start = models.DateTimeField(null=True, blank=True)
    date_time_end = models.DateTimeField(null=True, blank=True)
    color = models.CharField(
        max_length=7,
        choices=Colors.choices,
        default=Colors.BLACK,
    )

    def __str__(self) -> str:
        return f"{self.title} - {self.date_time_start}"
