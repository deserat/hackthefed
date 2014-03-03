import datetime

from django.db.utils import OperationalError
from django.db.models import F
from django.utils.timezone import utc

from .models import BannedWord, BannedUser, FlaggedUser


try:
    banned_words = BannedWord.get_banned_words()
except OperationalError:
    # Table has not been created yet
    pass


def flag_user(poster_sn, poster_id='', source=''):
    '''Flags a user'''
    updated = FlaggedUser.objects.filter(poster_sn=poster_sn,
        poster_id=poster_id,
        source=source).update(times_flagged=F('times_flagged') + 1,
        last_flagged_date=datetime.datetime.utcnow().replace(tzinfo=utc))

    if not updated:
        FlaggedUser.objects.create(poster_sn=poster_sn, poster_id=poster_id, source=source, times_flagged=1, last_flagged_date=datetime.datetime.utcnow().replace(tzinfo=utc))


def unflag_user(poster_sn, poster_id='', source=''):
    '''Deletes a flagged user'''
    FlaggedUser.objects.filter(poster_sn=poster_sn,
        poster_id=poster_id,
        source=source).delete()


def ban_user(poster_sn, poster_id='', source=''):
    '''Bans a user'''
    updated = BannedUser.objects.filter(poster_sn=poster_sn,
        poster_id=poster_id,
        source=source).update(times_banned=F('times_banned') + 1,
        last_banned_date=datetime.datetime.utcnow().replace(tzinfo=utc))

    if not updated:
        BannedUser.objects.create(poster_sn=poster_sn, poster_id=poster_id, source=source, times_banned=1, last_banned_date=datetime.datetime.utcnow().replace(tzinfo=utc))


def unban_user(poster_sn, poster_id='', source=''):
    '''Deletes a banned user'''
    BannedUser.objects.filter(poster_sn=poster_sn,
        poster_id=poster_id,
        source=source).delete()
