from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from books.models import Book
from borrowings.models import Borrowing
from borrowings.permissions import IsBorrower
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer
)


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

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

    def get_queryset(self) -> QuerySet[Borrowing]:
        queryset = Borrowing.objects.select_related("user", "book")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active == "1":
            queryset = queryset.filter(actual_return_date=None)
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=int(user_id))

        return queryset


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingDetailSerializer
    permission_classes = (IsBorrower,)
