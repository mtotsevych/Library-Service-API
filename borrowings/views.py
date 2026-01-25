from rest_framework import generics
from rest_framework.serializers import Serializer

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer
)


class BorrowingListCreateView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("user", "book")

    @staticmethod
    def borrow_one_book(book: Book) -> None:
        book.inventory -= 1
        book.save()

    def get_serializer_class(self) -> Serializer:
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingListSerializer

    def perform_create(self, serializer: BorrowingCreateSerializer) -> None:
        borrowing = serializer.save(user=self.request.user)
        self.borrow_one_book(borrowing.book)


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingDetailSerializer
