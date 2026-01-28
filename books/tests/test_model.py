from django.test import TestCase
from books.models import Book


class BookModelTest(TestCase):
    def test_str_returns_title(self):
        book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover=Book.CoverChoices.HARD,
            inventory=10,
            daily_fee="2.50"
        )

        self.assertEqual(str(book), "Clean Code")
