from django.conf.urls import url
from django.contrib import admin

from bitcoinnodestats.views import HomeView, PlotsViews


urlpatterns = [
    url(r'^$', HomeView.as_view()),
    url(r'^plots/$', PlotsViews.as_view()),
    url(r'^admin/', admin.site.urls),
]
