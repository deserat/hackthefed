import logging

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

import factory

from moderation.models import (MODERATION_STATUS_APPROVED,
                               MODERATION_STATUS_PENDING,
                               MODERATION_STATUS_REJECTED,
                               ModeratedObject,
                               BannedUser,
                               FlaggedUser,
                               BannedWord,
                               signal_moderated_status_changed)

from moderation.moderators import UserModerator, WordModerator
from .models import Comment


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


class ModerationTestCase(TestCase):
    '''Testing generic moderation using a specific Comment object defined in
    models.py
    '''
    def _signal_handler(self, sender, **kwargs):
        self.assertEquals(kwargs['old_status'], MODERATION_STATUS_PENDING)
        self.assertEquals(kwargs['new_status'], MODERATION_STATUS_APPROVED)

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

    def test_status_changed(self):
        '''Tests if moderated_status_changed custom signal works properly
        '''
        signal_moderated_status_changed.connect(self._signal_handler, sender=ModeratedObject)
        self.comment.approve()
        self.assertEquals(self.comment.moderation_status, MODERATION_STATUS_APPROVED)


class BannedUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BannedUser

    poster_sn = 'username'
    source = 'Instagram poller'


class UserModeratorTestCase(TestCase):
    '''Testing User moderation
    '''
    def setUp(self):
        self.poster_sn = 'username'
        self.source = 'Instagram poller'
        self.user_for_flagging = 'username2'
        self.moderator = UserModerator()

    def test_get_banned_users(self):
        self.assertEquals(BannedUser.objects.all().count(), 0)

    def test_ban_user(self):
        self.moderator.ban_user(self.poster_sn, self.source)
        banned_users = BannedUser.objects.all().count()
        self.assertEquals(banned_users, 1)

    def test_unban_user(self):
        # Bans user
        self.moderator.ban_user(self.poster_sn, self.source)
        banned_users = BannedUser.objects.all().count()
        self.assertEquals(banned_users, 1)
        # Unbans user
        self.moderator.unban_user(self.poster_sn, self.source)
        banned_users = BannedUser.objects.all().count()
        self.assertEquals(banned_users, 0)

    def test_flag_user(self):
        self.moderator.flag_user(self.poster_sn, self.source, self.user_for_flagging)
        flagged_users = FlaggedUser.objects.all().count()
        self.assertEquals(flagged_users, 1)

    def test_unflag_user(self):
        # Flags user
        self.moderator.flag_user(self.poster_sn, self.source, self.user_for_flagging)
        flagged_users = FlaggedUser.objects.all().count()
        self.assertEquals(flagged_users, 1)
        # Unflags user
        self.moderator.unflag_user(self.poster_sn, self.source, self.user_for_flagging)
        flagged_users = FlaggedUser.objects.all().count()
        self.assertEquals(flagged_users, 0)

    def test_get_flagged_users(self):
        self.moderator.flag_user(self.poster_sn, self.source, self.user_for_flagging)
        self.assertEquals(FlaggedUser.objects.all().count(), 1)


class WordModeratorTestCase(TestCase):
    '''Testing Word moderation
    '''
    def setUp(self):
        self.banned_words = [u'ahole', u'amatuer', u'amcik']
        self.content = 'This text passes moderation'
        self.banned_content = 'Text ahole ameteur'
        self.moderator = WordModerator()

    def test_set_banned_words(self):
        self.moderator.set_banned_words(self.banned_words)
        banned_words = BannedWord.objects.all().count()
        self.assertEquals(banned_words, 3)

    def test_get_banned_words(self):
        self.moderator.set_banned_words(self.banned_words)
        banned_words = BannedWord.objects.all()
        self.assertEquals(banned_words.count(), 3)
        stored_banned_words = self.moderator.get_banned_words()
        for word_obj in banned_words:
            self.assertTrue(word_obj.word in stored_banned_words)

    def test_passes_moderation(self):
        self.moderator.set_banned_words(self.banned_words)
        self.assertTrue(self.moderator.passes_moderation(self.content))
        self.assertFalse(self.moderator.passes_moderation(self.banned_content))

    def test_is_banned_word(self):
        self.moderator.set_banned_words(self.banned_words)
        self.assertTrue(self.moderator.is_banned_word(self.banned_words[0]))
        self.assertFalse(self.moderator.is_banned_word(self.content.split()[0]))
