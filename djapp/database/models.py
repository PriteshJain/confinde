from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """Stores actual messages, and optionally tags with keywords."""
    text = models.TextField()
    user = models.ForeignKey(User)
    keyword = models.ForeignKey('Keyword', blank=True, null=True)


class Keyword(models.Model):
    """Stores keywords for easy indexing."""
    keyword = models.CharField(max_length=100)
