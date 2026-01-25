from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from borrowings.models import Borrowing


class IsBorrower(BasePermission):
    def has_object_permission(
        self,
        request: Request,
        view,
        obj: Borrowing
    ) -> bool:
        return (
            bool(request.user.is_staff)
            or bool(request.user == obj.user)
        )
