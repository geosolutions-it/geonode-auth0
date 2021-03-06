from jose import jwt
from urllib import request
from django.conf import settings
from social_core.backends.oauth import BaseOAuth2


class Auth0(BaseOAuth2):
    """Auth0 OAuth authentication backend"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    EXTRA_DATA = [
        ('picture', 'picture'),
        ('email', 'email'),
        (settings.AUTH0_ROLE_CLAIM, 'role')
    ]

    def authorization_url(self):
        return 'https://' + self.setting('DOMAIN') + '/authorize'

    def access_token_url(self):
        return 'https://' + self.setting('DOMAIN') + '/oauth/token'

    def get_user_id(self, details, response):
        """Return current user id."""
        return details['user_id']

    def get_user_details(self, response):
        # Obtain JWT and the keys to validate the signature
        id_token = response.get('id_token')
        jwks = request.urlopen('https://' + self.setting('DOMAIN') + '/.well-known/jwks.json')
        issuer = 'https://' + self.setting('DOMAIN') + '/'
        audience = self.setting('KEY')  # CLIENT_ID
        payload = jwt.decode(id_token, jwks.read(), algorithms=['RS256'], audience=audience, issuer=issuer)

        roles = payload.get(settings.AUTH0_ROLE_CLAIM, None)

        if isinstance(roles, (list, tuple)):
            role = roles[0] if roles else settings.AUTH0_DEFAULT_ROLE
        else:
            role = roles if roles else settings.AUTH0_DEFAULT_ROLE

        details = {
            'username': payload['nickname'],
            'first_name': payload['name'],
            'picture': payload['picture'],
            'user_id': payload['sub'],
            'email': payload['email'],
            'role': role,
        }

        return details

    def auth_allowed(self, response, details):
        """Return True if the user should be allowed to authenticate"""

        allowed = super().auth_allowed(response, details)
        role = details.get('role', None)

        if role in settings.AUTH0_REJECTED_ROLES:
            return False

        return allowed
