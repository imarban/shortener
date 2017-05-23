from django import forms
from django.core.exceptions import ValidationError

from shorten.shortener import Shortener, AlreadyTakenError


class ShortUrlForm(forms.Form):
    url = forms.URLField(max_length=250, required=True)
    custom = forms.CharField(max_length=35, required=False)

    def clean_custom(self):
        custom = self.cleaned_data['custom']
        try:
            Shortener.validate_custom(custom)
        except AlreadyTakenError as e:
            raise ValidationError(e.message)

        return custom
