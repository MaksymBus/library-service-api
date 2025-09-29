from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    class Cover(models.TextChoices):
        HARD = "HD", "HARD"
        SOFT = "ST", "SOFT"

    cover = models.CharField(max_length=2, choices=Cover.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return f"{self.title}, {self.author}"
