from typing import Dict

from django.conf import settings
from django.contrib.auth import get_user_model


def user_permissions(*args, user: get_user_model() = None, details: Dict = None, **kwargs):
    """
    Function updating user permissions on every login basis, based on the custom claim.
    """

    if not user:
        return

    if details.get('role', '') == settings.AUTH0_ADMIN_ROLE:
        user.is_superuser = True
        user.is_staff = True
        user.save()


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    if details.get('role', '') in settings.AUTH0_REJECTED_ROLES:
        return

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }
