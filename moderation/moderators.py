import logging

from .models import BannedUser, BannedWord, FlaggedUser


# Generic logger
logger = logging.getLogger(__name__)


class ModerationException(Exception):
    '''Generic Exception for moderation actions
    '''
    pass


class UserModerator(object):
    '''This class encapsulates actions for moderating users
    '''
    def get_banned_users(self):
        '''Returns all banned users
        '''
        return BannedUser.objects.all()

    def unban_user(self, poster_sn, source, poster_id=''):
        '''Unbans given user who has been previously banned
        '''
        try:
            banned_user = BannedUser.objects.get(poster_id=poster_id, source=source,
                                                 poster_sn=poster_sn)
            banned_user.delete()
        except BannedUser.DoesNotExists:
            logger.info(u"poster_id={0}, source={1} user wasn't banned".format(poster_id, source))

    def ban_user(self, poster_sn, source, poster_id=''):
        '''Bans a given user
        '''
        banned_user = BannedUser(poster_id=poster_id, source=source, poster_sn=poster_sn)
        banned_user.save()

    def flag_user(self, user_who, source, user_flagged):
        '''Flags a user
        '''
        flagged_user = FlaggedUser(poster_sn=user_flagged, source=source, who_flags=user_who)
        flagged_user.save()

    def unflag_user(self, user_who, source, user_flagged):
        '''Unflags a user
        '''
        try:
            flagged_user = FlaggedUser.objects.get(poster_sn=user_flagged,
                                                   source=source,
                                                   who_flags=user_who)
            flagged_user.delete()
        except FlaggedUser.DoesNotExists:
            logger.info(u"poster_id={0}, source={1} wasn't flagged".format(user_flagged, source))

    def get_flagged_users(self):
        '''Returns a list with users that has been flagged
        '''
        return FlaggedUser.objects.all()


class WordModerator(object):
    '''This class encapsulates actions for moderating words/posts
    '''
    def get_banned_words(self):
        '''Return a list of all banned words admin interface
        '''
        return BannedWord.objects.values_list('word', flat=True)

    def set_banned_words(self, banned_words):
        '''Sets a list with banned words
        '''
        if not isinstance(banned_words, list):
            raise ModerationException('Please, use a list of banned words')

        stored_banned_words = self.get_banned_words()
        for word in banned_words:
            if word not in stored_banned_words:
                banned_words = BannedWord(word=word)
                banned_words.save()

    def get_posts_with_banned_words(self):
        '''Returns a list with all posts which contains banned words
        '''
        pass

    def passes_moderation(self, content):
        '''Returns True if content haven't any banned word, otherwise returns False
        '''
        banned_words = set(self.get_banned_words())
        words = set(content.split())
        if len(words.intersection(banned_words)) > 0:
            return False
        return True

    def is_banned_word(self, word):
        '''Returns True if given word is a banned word
        '''
        banned_words = self.get_banned_words()
        return word in banned_words
