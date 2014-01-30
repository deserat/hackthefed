import os
import json

from django.core.management.base import BaseCommand, CommandError

from moderation.models import DefaultBannedWord
from moderation.actions import ModerationAction


FIXTURE_FILE = os.path.abspath(os.path.dirname(__file__)) + '/../../fixtures/moderation_banned_words.json'


class Command(BaseCommand):
    help = 'Creates default banned words'

    def handle(self, *args, **options):
        actions = ModerationAction()
        banned_words = actions.get_banned_words()
        try:
            fixture = open(FIXTURE_FILE)
            json_data = json.load(fixture)
            for item in json_data:
                word = item['fields']['word']
                if not word in banned_words:
                    default_word = DefaultBannedWord(word=word)
                    default_word.save()
        except IOError:
            raise CommandError("Error opening {0} file".format(FIXTURE_FILE))

        return
