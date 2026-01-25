from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from users.models import User
from borrowings.models import Borrowing


class BorrowingListCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass123", is_staff=True
        )

        self.book = Book.objects.create(
            title="Django Book",
            author="Author",
            cover=Book.CoverChoices.HARD,
            inventory=5,
            daily_fee="1.50"
        )

        self.url = reverse("borrowings:borrowing-list-create")

    # LIST TESTS

    def test_anonymous_cannot_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_his_borrowings(self):
        Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.admin
        )

        own = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.user
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own.id)

    def test_admin_sees_all_borrowings(self):
        Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.user
        )
        Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.admin
        )

        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_is_active(self):
        active = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.user,
            actual_return_date=None
        )
        Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.user,
            actual_return_date=timezone.now().date()
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url + "?is_active=1")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], active.id)

    def test_filter_user_id_only_for_admin(self):
        b1 = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.user
        )
        b2 = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            book=self.book,
            user=self.admin
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url + f"?user_id={self.admin.id}")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], b1.id)

        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url + f"?user_id={self.user.id}")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], b1.id)

    # CREATE TESTS

    def test_anonymous_cannot_create(self):
        response = self.client.post(self.url, {
            "borrow_date": "2024-01-01",
            "expected_return_date": "2024-01-02",
            "book": self.book.title
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_create_borrowing(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {
            "borrow_date": "2024-01-01",
            "expected_return_date": "2024-01-02",
            "book": self.book.title
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)

        borrowing = Borrowing.objects.first()
        self.assertEqual(borrowing.user, self.user)

    def test_inventory_decreases_on_create(self):
        self.client.force_authenticate(self.user)

        self.client.post(self.url, {
            "borrow_date": "2024-01-01",
            "expected_return_date": "2024-01-02",
            "book": self.book.title
        })

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_cannot_create_if_book_out_of_stock(self):
        self.book.inventory = 0
        self.book.save()

        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {
            "borrow_date": "2024-01-01",
            "expected_return_date": "2024-01-02",
            "book": self.book.title
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This book is out of stock", str(response.data))


class BorrowingReturnViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com", password="pass123"
        )
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass123", is_staff=True
        )

        self.book = Book.objects.create(
            title="Django Book",
            author="Author",
            cover=Book.CoverChoices.HARD,
            inventory=1,
            daily_fee="1.50"
        )

        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date(),
            actual_return_date=None,
            book=self.book,
            user=self.user
        )

        self.url = reverse(
            "borrowings:borrowing-return",
            args=[self.borrowing.id]
        )

    # PERMISSIONS

    def test_anonymous_cannot_return(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_cannot_return(self):
        stranger = User.objects.create_user(
            email="stranger@test.com", password="pass123"
        )
        self.client.force_authenticate(stranger)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_return_any_borrowing(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    # RETURN LOGIC

    def test_user_can_return_own_borrowing(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "The book has been returned")

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 2)

    def test_cannot_return_twice(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "The book was already returned")

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)
