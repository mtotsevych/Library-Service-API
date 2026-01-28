from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("users:register")
        self.me_url = reverse("users:me")

        self.user = User.objects.create_user(
            email="user@test.com",
            password="pass123",
            first_name="John",
            last_name="Doe"
        )

    # REGISTER VIEW

    def test_user_can_register(self):
        data = {
            "email": "new@test.com",
            "password": "pass123",
            "first_name": "Alice",
            "last_name": "Smith",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

        user = User.objects.get(email="new@test.com")
        self.assertTrue(user.check_password("pass123"))

    def test_register_ignores_is_staff(self):
        data = {
            "email": "evil@test.com",
            "password": "pass123",
            "is_staff": True,
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="evil@test.com")
        self.assertFalse(user.is_staff)

    # ME

    def test_anonymous_cannot_access_me(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_get_own_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_can_update_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.put(self.me_url, {
            "email": "user@test.com",
            "first_name": "NewName",
            "last_name": "NewLast",
            "password": "newpass123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewName")
        self.assertTrue(self.user.check_password("newpass123"))
