from django.test import TestCase
from users.models import User


class UserModelTest(TestCase):
    def test_str_returns_email(self):
        user = User.objects.create_user(
            email="user@test.com",
            password="pass123"
        )

        self.assertEqual(str(user), "user@test.com")
