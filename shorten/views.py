# Create your views here.
import http
import json

from django.contrib.auth import logout as auth_logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from django.http.response import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import ProcessFormView
from django.views.generic.list import ListView

from shorten.forms import ShortUrlForm
from shorten.models import ShortUrl, Domain
from shorten.shortener import Shortener
from shortener import settings


class ShortenView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['urls_created'] = ShortUrl.objects.count()
        context['clicks_served'] = ShortUrl.objects.aggregate(Sum('count'))["count__sum"] or 0

        return context


class ShortUrlView(ProcessFormView):
    def post(self, request, *args, **kwargs):
        body_data = json.loads(request.body)
        form = ShortUrlForm(body_data)

        if form.is_valid():
            to_shorten = form.cleaned_data['url']
            custom = form.cleaned_data["custom"]
            user = request.user if not request.user.is_anonymous() else None
            result = Shortener.shorten(to_shorten, custom, user=user)
            shortened = custom if custom else result.shortened
            context = {'shortened': shortened,
                       'url': "http://" + settings.HOST + "/" + shortened}

            return JsonResponse(context, status=http.HTTPStatus.OK)
        else:
            return JsonResponse({'errors': [(f, e) for f, e in form.errors.items()]},
                                status=http.HTTPStatus.UNPROCESSABLE_ENTITY)


class VisitShortUrlView(View):
    def get(self, _, encoded):
        decoded = Shortener.decode(encoded)
        try:
            url_shortened = ShortUrl.objects.select_for_update().get(hash_id=decoded)
            domain = Domain.objects.select_for_update().get(name=url_shortened.url_associated.domain.name)

            domain.count += 1
            domain.save()
            url_shortened.count += 1
            url_shortened.save()

            return redirect(url_shortened.url_associated.original)
        except ObjectDoesNotExist:
            raise Http404("URL not existent")


class ShowAllUrlsSaved(ListView):
    template_name = "list.html"
    context_object_name = "short_urls"
    model = ShortUrl


class GetMyURLS(ListView):
    template_name = "list.html"
    context_object_name = "short_urls"

    def get_queryset(self):
        objects = ShortUrl.objects.filter(user=self.request.user)
        return objects


class GetDomainCount(ListView):
    template_name = "list_domain.html"
    context_object_name = "domains"
    model = Domain


class GetMyDomainCount(ListView):
    template_name = "list_domain.html"
    context_object_name = "domains"

    def get_queryset(self):
        domains = {}
        short_urls = ShortUrl.objects.filter(user=self.request.user)
        for short_url in short_urls:
            if short_url.url_associated.domain.name in domains:
                domains[short_url.url_associated.domain.name] += short_url.count
            else:
                domains[short_url.url_associated.domain.name] = 1

        return [Domain(name=k, count=v) for k, v in domains.items()]


class LogoutView(ProcessFormView):
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect('/')
