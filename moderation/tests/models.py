from django.db import models

from moderation.models import ModeratedContent


class Comment(ModeratedContent):
    username = models.TextField()
    content = models.TextField()

    def __unicode__(self):
        return u"{0} - {1}".format(self.username, self.content)


class Post(ModeratedContent):
    content = models.TextField()

    def __unicode__(self):
        return u"{0}".format(self.content)
