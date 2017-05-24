from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class OriginalUrl(models.Model):
    original = models.URLField(max_length=250, db_index=True, unique=True)

    def __str__(self):
        return "Id: {}, Shortened {}, Original {}".format(self.id, self.shortened, self.original)


class ShortUrl(models.Model):
    shortened = models.CharField(max_length=35, db_index=True, unique=True, null=True)
    url_associated = models.ForeignKey(OriginalUrl, null=False)
    hash_id = models.IntegerField(unique=True, null=False, db_index=True)
    count = models.IntegerField(default=0)
    user = models.ForeignKey(User, null=True, default=None)


class BadWords(models.Model):
    word = models.CharField(max_length=35, db_index=True, unique=True, null=False)
