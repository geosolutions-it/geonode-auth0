from django.conf import settings
from django.http import HttpResponseRedirect
from social_core.exceptions import AuthForbidden


class UserRejectedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthForbidden):
            if getattr(settings, 'AUTH0_REJECTION_REDIRECT', ''):
                return HttpResponseRedirect(settings.AUTH0_REJECTION_REDIRECT)
