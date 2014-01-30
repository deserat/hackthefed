from django.db import models


class BannedWord(models.Model):
    '''This model represents a banned word'''
    word = models.CharField(max_length=100)

    def __unicode__(self):
        return self.word


class DefaultBannedWord(models.Model):
    '''We'll have a list of default banned words'''
    word = models.CharField(max_length=100)

    def __unicode__(self):
        return self.word


class BannedUser(models.Model):
    '''This model represents a banned user'''
    poster_sn = models.TextField()
    poster_id = models.TextField(blank=True, help_text='Required for Facebook users')
    source = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)
