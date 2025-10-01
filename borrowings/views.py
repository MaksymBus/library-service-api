from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

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

    @action(methods=["POST", "GET"], detail=True, url_path="return")
    def return_borrowing(self, request, pk=None):
        """Endpoint to mark a book as returned"""
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(BorrowingDetailSerializer(borrowing).data, status=status.HTTP_200_OK)
