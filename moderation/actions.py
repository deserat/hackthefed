import logging

from django.db.models import signals

from .models import BannedUser, BannedWord, DefaultBannedWord
from . import get_post_model


class ModerationActionException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ModerationAction(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
            raise ModerationActionException('Please, use a list of banned words')

        default_banned_words = self.get_default_banned_words()
        for word in banned_words:
            if word not in default_banned_words:
                default_banned_word = DefaultBannedWord(word=word)
                default_banned_word.objects.save(word=word)

    def get_default_banned_words(self):
        '''Gets a list with default banned words'''
        return set(DefaultBannedWord.objects.values_list('word', flat=True))

    def get_banned_users(self):
        '''Returns all banned users'''
        return BannedUser.objects.all()

    def get_posts_with_banned_words(self):
        '''Returns a list with all posts which contains banned words'''
        pass

    def unban_user(self, poster_id, source, poster_sn=None):
        '''Unbans given user who has been previously banned'''
        try:
            banned_user = BannedUser.objects.get(poster_id=poster_id, source=source,
                                                 poster_sn=poster_sn)
            banned_user.delete()
        except BannedUser.DoesNotExists:
            self.logger.info(u"poster_id={0}, source={1} user wasn't banned".format(poster_id, source))

    def ban_user(self, poster_id, source, poster_sn=None):
        '''Bans a given user'''
        banned_user = BannedUser(poster_id=poster_id, source=source, poster_sn=poster_sn)
        banned_user.save()

    def passes_moderation(self, processed_data):
        '''Returns True if processed_data haven't any banned word, otherwise
        returns False'''
        banned_words = self.get_banned_words()
        words = set(processed_data.split())
        if len(banned_words.intersection(words)) > 0:
            return True
        return False

    def ban_users_posts(self, sender, instance, created, **kwargs):
        '''Bans (delete) all posts of a given user. This method will be invoked from a
        Django signal'''
        source = instance.source
        poster_sn = instance.poster_sn
        poster_id = instance.poster_id
        users_posts = get_post_model().objects.filter(poster_id=poster_id,
                                                      poster_sn=poster_sn,
                                                      source__poller=source)
        users_posts.delete()

    def is_banned_word(self, word):
        '''Return True if word is a banned word'''
        banned_words = self.get_banned_words()
        return word in banned_words


# If user is banned then it deletes his saved posts
moderation_action = ModerationAction()
signals.post_save.connect(moderation_action.ban_users_posts, sender=BannedUser,
                          dispatch_uid="Remove_banned_posts")
