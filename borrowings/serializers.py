from django.utils import timezone

from django.db import transaction
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.notifications.telegram import send_telegram_notification


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        if attrs["book"].inventory <= 0:
            raise serializers.ValidationError(
                {
                    "book": "Book's inventory <= 0"
                }
            )
        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            user = self.context["request"].user

            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(
                user=user,
                book=book,
                expected_return_date=validated_data["expected_return_date"],
            )

            message = (
                f"New Book Borrowing\n\n"
                f"User: {user.email}\n"
                f"Book: {book.title}\n"
                f"Borrowed On: {borrowing.borrow_date}\n"
                f"Return By: {borrowing.expected_return_date}"
            )

            send_telegram_notification(message=message)

            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date:
            raise serializers.ValidationError(
                {
                    "actual_return_date":
                        "This borrowing has already been returned"
                }
            )
        return attrs

    def save(self, **kwargs):
        with transaction.atomic():
            borrowing = self.instance
            book = borrowing.book

            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            book.inventory += 1
            book.save()

            return borrowing
