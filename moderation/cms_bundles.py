from django import forms

from scarlet.cms import bundles, site, views
from scarlet.cms.forms import BaseFilterForm


from .models import BannedWord, BannedUser, FlaggedUser
from .forms import SourceForm

import groups


class BannedWordListView(views.ListView):
    def get_queryset(self):
        self.queryset = BannedWord.objects.all()
        return super(BannedWordListView, self).get_queryset()


class BannedWordBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    main = BannedWordListView(
        paginate_by=30,
    )

    class Meta:
        model = BannedWord
        primary_model_bundle = True


class BannedUserListView(views.ListView):
    def get_queryset(self):
        self.queryset = BannedUser.objects.all()
        return super(BannedUserListView, self).get_queryset()


class BannedUserFilterForm(BaseFilterForm):
    poster_sn = forms.CharField(label='poster_sn', max_length=255, required=False)
    source = forms.CharField(label='source', max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super(BannedUserFilterForm, self).__init__(*args, **kwargs)
        self.search_fields = ('poster_sn', 'source')

    class Meta:
        model = BannedUser


class BannedUserBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source')}),)
    )

    edit = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source')}),)
    )

    main = BannedUserListView(
        display_fields=('poster_sn', 'source', 'when_banned'),
        filter_form=BannedUserFilterForm,
        paginate_by=30,
    )

    class Meta:
        model = BannedUser
        primary_model_bundle = True


class FlaggedUserListView(views.ListView):
    def get_queryset(self):
        self.queryset = FlaggedUser.objects.all()
        return super(FlaggedUserListView, self).get_queryset()


class FlaggedUserBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source', 'who_flags')}),)
    )

    edit = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source', 'who_flags')}),)
    )

    main = FlaggedUserListView(
        display_fields=('poster_sn', 'source', 'when_flagged', 'who_flags'),
        paginate_by=30,
    )

    class Meta:
        model = FlaggedUser
        primary_model_bundle = True


class ModerationBundle(bundles.BlankBundle):
    required_groups = (groups.MODERATOR,)

    dashboard = (
        ('banned_word', ),
        ('banned_user', ),
        ('flagged_user', ),
    )

    banned_word = BannedWordBundle.as_subbundle(name='banned_word')
    banned_user = BannedUserBundle.as_subbundle(name='banned_user')
    flagged_user = FlaggedUserBundle.as_subbundle(name='flagged_user')
