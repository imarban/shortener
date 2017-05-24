from django.test import TestCase

# Create your tests here.
from shorten.models import URLShortened, CustomShortUrl
from shorten.shortener import Shortener, AlreadyTakenError


class ShortenerEncoderTest(TestCase):
    def test_encode(self):
        self.assertEqual(Shortener.AVAILABLE_CHARS[0], Shortener.encode(0))
        self.assertEqual(Shortener.AVAILABLE_CHARS[26], Shortener.encode(26))
        self.assertEqual('eyay', Shortener.encode(217752))
        self.assertEqual('ooo', Shortener.encode(18662))
        self.assertEqual('upiz', Shortener.encode(952873))

    def test_decode(self):
        self.assertEqual(0, Shortener.decode(Shortener.AVAILABLE_CHARS[0]))
        self.assertEqual(26, Shortener.decode(Shortener.AVAILABLE_CHARS[26]))
        self.assertEqual(217752, Shortener.decode('eyay'))
        self.assertEqual(18662, Shortener.decode('ooo'))
        self.assertEqual(952873, Shortener.decode('upiz'))


class ValidCustomTest(TestCase):
    def test_already_taken_custom(self):
        Shortener.shorten(url="www.a.com", custom="upiz")
        with self.assertRaises(AlreadyTakenError):
            Shortener.validate_custom("upiz")

    def test_invalid_chars_custom(self):
        Shortener.shorten(url="www.b.com", custom="nope")
        with self.assertRaises(AlreadyTakenError):
            Shortener.validate_custom("-.google")

    def test_next_encoded(self):
        value, encoded = Shortener.get_next_encoded()
        self.assertEqual(value, Shortener.decode(encoded))
        self.assertEqual(encoded, Shortener.encode(value))


class ShortenerSaveTest(TestCase):
    def test_save_without_custom(self):
        url = "www.a.com"
        Shortener.shorten(url=url)
        result = URLShortened.objects.get(original=url)
        self.assertEqual(result.original, url)
        self.assertEqual(result.shortened, Shortener.encode(result.hash_id))

    def test_save_with_custom(self):
        url = "www.b.com"
        custom = "nope"
        Shortener.shorten(url=url, custom=custom)
        result_url = URLShortened.objects.get(original=url)
        result_custom = CustomShortUrl.objects.get(custom=custom)

        self.assertEqual(result_url.original, url)
        self.assertEqual(result_url.shortened, Shortener.encode(result_url.hash_id))
        self.assertEqual(result_custom.url_associated_id, result_url.id)

    def test_save_existent(self):
        url = "www.c.com"
        result_url1 = Shortener.shorten(url=url)
        result_url2 = Shortener.shorten(url=url)

        self.assertEqual(result_url1, result_url2)

    def test_save_existent_with_custom(self):
        url = "www.c.com"
        custom = "kame"
        result_url1 = Shortener.shorten(url=url)
        result_url2 = Shortener.shorten(url=url, custom=custom)
        custom_result = CustomShortUrl.objects.get(custom=custom)

        self.assertEqual(result_url1, result_url2)
        self.assertEqual(result_url1.id, custom_result.url_associated_id)

    def test_save_existent_custom(self):
        custom = "right"
        Shortener.shorten(url="www.d.com", custom=custom)
        with self.assertRaises(AlreadyTakenError):
            Shortener.shorten(url="www.e.com", custom=custom)
