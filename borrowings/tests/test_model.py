from django.test import TestCase
from django.utils import timezone

from books.models import Book
from users.models import User
from borrowings.models import Borrowing


class BorrowingModelTest(TestCase):
    def test_str_returns_correct_format(self):
        user = User.objects.create_user(
            email="user@test.com",
            password="pass123"
        )
        book = Book.objects.create(
            title="Clean Architecture",
            author="Robert C. Martin",
            cover=Book.CoverChoices.HARD,
            inventory=3,
            daily_fee="1.50"
        )

        borrow_date = timezone.now().date()

        borrowing = Borrowing.objects.create(
            borrow_date=borrow_date,
            expected_return_date=borrow_date,
            actual_return_date=None,
            book=book,
            user=user
        )

        expected_str = f"{book.title} borrowed at {borrow_date}"
        self.assertEqual(str(borrowing), expected_str)
