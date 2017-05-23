from django.conf.urls import patterns, url

from comunidad.views import UserDetailView, HomeUsersView

urlpatterns = patterns('',
                       url(r'^$', HomeUsersView.as_view(), name="index"),
                       )
