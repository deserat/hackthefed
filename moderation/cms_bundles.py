from django import forms

from scarlet.cms import bundles, views
from scarlet.cms.forms import BaseFilterForm
from scarlet.cms.actions import ActionView

from .models import (
    BannedWord, BannedUser, FlaggedUser, MODERATION_STATUS_APPROVED,
    MODERATION_STATUS_REJECTED, MODERATION_STATUS
)
from .forms import SourceForm

import groups


#---------------------
# BannedWord
#---------------------

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

#---------------------
# BannedUser
#---------------------


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

#---------------------
# FlaggedUser
#---------------------


class FlaggedUserListView(views.ListView):
    def get_queryset(self):
        self.queryset = FlaggedUser.objects.all()
        return super(FlaggedUserListView, self).get_queryset()


class FlaggedUserBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source', )}),)
    )

    edit = views.FormView(
        form_class=SourceForm,
        fieldsets=((None, {'fields': ('poster_sn', 'poster_id', 'source', )}),)
    )

    main = FlaggedUserListView(
        display_fields=('poster_sn', 'source', 'when_flagged', ),
        paginate_by=30,
    )

    class Meta:
        model = FlaggedUser
        primary_model_bundle = True

#---------------------------
# Moderation specific model
#---------------------------


class ModerationFilterForm(BaseFilterForm):
    m_status = forms.ChoiceField(choices=MODERATION_STATUS, required=False, label=u'Status')

    def __init__(self, *args, **kwargs):
        super(ModerationFilterForm, self).__init__(*args, **kwargs)
        self.search_fields = ('m_status', )


class ModerationAction(ActionView):

    def process_action(self, request, queryset):
        count = queryset.update(moderation_status=self.status)
        url = self.get_done_url()
        msg = self.write_message(message='{0} {1}'.format(count, self.final_message))
        return self.render(request, redirect_url=url, message=msg, collect_render_data=False)


class ApproveAction(ModerationAction):
    confirmation_message = 'This will approve these records:'
    short_description = 'Approve records'
    action_name = 'Approve'
    final_message = 'record/s have been approved.'
    status = MODERATION_STATUS_APPROVED


class RejectAction(ModerationAction):
    confirmation_message = 'This will reject these records:'
    short_description = 'Reject records'
    action_name = 'Reject'
    final_message = 'records/s have been rejected.'
    status = MODERATION_STATUS_REJECTED


class ModerationListView(views.ListView):
    def __init__(self, *args, **kwargs):
        super(ModerationListView, self).__init__(*args, **kwargs)
        if 'model' in kwargs:
            self.model = kwargs['model']

    def get_queryset(self):
        self.queryset = self.model.objects.all()
        return super(ModerationListView, self).get_queryset()


class ModerationBundle(bundles.Bundle):
    required_groups = bundles.PARENT

    add = None
    delete = None
    approve = ApproveAction()
    reject = RejectAction()

    def render_m_times_moderated(self):
        return self.m_times_moderated
    render_m_times_moderated.short_description = 'Times moderated'

    def m_times_flagged(self):
        return self.m_times_flagged
    m_times_flagged.short_description = 'Times flagged'

    def render_m_status(self):
        return self.get_m_status_display()
    render_m_status.short_description = 'Moderation status'

    display_fields = (render_m_times_moderated,
                      m_times_flagged,
                      render_m_status, )

    main = ModerationListView(
        display_fields=display_fields,
        paginate_by=30,
        filter_form=ModerationFilterForm,
    )

    class Meta:
        action_views = ('approve', 'reject', )


#---------------------------
# Main moderation bundle
#---------------------------


class ModerationMainBundle(bundles.BlankBundle):
    required_groups = (groups.MODERATOR,)

    dashboard = (
        ('banned_word', ),
        ('banned_user', ),
        ('flagged_user', ),
    )

    banned_word = BannedWordBundle.as_subbundle(name='banned_word')
    banned_user = BannedUserBundle.as_subbundle(name='banned_user')
    flagged_user = FlaggedUserBundle.as_subbundle(name='flagged_user')
