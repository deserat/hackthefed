from django.db import models


class BannedWordManager(models.Manager):
    def get_banned_words(self):
        '''Return a list of all banned words admin interface
        '''
        return self.values_list('word', flat=True)
