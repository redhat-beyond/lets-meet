from django.db import models
from django.core.exceptions import ValidationError


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

    def clean(self):
        if ((self.date_time_end is None and self.date_time_start is not None)
           or (self.date_time_start is None and self.date_time_end is not None)):
            raise ValidationError('start and end date_time - one field not filled')

        if (self.date_time_start is not None and self.date_time_end is not None
           and self.date_time_start >= self.date_time_end):
            raise ValidationError('date_time_start is equal or greater than date_time_end')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} - {self.date_time_start}"
