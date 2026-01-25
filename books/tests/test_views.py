from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from users.models import User


class BookViewSetPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass123", is_staff=True
        )
        self.list_url = reverse("books:book-list")

    def test_anyone_can_list_books(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_book(self):
        response = self.client.post(self.list_url, {
            "title": "Test Book",
            "author": "Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": "1.50"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, {
            "title": "Test Book",
            "author": "Author",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": "1.50"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.list_url, {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": "Soft",
            "inventory": 10,
            "daily_fee": "2.00"
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.first().title, "Admin Book")
