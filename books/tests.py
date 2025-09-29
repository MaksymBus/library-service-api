from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(books_id):
    return reverse("books:book-detail", args=[books_id])


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def test_list_books(self):
        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        url = detail_url(self.book1.id)
        res = self.client.get(url)

        serializer = BookSerializer(self.book1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "new_title",
            "author": "new_author",
            "cover": "HD",
            "inventory": 2,
            "daily_fee": 22.23,
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_forbidden(self):
        url = detail_url(self.book1.id)
        payload = {
            "title": "update_title",
            "author": "update_author",
            "cover": "HD",
            "inventory": 2,
            "daily_fee": 22.23,
        }
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_forbidden(self):
        url = detail_url(self.book1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBookApiTests(TestCase):
    def setUp(self):
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
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "new_title",
            "author": "new_author",
            "cover": "ST",
            "inventory": 2,
            "daily_fee": 22.23,
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_book(self):
        payload = {
            "title": "update_title",
            "author": "update_author",
            "cover": "ST",
            "inventory": 2,
            "daily_fee": 22.23,
        }

        url = detail_url(self.book1.id)

        res = self.client.put(url, payload)
        self.book1.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book1.title, "update_title")
        self.assertEqual(self.book1.author, "update_author")

    def test_delete_book(self):
        url = detail_url(self.book1.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
