from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import User


def role_required(*allowed_roles):
    """
    Restringe el acceso a usuarios logueados cuyo role esté en allowed_roles.
    Uso:
        @role_required(User.Roles.PATIENT)
        def mi_vista(request): ...
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user: User = request.user
            if user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator
