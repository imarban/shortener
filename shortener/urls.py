"""shortener URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

# from django.contrib import admin
from shorten.views import ShortenView, ShortUrlView, VisitShortUrlView, ShowAllUrlsSaved

urlpatterns = [
    # url(r'^admin/', admin.site.urls),

    url(r'^$', ShortenView.as_view(), name="index"),
    url(r'^short$', ShortUrlView.as_view(), name="short_url"),
    url(r'^all$', ShowAllUrlsSaved.as_view(), name="all_urls"),
    url(r'^(?P<encoded>[a-z0-9]+)$', VisitShortUrlView.as_view(), name="visit_shorten")
]
