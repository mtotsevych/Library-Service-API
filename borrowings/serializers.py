from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email",
    )
    book = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="title",
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )


class BorrowingDetailSerializer(BorrowingListSerializer):
    user = UserSerializer(many=False, read_only=True)
    book = BookSerializer(many=False, read_only=True)
