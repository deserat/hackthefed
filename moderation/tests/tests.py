import logging

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command

import factory

from .models import Comment, Post
from moderation.models import (MODERATION_STATUS_PENDING,
                               MODERATION_STATUS_APPROVED,
                               MODERATION_STATUS_REJECTED,
                               BannedWord)

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


class BannedWordFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BannedWord

    word = 'ahole'


class ModerationTestCase(TestCase):
    '''Testing generic moderation using a specific Comment object defined in
    models.py
    '''
    def setUp(self):
        self.comment = CommentFactory.create()
        self.banned_content = 'This ahole is amatuer and amcik'
        # Creating banned words records
        self.banned_word_1 = BannedWordFactory.create()
        self.banned_word_2 = BannedWordFactory.create(word='amatuer')
        self.banned_word_3 = BannedWordFactory.create(word='amcik')

    def test_approve(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_date)
        self.comment.approve()
        comment = Comment.objects.get(id=1)
        self.assertEquals(comment.moderation_status, MODERATION_STATUS_APPROVED)
        self.assertIsNotNone(comment.moderation_last_date)

    def test_reject(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_date)
        self.comment.reject()
        comment = Comment.objects.get(id=1)
        self.assertEquals(comment.moderation_status, MODERATION_STATUS_REJECTED)
        self.assertIsNotNone(comment.moderation_last_date)

    def test_flag(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.assertIsNone(self.comment.moderation_last_flagged_date)
        self.comment.flag()
        # Object has not been saved by flag()
        comment = Comment.objects.get(id=1)
        self.assertEquals(comment.moderation_times_flagged, 1)
        self.assertIsNotNone(comment.moderation_last_flagged_date)

    def test_pre_moderation_approve(self):
        settings.PRE_MODERATE_Post_content_field = 'content'
        settings.PRE_MODERATE_Post = True
        self.post = PostFactory.create()
        self.assertEquals(self.post.moderation_status, MODERATION_STATUS_APPROVED)

    def test_pre_moderation_reject(self):
        settings.PRE_MODERATE_Post = True
        settings.PRE_MODERATE_Post_content_field = 'content'
        self.post = PostFactory.create(content=self.banned_content)
        self.assertEquals(self.post.moderation_status, MODERATION_STATUS_REJECTED)


class ModerationCommands(TestCase):
    '''Testing django custom commands for moderation
    '''
    def setUp(self):
        self.comment = CommentFactory.create()

    def test_approve_content(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        call_command('approve_content', 'tests.Comment')
        comment = Comment.objects.all()[0]
        self.assertEquals(comment.moderation_status, MODERATION_STATUS_APPROVED)

    def test_delete_rejected_content(self):
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_PENDING)
        self.comment.reject()
        comment = Comment.objects.get(id=1)
        self.assertEquals(comment.moderation_status, MODERATION_STATUS_REJECTED)
        call_command('delete_rejected_content', 'tests.Comment', no_confirmation=True)
        self.assertEquals(Comment.objects.all().count(), 0)
