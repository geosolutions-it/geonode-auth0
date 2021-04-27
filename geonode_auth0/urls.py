from django.conf.urls import url, include
from geonode_auth0.views import rejected_user_view


urlpatterns = [
    url('', include('social_django.urls')),
    url('/unauthorized', rejected_user_view, name='geonode_auth0_unauthorized'),
]
