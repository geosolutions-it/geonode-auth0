from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect


def admin_login_view(request):
    """
    Custom django admin login view, redirecting unauthenticated requests
    to the LOGIN_URL (by default Auth0 OpenID provider), rendering unauthorized
    message for underprivileged users, and privileged users to the admin panel.
    """
    if not request.user:
        return HttpResponseRedirect(settings.LOGIN_URL)

    elif not request.user.is_staff and not request.user.is_superuser:
        return HttpResponse('Unauthorized')

    else:
        return HttpResponseRedirect(reverse('admin:index'))


def admin_logout_view(request):
    """
    Custom django admin logout view, redirecting requests to settings.LOGOUT_URL
    """
    return HttpResponseRedirect(settings.LOGOUT_URL)
