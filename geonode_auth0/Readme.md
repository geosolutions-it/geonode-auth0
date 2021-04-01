## Auth0 integration

#### Description
This application provides an optional Auth0 integration, which is configured as the only authentication backend 
of an instance (all other authentication backends are disabled, and that includes django's admin panel).

Integration is implemented with `social-auth-app-django` (see: `requirements.txt`) pipeline, extended with user creation
and update from a custom claim (mapping a custom claim `settings.AUTH0_ROLE_CLAIM`'s value `settings.AUTH0_ADMIN_ROLE` 
to user's `is_superuser` and `is_staff` flags). When enabled, the integration overrides django's admin login and logout
URLs with custom views. Login checks whether a user is authenticated - if not, it redirects to Auth0 login page; 
if so, it checks user's privileges and redirects them to the admin panel or renders Unauthorized response. Logout on the
other hand simply redirects the user to a common logout URL, clearing user's session (`settings.LOGOUT_URL`).
In case logout from the provider (Auth0) should also be performed, django's `settings.ACCOUNT_LOGOUT_REDIRECT_URL` 
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

#### Configuration

To configure the Auth0 integration, the following variables should be set in the instance's environment:

```
export AUTH0_CLIENT_ID=<client_id>                     # OpenID config
export AUTH0_CLIENT_SECRET=<client's_super_secret>     # OpenID config 
export AUTH0_FORCE_SSO=True                            # diables local logins, and enables OpenID endpoints
export LOGIN_URL=/login/auth0                          # makes LoginRequiredMiddleware route all unauthorized to an appropriate login URL
```

**Note**: In case `AUTH0_FORCE_SSO` is `True`, `AUTH0_CLIENT_ID` and `AUTH0_CLIENT_SECRET` variables are required to
or `ImproperlyConfigured` exception is raised.
