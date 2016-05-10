from django.conf.urls import url
from django.contrib import admin

from bitcoinnodestats.views import HomeView


urlpatterns = [
    url(r'^$', HomeView.as_view()),
    url(r'^admin/', admin.site.urls),
]
