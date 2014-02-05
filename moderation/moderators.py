import logging

from django.conf import settings
from django.core.mail import send_mail

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

    def unban_user(self, poster_id, source, poster_sn=None):
        '''Unbans given user who has been previously banned
        '''
        try:
            banned_user = BannedUser.objects.get(poster_id=poster_id, source=source,
                                                 poster_sn=poster_sn)
            banned_user.delete()
        except BannedUser.DoesNotExists:
            logger.info(u"poster_id={0}, source={1} user wasn't banned".format(poster_id, source))

    def ban_user(self, poster_id, source, poster_sn=None):
        '''Bans a given user
        '''
        banned_user = BannedUser(poster_id=poster_id, source=source, poster_sn=poster_sn)
        banned_user.save()

    def flag_user(self, source, user_who, user_flagged):
        '''Flags a user
        '''
        flagged_user = FlaggedUser(poster_sn=user_flagged, source=source, who_flags=user_who)
        flagged_user.save()

    def unflag_user(self, source, user_who, user_flagged):
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

        banned_words = self.get_banned_words()
        for word in banned_words:
            if word not in banned_words:
                banned_words = BannedWord(word=word)
                banned_words.objects.save(word=word)

    def get_posts_with_banned_words(self):
        '''Returns a list with all posts which contains banned words
        '''
        pass

    def passes_moderation(self, content):
        '''Returns True if content haven't any banned word, otherwise returns False
        '''
        banned_words = self.get_banned_words()
        words = set(content.split())
        if len(banned_words.intersection(words)) > 0:
            return True
        return False

    def is_banned_word(self, word):
        '''Returns True if given word is a banned word
        '''
        banned_words = self.get_banned_words()
        return word in banned_words


class CommentModerator(object):
    '''This class moderates comments
    '''
    def email_notification(self, comment, content_object):
        '''Sends an email when a new comment has been posted
        '''
        recipient_list = [manager_tuple[1] for manager_tuple in settings.MANAGERS]
        subject = "Moderation: New comment has been posted"
        message = "Object: {0}. Comment: {1}".format(content_object, comment)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)

    def passes_moderation_receiver(self, sender, **kwargs):
        '''Connect this receiver to you signal after saving a comment.
        If current instance doesn't pass moderation then delete it.
        Sender instance must contain a 'comment' field

        How to connect your model to this receiver:

        moderator = CommentModerator()
        post_save.connect(moderator.passes_moderation_receiver, sender=your_model)

        '''
        instance = kwargs['instance']
        word_moderator = WordModerator()
        if not word_moderator.passes_moderation(instance.comment):
            instance.delete()

    def passes_moderation(self, comment):
        '''Returns True if comment haven't any banned word, otherwise returns False
        '''
        word_moderator = WordModerator()
        return word_moderator.passes_moderation(comment)
