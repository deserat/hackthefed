import logging

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

import factory

from moderation.models import (MODERATION_STATUS_APPROVED,
                               MODERATION_STATUS_PENDING,
                               MODERATION_STATUS_REJECTED,
                               ModeratedObject)
from .models import Comment


# Setting logging for factory boy
logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)


class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment

    username = 'Username'
    content = 'This is a simple comment'


class ModerationTestCase(TestCase):
    def setUp(self):
        self.comment = CommentFactory.create()

    def test_approve(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.comment.approve()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_APPROVED)

    def test_reject(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.comment.reject()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_REJECTED)

    def test_flag(self):
        self.comment.flag()
        ct = ContentType.objects.get_for_model(Comment)
        mo = ModeratedObject.objects.get(content_type=ct, object_pk=self.comment.pk)
        self.assertEquals(mo.flagged, True)

    def test_unflag(self):
        self.comment.unflag()
        ct = ContentType.objects.get_for_model(Comment)
        mo = ModeratedObject.objects.get(content_type=ct, object_pk=self.comment.pk)
        self.assertEquals(mo.flagged, False)

    def test_is_flagged(self):
        ct = ContentType.objects.get_for_model(Comment)
        mo = ModeratedObject.objects.get(content_type=ct, object_pk=self.comment.pk)
        self.assertEquals(mo.flagged, False)
        self.assertEquals(self.comment.is_flagged(), False)

    def test_is_approved(self):
        self.comment.approve()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_APPROVED)
        self.assertEquals(self.comment.is_approved(), True)

    def test_is_rejected(self):
        self.comment.reject()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_REJECTED)
        self.assertEquals(self.comment.is_rejected(), True)

    def test_is_pending(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertEquals(self.comment.is_pending(), True)
