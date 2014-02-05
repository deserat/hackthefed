from django.db import models

from moderation import moderator


class Comment(models.Model):
    username = models.TextField()
    content = models.TextField()

    def __unicode__(self):
        return u"{0} - {1}".format(self.username, self.content)

moderator.register(Comment)
