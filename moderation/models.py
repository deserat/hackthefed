import datetime

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


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
    poster_id = models.TextField(blank=True, help_text='Required for some networks such as FB and Instagram')
    source = models.CharField(max_length=255, db_index=True)
    when_banned = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)


class FlaggedUser(models.Model):
    '''This model represents a user that has been flagged for another user'''
    poster_sn = models.TextField()
    # User who flags another one
    source = models.CharField(max_length=255, db_index=True)
    who_flags = models.TextField()
    when_flagged = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s: %s (%s)' % (self.source, self.poster_sn, self.poster_id)


# Available moderation status
MODERATION_STATUS_REJECTED = 0
MODERATION_STATUS_APPROVED = 1
MODERATION_STATUS_PENDING = 2


MODERATION_STATUS = (
    (MODERATION_STATUS_APPROVED, "Approved"),
    (MODERATION_STATUS_PENDING, "Pending"),
    (MODERATION_STATUS_REJECTED, "Rejected"),
)


class ModeratedObjectManager(models.Manager):
    def get_for_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj.__class__)
        try:
            mo = ModeratedObject.objects.get(content_type=ct, object_pk=obj.pk)
            return mo
        except ModeratedObject.DoesNotExist:
            pass


class ModeratedObject(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'),
                                     related_name='content_type_set_for_%(class)s')
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    last_moderation_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=MODERATION_STATUS, default=MODERATION_STATUS_PENDING)
    reason = models.TextField(blank=True)
    flagged = models.BooleanField(default=False)
    flagged_by = models.TextField(blank=True)
    flagged_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Moderation Queue'
        verbose_name_plural = 'Moderation Queue'

    # Manager
    objects = ModeratedObjectManager()

    def __unicode__(self):
        return '[{0}] {1}'.format(self.get_status_display(), self.content_object)

    def get_absolute_url(self):
        if hasattr(self.content_object, "get_absolute_url"):
            return self.content_object.get_absolute_url()

    def get_status_display(self):
        return dict(MODERATION_STATUS)[self.status]

    def approve(self, reason=''):
        self._moderate(MODERATION_STATUS_APPROVED, reason)

    def reject(self, reason=''):
        self._moderate(MODERATION_STATUS_REJECTED, reason)

    def flag(self, username=''):
        self._mark_flag(True, username)

    def unflag(self, username=''):
        '''username should be an admin user'''
        self._mark_flag(False, username)

    def _moderate(self, status, reason=''):
        self.status = status
        self.last_moderation_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.reason = reason

        self.save()

    def _mark_flag(self, status, username=''):
        self.flagged = status
        self.flagged_by = username
        self.flagged_at = datetime.datetime.utcnow().replace(tzinfo=utc)

        self.save()

