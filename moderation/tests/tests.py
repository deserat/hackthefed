import logging

from django.test import TestCase

import factory

from .models import Comment, Post
from moderation.models import MODERATION_STATUS_PENDING, MODERATION_STATUS_APPROVED, MODERATION_STATUS_REJECTED


# Setting logging for factory boy
logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)

# Generic logger
logger_g = logging.getLogger(__name__)


class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment

    username = 'Username'
    content = 'This is a simple comment'


class PostFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Post

    content = 'This is a simple content for posting'


class ModerationTestCase(TestCase):
    '''Testing generic moderation using a specific Comment object defined in
    models.py
    '''
    def setUp(self):
        self.comment = CommentFactory.create()

    def test_approve(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_date)
        self.comment.approve()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_APPROVED)
        self.assertIsNotNone(self.comment.moderation_last_date)

    def test_reject(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_date)
        self.comment.reject()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_REJECTED)
        self.assertIsNotNone(self.comment.moderation_last_date)

    def test_flag(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_flagged_date)
        self.comment.flag()
        self.assertEquals(self.comment.moderation_times_flagged, 1)
        self.assertIsNotNone(self.comment.moderation_last_flagged_date)
