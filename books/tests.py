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
            cover="HARD",
            inventory=1,
            daily_fee=12.23,
        )
        self.book2 = Book.objects.create(
            title="test_title2",
            author="test_author2",
            cover="HARD",
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
            "cover": "HARD",
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
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 22.23,
        }
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_forbidden(self):
        url = detail_url(self.book1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


#
# class AdminCrewApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             "admin@admin.com", "testpass", is_staff=True
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_create_book(self):
#         payload = {
#             "title": "new_title",
#             "author": "new_author",
#             "cover": "HARD",
#             "inventory": 2,
#             "daily_fee": 22.23,
#         }
#         res = self.client.post(BOOKS_URL, payload)
#
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#
#     def test_update_journey(self):
#         payload = {
#             "departure_time": datetime(2025, 10, 23, 8, 0),
#             "arrival_time": datetime(2025, 10, 23, 14, 0),
#             "train": self.train2.id,
#             "route": self.route.id,
#         }
#
#         url = detail_url(self.journey1.id)
#
#         res = self.client.put(url, payload)
#         self.journey1.refresh_from_db()
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(self.journey1.train, self.train2)
#
#     def test_delete_journey(self):
#         url = detail_url(self.journey1.id)
#
#         res = self.client.delete(url)
#
#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Journey.objects.filter(id=self.journey1.id).exists())
