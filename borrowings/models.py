from django.db import models

from Library_Service_API import settings


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True)
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def __str__(self) -> str:
        return f"{self.book.title} borrowed at {self.borrow_date}"

    class Meta:
        ordering = ("-borrow_date",)
