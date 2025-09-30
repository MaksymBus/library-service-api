from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, related_name="borrowings", on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), related_name="borrowings", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"User:{self.user.email} (book:{self.book.title}, borrow_date:{self.borrow_date}"

    def clean(self):
        if self.expected_return_date <= timezone.now().date():
            raise ValidationError(
                {
                    "expected_return_date": "Expected return date must be before the borrow date"
                }
            )
        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError(
                {
                    "actual_return_date": "Actual return date must be before the borrow date"
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
