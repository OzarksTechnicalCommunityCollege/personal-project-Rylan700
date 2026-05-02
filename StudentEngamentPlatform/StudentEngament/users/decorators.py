from django.http import HttpResponseForbidden
from functools import wraps

def club_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseForbidden("Login required")

        if request.user.role != "club_admin":
            return HttpResponseForbidden("Not a club admin")

        return view_func(request, *args, **kwargs)

    return wrapper