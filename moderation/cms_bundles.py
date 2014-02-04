from scarlet.cms import bundles, site, views

from .models import BannedWord, BannedUser, DefaultBannedWord, ModeratedObject
from .forms import SourceForm

import groups


class BannedWordBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    class Meta:
        model = BannedWord
        primary_model_bundle = True


class DefaultBannedWordBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    class Meta:
        model = DefaultBannedWord
        primary_model_bundle = True


class BannedUserBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = views.FormView(form_class=SourceForm,
                         fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source')}),))

    edit = views.FormView(form_class=SourceForm,
                          fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source')}),))

    class Meta:
        model = BannedUser
        primary_model_bundle = True


class ModeratedObjectBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = None

    class Meta:
        model = ModeratedObject
        primary_model_bundle = True


class ModerationBundle(bundles.BlankBundle):
    required_groups = (groups.MODERATOR,)

    dashboard = (
        ('banned_word',),
        ('banned_user',),
        ('default_banned_word',),
        ('moderated_content',),
    )

    banned_word = BannedWordBundle.as_subbundle(name='banned_word')
    default_banned_word = DefaultBannedWordBundle.as_subbundle(name='default_banned_word')
    banned_user = BannedUserBundle.as_subbundle(name='banned_user')
    moderated_content = ModeratedObjectBundle.as_subbundle(name='moderated_content')


site.register('moderation', ModerationBundle(name='moderation'), title='Moderation')
