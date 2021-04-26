# geonode-auth0

### Auth0 as the only authentication method for Geonode
 
This application provides an optional Auth0 integration, which is configured as the only authentication backend 
of an instance (if integration is enabled, all other authentication backends are disabled, and that includes 
django's admin panel).

Integration is implemented with `social-auth-app-django` (see: `requirements.txt`) pipeline, extended with user creation
and update from a custom claim - mapping a custom claim `settings.AUTH0_ROLE_CLAIM`'s value `settings.AUTH0_ADMIN_ROLE` 
to user's `is_superuser` and `is_staff` flags (required since all local authentication backends are disabled).
When enabled, the integration overrides django's admin login and logout URLs with custom views. Admin login checks 
whether a user is authenticated - if not, it redirects to Auth0 login page;  if so, it checks user's privileges 
and redirects them to the admin panel or renders Unauthorized response. Logout on the other hand simply redirects 
the user to a common logout URL, clearing user's session (`settings.LOGOUT_URL`).

In case logout from the provider (Auth0) should also be performed, django-allauth's `settings.ACCOUNT_LOGOUT_REDIRECT_URL` 
should be updated with provider's endpoint, enabling the logout.

**Warning**: The integration assumes there are no local users in the database of an instance for which Auth0 authentication
is enabled. Turning on the integration without clearing the existing users from the DB may result in an unexpected behavior.

**Warning**: Configuring the integration without providing the custom claim and admin role's defined by this claim will 
disable a possibility to reach admin panel, since all other authentication backends are disabled.

**Note**: The integration unconditionally overrides `allauth`'s logout message with a blank template in 
`geosk/auth0/templates/account/messages/logged_out.txt`. `allauth` logout is the default logout of Geonode.
With a redirection to Auth0 after local user's logout, the `You have signed out.` message was stored and displayed 
once Geonode was reached again, which was right after user's login, causing sign out message to be displayed after 
the login. To prevent this behavior, the message template had to be overridden.

#### Quick start

1. Install the application and it's dependencies
    ```
    pip install -e git+https://github.com/geosolutions-it/geonode-auth0.git@main#egg=geonode_auth0
    ```
   
2. Add `social_django` (which provides base OpenID functionalities for the app) and `geonode_auth0` to INSTALLED_APPS on the beginning of the list:
    ```python
    INSTALLED_APPS = [
       # social logins
       'social_django',
       'geonode_auth0',
       ...
   ]
    ```

3. Add Auth0 configuration to your `settings.py` as optional for your project
    ```python
    import os
    
    AUTH0_FORCE_SSO = os.getenv('AUTH0_FORCE_SSO', False)
    AUTH0_ROLE_CLAIM = '<role_claim>'
    AUTH0_ADMIN_ROLE = '<role_claim's_admin_value>'
    
    SOCIAL_AUTH_AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    SOCIAL_AUTH_AUTH0_KEY = os.getenv('AUTH0_CLIENT_ID')
    SOCIAL_AUTH_AUTH0_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    
    LOGOUT_URL = os.getenv('LOGOUT_URL', '{}account/logout/'.format(SITEURL))
    ACCOUNT_LOGIN_REDIRECT_URL = os.getenv('LOGIN_REDIRECT_URL', SITEURL)
    
    if AUTH0_FORCE_SSO:
        # -- START overwrite configuration if Auth0 is the only supported login method
        AUTHENTICATION_BACKENDS = ['geonode_auth0.auth0backend.Auth0']
    
        LOGIN_URL = os.getenv('LOGIN_URL', '{}login/auth0'.format(SITEURL))
    
        # on logout, redirect the user to logout also from Auth0 Identity Provider
        # read more: https://auth0.com/docs/api/authentication#logout
        ACCOUNT_LOGOUT_REDIRECT_URL = os.getenv(
            'LOGOUT_REDIRECT_URL',
            'https://{domain}/v2/logout?client_id={client_id}'.format(
                domain=SOCIAL_AUTH_AUTH0_DOMAIN,
                client_id=SOCIAL_AUTH_AUTH0_KEY,
            )
        )
        # -- END overwrite configuration if Auth0 is the only supported login method
    else:
        LOGIN_URL = os.getenv('LOGIN_URL', '{}account/login/'.format(SITEURL))
        ACCOUNT_LOGOUT_REDIRECT_URL = os.getenv('LOGOUT_REDIRECT_URL', SITEURL)
    ```

4. If your Geonode instance is locked down (`LOCKDOWN_GEONODE` is True), remember to add OpenID's callback URL to the authorized exempt URLs (also in `settings.py`)
    
    ```python
    AUTH_EXEMPT_URLS = ('/complete/auth0',)
    ``` 

5. Add OpenId URLs and update Auth0 admin panel access configuration in `urls.py` (as applicable only when the integration is enabled)
    ```python
   from django.conf import settings
   from django.conf.urls import url
   from geonode_auth0.urls import urlpatterns as auth0_patterns
   from geonode_auth0.views import admin_login_view, admin_logout_view
   
   ... # define your urlpatterns
   
   # at the very end of the urls.py file
    if settings.AUTH0_FORCE_SSO:
        urlpatterns = [
            # overwrite /admin/login with a custom OpenID based view
            url('/admin/login/', admin_login_view),
            # overwrite /admin/logout with a custom view, redirecting to settings.LOGOUT_URL
            url('/admin/logout/', admin_logout_view),
        ] + urlpatterns + auth0_patterns
    ```

6. To enable the Auth0 integration set the following variables in your project's environment:
    ```.env
    AUTH0_CLIENT_ID=<client_id>                     # OpenID config
    AUTH0_CLIENT_SECRET=<client's_super_secret>     # OpenID config 
    AUTH0_DOMAIN=<provider's_domain>                # OpenID config
    AUTH0_FORCE_SSO=True                            # diables local logins, and enables OpenID endpoints
    LOGIN_URL=/login/auth0                          # makes LoginRequiredMiddleware route all unauthorized to an appropriate login UR
    ```

**Note**: In case `AUTH0_FORCE_SSO` is `True`, `SOCIAL_AUTH_AUTH0_KEY`, `SOCIAL_AUTH_AUTH0_KEY` and 
`SOCIAL_AUTH_AUTH0_DOMAIN` settings variables are required (in the configuration above, they are set using 
environment variables) or `ImproperlyConfigured` exception is raised.


### Rejected Roles

This application allows setting user's roles (retrieved from the custom claim), which will be rejected
at login.

In order to configure such behavior, you need to add the following in your project settings:
`AUTH0_REJECTED_ROLES`, `AUTH0_REJECTION_REDIRECT`, and append `UserRejectedMiddleware` middleware 
to your middleware list, e.g.:
```python
AUTH0_REJECTED_ROLES = ['my_role1', 'my_role2']                            # default ['dealer', 'subsidiary']
AUTH0_REJECTION_REDIRECT = '/<geonode-auth0-url-perfix>/unauthorized'    # does not have a default value
MIDDLEWARE = (
   ...
   'geonode_auth0.middleware.UserRejectedMiddleware',
)
```

The configuration above will prevent a user with a group in `AUTH0_REJECTED_ROLES` from login
and account creation with Auth0 provider, redirecting them (using `UserRejectedMiddleware`)
to an unauthorized view (provided in `AUTH0_REJECTION_REDIRECT`).

Please note, that if your Geonode instance is in `LOCKDOWN` mode, you need to update the `AUTH_EXEMPT_URLS` list:
```python
AUTH_EXEMPT_URLS = (
    ...
    AUTH0_REJECTION_REDIRECT,
    f'/\w{{2}}{AUTH0_REJECTION_REDIRECT}',
)
```

(the first entry allows reaching the unauthorized view, and the second one allows reaching translations of 
unauthorized view).

**Warning:** It is very important to  test the above exempts, since a simple typo may cause the system
to go into an infinite redirection loop (if a User is logged in to the Auth0 provider).