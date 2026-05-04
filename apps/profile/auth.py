from functools import wraps

from django.middleware.csrf import rotate_token
from django.shortcuts import redirect

from .models import SiteUser

SITE_USER_SESSION_KEY = "site_user_id"


class AnonymousSiteUser:
    is_authenticated = False
    is_anonymous = True
    full_name = ""
    email = ""
    pk = None


def get_current_site_user(request):
    site_user_id = request.session.get(SITE_USER_SESSION_KEY)
    if not site_user_id:
        return AnonymousSiteUser()
    try:
        return SiteUser.objects.get(pk=site_user_id, is_active=True)
    except SiteUser.DoesNotExist:
        request.session.pop(SITE_USER_SESSION_KEY, None)
        return AnonymousSiteUser()


def login_site_user(request, site_user):
    request.session.cycle_key()
    request.session[SITE_USER_SESSION_KEY] = site_user.pk
    request.site_user = site_user
    rotate_token(request)


def logout_site_user(request):
    request.session.pop(SITE_USER_SESSION_KEY, None)
    request.site_user = AnonymousSiteUser()
    rotate_token(request)


def site_login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if getattr(request, "site_user", AnonymousSiteUser()).is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(f"/accounts/login/?next={request.get_full_path()}")

    return wrapped
