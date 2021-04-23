# default geonode_auth0 app's settings

import os

# variable determining, whether Auth0 should be the only authentication provider
AUTH0_FORCE_SSO = False

AUTH0_ADMIN_ROLE = 'factory'
AUTH0_ROLE_CLAIM = 'https://sdf.com/role'
AUTH0_DEFAULT_ROLE = 'customer'

SOCIAL_AUTH_AUTH0_KEY = os.getenv('AUTH0_CLIENT_ID')
SOCIAL_AUTH_AUTH0_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
SOCIAL_AUTH_AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')

SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
SOCIAL_AUTH_STORAGE = 'geonode_auth0.models.Auth0DjangoStorage'
SOCIAL_AUTH_USER_FIELDS = ['username', 'email', 'role']
SOCIAL_AUTH_PIPELINE = (
    # default auth pipeline - social_core.pipeline.DEFAULT_AUTH_PIPELINE
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    # auth pipeline extension - assign custom user permissions
    'geonode_auth0.pipelines.user_permissions'
)

SOCIAL_AUTH_AUTH0_SCOPE = [
    'openid',
    'profile',
    'email',
    AUTH0_ROLE_CLAIM
]
