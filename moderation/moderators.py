import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import BannedUser, BannedWord, DefaultBannedWord, FlaggedUser
from . import get_post_model


# Generic logger
logger = logging.getLogger(__name__)


class ModerationException(Exception):
    '''Generic Exception for moderation actions'''
    pass


class UserModerator(object):
    '''This class encapsulates actions for moderating users'''
    def get_banned_users(self):
        '''Returns all banned users'''
        return BannedUser.objects.all()

    def unban_user(self, poster_id, source, poster_sn=None):
        '''Unbans given user who has been previously banned'''
        try:
            banned_user = BannedUser.objects.get(poster_id=poster_id, source=source,
                                                 poster_sn=poster_sn)
            banned_user.delete()
        except BannedUser.DoesNotExists:
            logger.info(u"poster_id={0}, source={1} user wasn't banned".format(poster_id, source))

    def ban_user(self, poster_id, source, poster_sn=None):
        '''Bans a given user'''
        banned_user = BannedUser(poster_id=poster_id, source=source, poster_sn=poster_sn)
        banned_user.save()

    def flag_user(self, source, user_who, user_flagged):
        '''Flags a user'''
        flagged_user = FlaggedUser(poster_sn=user_flagged, source=source, who_flags=user_who)
        flagged_user.save()

    def unflag_user(self, source, user_who, user_flagged):
        '''Unflags a user'''
        try:
            flagged_user = FlaggedUser.objects.get(poster_sn=user_flagged,
                                                   source=source,
                                                   who_flags=user_who)
            flagged_user.delete()
        except FlaggedUser.DoesNotExists:
            logger.info(u"poster_id={0}, source={1} wasn't flagged".format(user_flagged, source))

    def get_flagged_users(self):
        '''Returns a list with users that has been flagged'''
        return FlaggedUser.objects.all()


class WordModerator(object):
    '''This class encapsulates actions for moderating words/posts'''
    def get_banned_words(self):
        '''Return a list of all banned words. It can include
        or not default banned words. Banned words are customizable from
        admin interface'''
        custom_banned_words = set([item for item in BannedWord.objects.values_list('word', flat=True)])
        default_banned_words = set([item for item in DefaultBannedWord.objects.values_list('word', flat=True)])
        return custom_banned_words.union(default_banned_words)

    def set_default_banned_words(self, banned_words):
        '''Sets a list with default banned words'''
        if not isinstance(banned_words, list):
            raise ModerationException('Please, use a list of banned words')

        default_banned_words = self.get_default_banned_words()
        for word in banned_words:
            if word not in default_banned_words:
                default_banned_word = DefaultBannedWord(word=word)
                default_banned_word.objects.save(word=word)

    def get_default_banned_words(self):
        '''Gets a list with default banned words'''
        return set(DefaultBannedWord.objects.values_list('word', flat=True))

    def get_posts_with_banned_words(self):
        '''Returns a list with all posts which contains banned words'''
        pass

    def passes_moderation(self, content):
        '''Returns True if content haven't any banned word, otherwise returns False'''
        banned_words = self.get_banned_words()
        words = set(content.split())
        if len(banned_words.intersection(words)) > 0:
            return True
        return False

    def ban_users_posts(self, sender, instance, created, **kwargs):
        '''Bans (delete) all posts of a given user. This method will be invoked from a Django signal'''
        source = instance.source
        poster_sn = instance.poster_sn
        poster_id = instance.poster_id
        users_posts = get_post_model().objects.filter(poster_id=poster_id,
                                                      poster_sn=poster_sn,
                                                      source__poller=source)
        users_posts.delete()

    def is_banned_word(self, word):
        '''Returns True if given word is a banned word'''
        banned_words = self.get_banned_words()
        return word in banned_words


class CommentModerator(object):
    '''This class moderates comments'''
    def __init__(self, comment):
        self.comment = comment

    def email_notification(self, content_object):
        '''Sends an email when a new comment has been posted'''
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        subject = "Moderation: New comment has been posted"
        message = "Object: {0}. Comment: {1}".format(content_object, self.comment)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

    def passes_moderation(self):
        '''Returns True if comment haven't any banned word, otherwise returns False'''
        word_moderator = WordModerator()
        return word_moderator.passes_moderation(self.comment)

# If user is banned then it deletes his saved posts
# moderation_action = ModerationAction()
# signals.post_save.connect(moderation_action.ban_users_posts, sender=BannedUser,
#                           dispatch_uid="Remove_banned_posts")
