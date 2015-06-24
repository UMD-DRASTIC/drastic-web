from django import forms

from archive.widgets import JsonPairInputs

def get_groups():
    from indigo.models import Group
    return [(g.id,g.name,) for g in Group.objects.all()]

class CollectionForm(forms.Form):
    groups = get_groups

    name = forms.CharField(label='Collection name', max_length=100, required=True)
    metadata = forms.CharField(label="Metadata", required=False,
                               widget=JsonPairInputs())
    read_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    write_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    edit_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    delete_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)


class ResourceForm(forms.Form):
    groups = get_groups

    name = forms.CharField(label='Resource name', max_length=100, required=True)
    file = forms.FileField(required=False)
    metadata = forms.CharField(label="Metadata", required=False,
                               widget=JsonPairInputs())
    read_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    write_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    edit_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)
    delete_access = forms.MultipleChoiceField(required=False,
                                    widget=forms.CheckboxSelectMultiple(),
                                    choices=groups,)