import math
import string

import random
from django.core.exceptions import ObjectDoesNotExist

from shorten.models import URLShortened, BadWords, CustomShortUrl


class Shortener:
    AVAILABLE_CHARS = string.ascii_lowercase[:] + string.digits
    LETTER_OFFSET = ord(string.ascii_lowercase[0])
    DIGIT_OFFSET = ord(string.digits[0]) - len(string.ascii_lowercase)
    BASE = len(AVAILABLE_CHARS)
    MAX_NUMBER = 1000000

    @staticmethod
    def shorten(url, custom=''):
        if custom:
            Shortener.validate_custom(custom)

        try:
            url_db_instance = URLShortened.objects.get(original=url)
        except ObjectDoesNotExist:
            hash_id, next_available_encoded = Shortener.get_next_encoded()
            url_db_instance = URLShortened(original=url, hash_id=hash_id, shortened=next_available_encoded)
            url_db_instance.save()

        if custom:
            custom_db_instance = CustomShortUrl(custom=custom, url_associated=url_db_instance,
                                                hash_id=Shortener.decode(custom))
            custom_db_instance.save()

        return url_db_instance

    @staticmethod
    def get_next_encoded():
        value = random.randint(0, Shortener.MAX_NUMBER)

        while Shortener.is_already_taken(value):
            value = random.randint(0, Shortener.MAX_NUMBER)

        avail_encoded = Shortener.encode(value)

        return value, avail_encoded

    @staticmethod
    def is_already_taken(decoded):
        return URLShortened.objects.filter(hash_id=decoded).count() > 0 or CustomShortUrl.objects.filter(
            hash_id=decoded).count() > 0

    @staticmethod
    def validate_custom(custom):
        custom = custom.lower().strip()
        custom_decoded = Shortener.decode(custom)
        if URLShortened.objects.filter(hash_id=custom_decoded).count() > 0 or CustomShortUrl.objects.filter(
                hash_id=custom_decoded).count() > 0:
            raise AlreadyTakenError("Custom is already taken. Choose another one")

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
