from django.urls import path

from borrowings.views import BorrowingDetailView, BorrowingListView

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingListView.as_view(), name="borrowing-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
]
