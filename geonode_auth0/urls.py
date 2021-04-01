from django.conf.urls import url, include


urlpatterns = [
    url('', include('social_django.urls')),
]
