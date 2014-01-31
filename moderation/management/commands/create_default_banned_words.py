import os
import json

from fabric.colors import green

from django.core.management.base import BaseCommand, CommandError

from moderation.models import DefaultBannedWord
from moderation.moderators import WordModerator


FIXTURE_FILE = os.path.abspath(os.path.dirname(__file__)) + '/../../fixtures/moderation_banned_words.json'


class Command(BaseCommand):
    help = 'Creates default banned words'

    def handle(self, *args, **options):
        word_moderator = WordModerator()
        banned_words = word_moderator.get_banned_words()
        new_words = 0
        try:
            fixture = open(FIXTURE_FILE)
            json_data = json.load(fixture)
            for item in json_data:
                word = item['fields']['word']
                if not word in banned_words:
                    default_word = DefaultBannedWord(word=word)
                    default_word.save()
                    new_words += 1
        except IOError:
            raise CommandError("Error opening {0} file".format(FIXTURE_FILE))
        print(green("{0} new words has been added as default banned words.".format(new_words)))
