from django.http import HttpResponseForbidden

from shorten.shortener import AlreadyTakenError


class UnauthorizedAccessMiddleware(object):
    def process_exception(self, _, exception):
        if isinstance(exception, AlreadyTakenError):
           return JSON("You are not authorized to access that page.")