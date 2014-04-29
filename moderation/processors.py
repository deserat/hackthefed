#-----------------------------------------------------------------------
# These processors are complatible with social-aggregation
#
# Code in this file has been copied from 'moderation' and 'text' apps
# inside 'social-aggregation'
#-----------------------------------------------------------------------

import redis
import logging
import json

from django.conf import settings


logger = logging.getLogger(__name__)

redis_client = redis.Redis(settings.REDIS_HOST,
                           settings.REDIS_PORT,
                           0)

CACHE_TIME = 480


def _has_phrase(text, phrase_list):
    words = text.lower().split()
    if not text:
        msg = 'Discarding post for having no text'
        logger.info(msg)
        return False

    for phrase in phrase_list:
        phrase_words = phrase.split()
        # if phrase is only one word, use 'in'. otherwise, use find()
        if ((len(phrase_words) == 1 and phrase.lower() in words) or
                (len(phrase_words) > 1 and text.find(phrase.lower()) != -1)):
            return True
    else:
        # reached the end without finding any of our desired terms
        return False


def has_banned_term(source, source_url, data_item, **kwargs):
    """
    Processor to determine if incoming text data contains
    relevant terms.
    """
    processed_data = kwargs.get('processed_data')
    text = processed_data.get('all_text', '')
    banned_terms = redis_client.get('banned_words')
    if not banned_terms:
        logger.debug('No banned terms set for %s' % source.name)
        return False
    banned_terms = json.loads(banned_terms)
    if _has_phrase(text, banned_terms):
        msg = 'Discarding post for containing banned term'
        logger.debug(msg)
        return True
    return False


def has_banned_user(source, known_source, raw_data, **kwargs):
    processed_data = kwargs.get('processed_data', {})
    banned_sns = redis_client.get('banned_sns')
    banned_ids = redis_client.get('banned_ids')

    poster_sn = processed_data.get('poster_sn')
    poster_id = processed_data.get('poster_id')

    if poster_sn and banned_sns:
        if poster_sn in banned_sns:
            msg = 'Discarding post for having banned username'
            logger.info(msg)
            return True

    if poster_id and banned_ids:
        if poster_id in banned_ids:
            msg = 'Discarding post for having banned user id'
            logger.info(msg)
            return True
    return False


def passes_moderation(source, known_source, raw_data, **kwargs):
    processed_data = kwargs.get('processed_data', {})

    if (has_banned_term(source,
                        known_source,
                        raw_data,
                        processed_data=processed_data)
        or has_banned_user(source,
                           known_source,
                           raw_data,
                           processed_data=processed_data)):
        msg = 'Discarding post for having banned item'
        logger.info(msg)
        return False
    return True
