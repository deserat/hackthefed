from django import forms

from social_aggregation import get_pollers


SOURCES = [(x.name, x.title) for x in sorted(get_pollers(), key=lambda x: x.title)]


class SourceForm(forms.ModelForm):
    source = forms.ChoiceField(choices=SOURCES)
