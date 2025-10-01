from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """
    Custom permission to allow read-only access (GET, HEAD, OPTIONS) for
    all users (authenticated and unauthenticated), and full read/write/delete
    (CRUD) access only for users with the 'is_staff' flag
    set (i.e., Admin users).

    Permissions logic:
    1. If the request method is a SAFE_METHOD (Read operation),
        allow access (True).
       This ensures that all users can list or retrieve resources.
    2. Otherwise (for write/unsafe operations like POST, PUT, DELETE),
       only allow access if the requesting user is authenticated
       and is a staff member.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
