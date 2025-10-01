import os
from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing
from borrowings.notifications.telegram import (
    send_telegram_notification,
    TELEGRAM_API_URL
)
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer
)

BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse(
        "borrowings:borrowing-return",
        args=[borrowing_id]
    )


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.book1 = Book.objects.create(
            title="test_title1",
            author="test_author1",
            cover="HD",
            inventory=1,
            daily_fee=12.23,
        )
        self.book2 = Book.objects.create(
            title="test_title2",
            author="test_author2",
            cover="HD",
            inventory=2,
            daily_fee=22.23,
        )

        self.borrowing1 = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book1,
            user=self.user,
        )
        self.borrowing2 = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=1),
            book=self.book2,
            user=self.user,
        )

    def test_list_borrowings(self):
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(borrowings.count(), 2)

    def test_retrieve_borrowing_detail(self):
        url = detail_url(self.borrowing1.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(self.borrowing1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        payload = {
            "expected_return_date": date.today() + timedelta(days=2),
            "book": self.book2.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_borrowings_by_is_active(self):
        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer1 = BorrowingListSerializer(self.borrowing1)
        serializer2 = BorrowingListSerializer(self.borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            "test_admin@admin.com", "testpass", is_staff=True
        )
        self.non_admin_user = get_user_model().objects.create_user(
            "test_non_admin@non_admin.com", "testpass", is_staff=False
        )
        self.client.force_authenticate(self.admin_user)

        self.book1 = Book.objects.create(
            title="test_title1",
            author="test_author1",
            cover="HD",
            inventory=1,
            daily_fee=12.23,
        )
        self.book2 = Book.objects.create(
            title="test_title2",
            author="test_author2",
            cover="HD",
            inventory=2,
            daily_fee=22.23,
        )

        self.borrowing1 = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book1,
            user=self.admin_user,
        )
        self.borrowing2 = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=1),
            book=self.book2,
            user=self.non_admin_user,
        )

    def test_list_borrowings_all_users(self):
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(serializer.data, res.data)
        self.assertEqual(len(res.data), 2)

    def test_filter_borrowings_by_user_id(self):
        res = self.client.get(
            BORROWING_URL,
            {"user_id": self.non_admin_user.id}
        )

        serializer1 = BorrowingListSerializer(self.borrowing1)
        serializer2 = BorrowingListSerializer(self.borrowing2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)


class TelegramSendingNotificationTests(TestCase):
    @patch.dict(os.environ,
                {"TELEGRAM_BOT_TOKEN": "TEST_BOT_TOKEN",
                 "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID")})
    @patch("requests.post")
    def test_sending_notification_about_new_borrowing(self, mock_post):

        message = "Test message notification"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_telegram_notification(message=message)

        mock_post.assert_called_once()

        expected_payload = {
            "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            "text": message,
            "parse_mode": "HTML",
        }

        mock_post.assert_called_with(
            TELEGRAM_API_URL,
            data=expected_payload
        )

        self.assertEqual(mock_response.status_code, status.HTTP_200_OK)
