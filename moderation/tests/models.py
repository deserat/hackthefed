from django.db import models

from moderation import moderator


class Comment(models.Model):
    username = models.TextField()
    content = models.TextField()

    def __unicode__(self):
        return u"{0} - {1}".format(self.username, self.content)


class Post(models.Model):
    content = models.TextField()

    def __unicode__(self):
        return u"{0}".format(self.content)

moderator.register(Comment)
moderator.register(Post, pre_moderated=True, content='content')
