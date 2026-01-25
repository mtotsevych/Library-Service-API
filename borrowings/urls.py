from django.urls import path

from borrowings.views import (
    BorrowingDetailView,
    BorrowingListCreateView,
)

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowing-list-create"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
]
