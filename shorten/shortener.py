import math
import string
from urllib.parse import urljoin

import random
from django.db import transaction
from wrapt.decorators import synchronized

from shorten.models import OriginalUrl, BadWords, ShortUrl, Domain


class Shortener:
    AVAILABLE_CHARS = string.ascii_lowercase[:] + string.digits
    LETTER_OFFSET = ord(string.ascii_lowercase[0])
    DIGIT_OFFSET = ord(string.digits[0]) - len(string.ascii_lowercase)
    BASE = len(AVAILABLE_CHARS)
    MAX_NUMBER = 2000000

    @staticmethod
    @transaction.atomic
    @synchronized
    def shorten(url, custom='', user=None):
        if custom:
            Shortener.validate_custom(custom)

        domain_db_instance, created = Domain.objects.get_or_create(name=get_domain(url))
        url_db_instance, created = OriginalUrl.objects.get_or_create(original=url, domain=domain_db_instance)
        if not custom:
            hash_id, encoded = Shortener.get_next_encoded()
        else:
            hash_id = Shortener.decode(custom)
            encoded = custom

        custom_db_instance = ShortUrl(shortened=encoded, url_associated=url_db_instance,
                                      hash_id=hash_id, user=user)
        custom_db_instance.save()

        return custom_db_instance

    @staticmethod
    def get_next_encoded():
        value = random.randint(0, Shortener.MAX_NUMBER)

        while Shortener.is_already_taken(value):
            value = random.randint(0, Shortener.MAX_NUMBER)

        avail_encoded = Shortener.encode(value)

        return value, avail_encoded

    @staticmethod
    def is_already_taken(decoded):
        return ShortUrl.objects.filter(hash_id=decoded).count() > 0

    @staticmethod
    def validate_custom(custom):
        custom = custom.lower().strip()

        Shortener.__valid_uniqueness_custom(custom)
        Shortener.__valid_characters_custom(custom)

    @staticmethod
    def __valid_uniqueness_custom(custom):
        custom_decoded = Shortener.decode(custom)
        if ShortUrl.objects.filter(hash_id=custom_decoded).count() > 0:
            raise AlreadyTakenError("Custom is already taken. Choose another one")

    @staticmethod
    def __valid_characters_custom(custom):
        for c in custom:
            if not (ord('a') <= ord(c) <= ord('z') or ord('0') <= ord(c) <= ord('9')):
                raise AlreadyTakenError("Custom value can only contain letters and digits")

    @staticmethod
    def encode(number):
        """
        Converts given number x, from base 10 to base b 
        x -- the number in base 10
        b -- base to convert
        """
        result = []

        if number == 0:
            return Shortener.AVAILABLE_CHARS[0]

        while number > 0:
            result.append(Shortener.AVAILABLE_CHARS[number % Shortener.BASE])
            number = number // Shortener.BASE

        return "".join(result[::-1])

    @staticmethod
    def decode(number_representation):
        """
        Converts given number s, from base b to base 10
        s -- string representation of number
        b -- base of given number
        """
        int_sum = 0
        reversed_number = number_representation[::-1]

        for i, char in enumerate(reversed_number):
            int_sum += Shortener.__alphabet_position(char) * int(math.pow(Shortener.BASE, i))

        return int_sum

    @staticmethod
    def __alphabet_position(char):
        char = char.lower()
        if 'a' <= char <= 'z':
            return ord(char) - Shortener.LETTER_OFFSET
        else:
            return ord(char) - Shortener.DIGIT_OFFSET


class AlreadyTakenError(ValueError):
    def __init__(self, message):
        self.message = message


class WhiteListWordValidator:
    @staticmethod
    def is_valid(word):
        return BadWords.objects.filter(word=word).count() == 0


def get_domain(url):
    return urljoin(url, '/')
