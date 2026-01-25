from django.utils import timezone

from celery import shared_task

from borrowings.models import Borrowing


@shared_task
def check_overdue_borrowings() -> None:
    today = timezone.now().date()

    borrowings = (
        Borrowing.objects
        .filter(
            actual_return_date=None,
            expected_return_date__lte=today
        )
        .select_related("book")
    )

    with open("overdue_borrowings.txt", "a") as file:
        file.write(f"Date: {today}.\n")
        if borrowings.exists():
            for borrowing in borrowings:
                file.write(
                    f"Borrowing ID is {borrowing.id}.\n"
                    f"The return of the borrowed book "
                    f"titled '{borrowing.book.title}' is overdue.\n"
                    f"The expected return date "
                    f"was {borrowing.expected_return_date}.\n\n"
                )
        else:
            file.write("No borrowings overdue today!\n\n")
