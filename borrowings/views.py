from django.contrib.admin import action
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingDetailSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingListSerializer

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        current_user = self.request.user
        queryset = self.queryset

        if not current_user.is_staff:
            queryset = queryset.filter(user=current_user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        if is_active == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        if is_active == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset
