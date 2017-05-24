# Create your views here.
import http
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from django.http.response import JsonResponse, Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import ProcessFormView
from django.views.generic.list import ListView

from shorten.forms import ShortUrlForm
from shorten.models import URLShortened, CustomShortUrl
from shorten.shortener import Shortener
from shortener import settings


class ShortenView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['urls_created'] = URLShortened.objects.count()
        context['clicks_served'] = URLShortened.objects.aggregate(Sum('count'))["count__sum"]

        return context


class ShortUrlView(ProcessFormView):
    def post(self, request, *args, **kwargs):
        body_data = json.loads(request.body)
        form = ShortUrlForm(body_data)

        if form.is_valid():
            to_shorten = form.cleaned_data['url']
            custom = form.cleaned_data['custom']
            result = Shortener.shorten(to_shorten, custom)
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
            url_shortened = URLShortened.objects.get(hash_id=decoded)
        except ObjectDoesNotExist:
            try:
                url_shortened = URLShortened.objects.get_(
                    id=CustomShortUrl.objects.get(hash_id=decoded).url_associated_id)
            except:
                raise Http404("URL not existent")

        url_shortened.count += 1
        url_shortened.save()

        return redirect(url_shortened.original)


class ShowAllUrlsSaved(ListView):
    template_name = "list.html"
    context_object_name = "urls"

    def get_queryset(self):
        objects = URLShortened.objects.all()
        for x in objects:
            x.customs = ", ".join([k.custom for k in CustomShortUrl.objects.filter(url_associated_id=x.id)])
        return objects
