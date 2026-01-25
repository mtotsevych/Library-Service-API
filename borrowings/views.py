from django.utils import timezone

from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

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


class BorrowingReturnView(APIView):
    permission_classes = (IsBorrower,)

    def post(self, request: Request, pk: int, *args, **kwargs) -> Response:
        borrowing = get_object_or_404(Borrowing, pk=pk)

        if not borrowing.actual_return_date:
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

            return Response(
                {"detail": "The book has been returned"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"detail": "The book was already returned"},
            status=status.HTTP_200_OK
        )
