from django.db.utils import OperationalError

from .models import BannedWord

try:
    banned_words = BannedWord.get_banned_words()
except OperationalError:
    # Table has not been created yet
    pass
