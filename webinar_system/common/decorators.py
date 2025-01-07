from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapped_view

    return decorator
