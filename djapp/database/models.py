from django.db import models


class Information(models.Model):
    """Stores actual messages, and optionally tags with keywords."""
    message = models.TextField()
    keyword = models.ForeignKey('Keyword', blank=True, null=True)


class Keyword(models.Model):
    """Stores keywords for easy indexing."""
    keyword = models.CharField(max_length=100)
