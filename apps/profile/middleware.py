from .auth import get_current_site_user


class SiteUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.site_user = get_current_site_user(request)
        return self.get_response(request)
