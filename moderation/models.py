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
    ban_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)


class FlaggedUser(models.Model):
    '''This model represents a user that has been flagged for another user'''
    poster_sn = models.TextField()
    # User who flags another one
    source = models.CharField(max_length=255, db_index=True)
    who_flags = models.TextField()
    flag_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)
