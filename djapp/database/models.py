from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """Stores actual messages, and optionally tags with keywords."""
    text = models.TextField()
    user = models.ForeignKey(User)
    keyword = models.ForeignKey('Keyword', blank=True, null=True)

    @staticmethod
    def store(email, text, keyword=None):
        """Stores given text and assigns it to user, creates Django user if
        matching user is not found."""
        try:
            user = User.objects.get(email=email)
        except:
            username = email.replace('.', '')
            username = username.replace('@', '')
            user = User(email=email, username=username).save()
            print "User", user, "created."

        Message(text=text, user=user, keyword=keyword).save()

    @staticmethod
    def get_by_search(email, words_to_match):
        """Gets messages with text that matches all words in the list."""
        try:
            user = User.objects.get(email=email)
        except:
            #TODO Raise a sane error
            raise

        return Message._get_recursive_union_filter(
                Message.objects, words_to_match, user)

    @staticmethod
    def _get_recursive_union_filter(message_objects, words, user):
        if len(words) == 0:
            return message_objects

        words_new = words[1:]
        return Message._get_recursive_union_filter(
                message_objects.filter(
                    text__contains=words[0], user=user), words_new, user)



class Keyword(models.Model):
    """Stores keywords for easy indexing."""
    keyword = models.CharField(max_length=100)
