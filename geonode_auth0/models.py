from django.conf import settings
from social_django.models import DjangoStorage, UserSocialAuth


class CustomPrivilegeUser(UserSocialAuth):
    """
    Proxy model overwriting social_django default's User model,
    enabling to create a user with custom permissions, depending on OpenID claims.
    """

    class Meta:
        proxy = True

    @classmethod
    def create_user(cls, *args, **kwargs):
        role = kwargs.pop('role', None)
        user = super().create_user(*args, **kwargs)

        if role == settings.AUTH0_ADMIN_ROLE:
            user.is_superuser = True
            user.is_staff = True
            user.save()

        return user


class Auth0DjangoStorage(DjangoStorage):
    """social_django Storage, implementing custom User model"""
    user = CustomPrivilegeUser
