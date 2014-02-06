from django import forms

from scarlet.cms import bundles, site, views
from scarlet.cms.forms import BaseFilterForm


from .models import BannedWord, BannedUser, FlaggedUser, ModeratedObject, MODERATION_STATUS
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


class ModeratedObjectListView(views.ListView):
    def get_queryset(self):
        self.queryset = ModeratedObject.objects.all()
        return super(ModeratedObjectListView, self).get_queryset()


class ModeratedObjectFilterForm(BaseFilterForm):
    status = forms.ChoiceField(choices=MODERATION_STATUS)

    def __init__(self, *args, **kwargs):
        super(ModeratedObjectFilterForm, self).__init__(*args, **kwargs)
        self.search_fields = ('status', )

    class Meta:
        model = ModeratedObject


class ModeratedObjectBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    def render_flagged(self):
        if self.flagged:
            return 'Yes'
        return 'No'
    render_flagged.short_description = 'Flagged'

    def render_last_moderation_date(self):
        return self.last_moderation_at
    render_last_moderation_date.short_description = 'Date'

    add = None

    main = ModeratedObjectListView(
        display_fields=('status', 'content_object', render_flagged, render_last_moderation_date),
        filter_form=ModeratedObjectFilterForm,
        can_sort=True,
        paginate_by=30,
    )

    class Meta:
        model = ModeratedObject
        primary_model_bundle = True


class ModerationBundle(bundles.BlankBundle):
    required_groups = (groups.MODERATOR,)

    dashboard = (
        ('banned_word', ),
        ('banned_user', ),
        ('flagged_user', ),
        ('moderated_content', ),
    )

    banned_word = BannedWordBundle.as_subbundle(name='banned_word')
    banned_user = BannedUserBundle.as_subbundle(name='banned_user')
    flagged_user = FlaggedUserBundle.as_subbundle(name='flagged_user')
    moderated_content = ModeratedObjectBundle.as_subbundle(name='moderated_content')


site.register('moderation', ModerationBundle(name='moderation'), title='Moderation')
