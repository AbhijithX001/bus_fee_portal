from django.shortcuts import redirect
from functools import wraps


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if getattr(request.user, "role", None) != required_role:
                if getattr(request.user, "role", None) == "admin":
                    return redirect("admin_dashboard")
                return redirect("student_dashboard")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
