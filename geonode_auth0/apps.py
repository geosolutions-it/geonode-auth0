from django.apps import AppConfig


class GeoNodeAuth0Config(AppConfig):
    """
    Application configuring and customizing Auth0 OpenID integration.
    """

    name = 'geonode_auth0'
    label = 'geonode_auth0'

    def ready(self):
        from django.conf import settings
        from geonode_auth0 import settings as defult_settings

        # load default settings
        for name in dir(defult_settings):
            if name.isupper() and not hasattr(settings, name):
                # if setting is not present in settings, update settings with it
                setattr(settings, name, getattr(defult_settings, name))

        if getattr(settings, 'AUTH0_FORCE_SSO', False):
            # check Auth0 configuration if Auth0 is forced authentication method
            if not getattr(settings, 'SOCIAL_AUTH_AUTH0_KEY', '') or not getattr(settings, 'SOCIAL_AUTH_AUTH0_KEY', ''):
                from django.core.exceptions import ImproperlyConfigured

                raise ImproperlyConfigured(
                    'Missing Auth0 configuration: check AUTH0_CLIENT_ID and/or AUTH0_CLIENT_SECRET envvars.'
                )
