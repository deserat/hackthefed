import datetime

from django.utils.timezone import utc
from django.db import models


# Available moderation status
MODERATION_STATUS_PENDING = 2
MODERATION_STATUS_REJECTED = 0
MODERATION_STATUS_APPROVED = 1


MODERATION_STATUS = (
    (MODERATION_STATUS_APPROVED, "Approved"),
    (MODERATION_STATUS_PENDING, "Pending"),
    (MODERATION_STATUS_REJECTED, "Rejected"),
)


class ModerationException(Exception):
    pass


class ModeratedContent(models.Model):
    moderation_status = models.SmallIntegerField(choices=MODERATION_STATUS,
                                                 default=MODERATION_STATUS_PENDING)
    moderation_reason = models.TextField(blank=True)
    moderation_last_date = models.DateTimeField(blank=True, null=True)
    moderation_times_moderated = models.SmallIntegerField(default=0)
    moderation_times_flagged = models.SmallIntegerField(default=0)
    moderation_last_flagged_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def approve(self, reason=''):
        self._moderate(MODERATION_STATUS_APPROVED, reason)

    def reject(self, reason=''):
        self._moderate(MODERATION_STATUS_REJECTED, reason)

    def flag(self):
        self.moderation_times_flagged += 1
        self.moderation_last_flagged_date = datetime.datetime.utcnow().replace(tzinfo=utc)

        self.save()

    def save(self, *args, **kwargs):
        return super(ModeratedContent, self).save(*args, **kwargs)

    def _moderate(self, status, reason=''):
        self.moderation_status = status
        self.moderation_last_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.moderation_reason = reason

        self.save()


class BannedWord(models.Model):
    '''This model represents a banned word'''
    word = models.CharField(max_length=100)

    class Meta:
        ordering = ['word']

    def save(self, *args, **kwargs):
        num_words = len(self.word.split(' '))
        if num_words > 1:
            raise ModerationException('Blank spaces are not allowed')
        return super(BannedWord, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.word


class BannedUser(models.Model):
    '''This model represents a banned user'''
    poster_sn = models.TextField()
    poster_id = models.TextField(blank=True, help_text='Required for some networks such as FB and Instagram')
    source = models.CharField(max_length=255, db_index=True)
    times_moderated = models.SmallIntegerField(default=0)
    last_moderated_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_moderated_date = datetime.datetime.now()
        return super(BannedUser, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)


class FlaggedUser(models.Model):
    '''This model represents a user that has been flagged by another user'''
    poster_sn = models.TextField()
    poster_id = models.TextField(blank=True, help_text='Required for some networks such as FB and Instagram')
    # User who flags another one
    source = models.CharField(max_length=255, db_index=True)
    times_flagged = models.SmallIntegerField(default=0)
    last_flagged_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_flagged_date = datetime.datetime.now()
        return super(FlaggedUser, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)
