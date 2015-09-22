from django import forms
import json

from archive.widgets import JsonPairInputs

from indigo.metadata import get_collection_validator, get_resource_validator

def get_groups():
    from indigo.models import Group
    return [(g.id,g.name,) for g in Group.objects.all()]

class CollectionForm(forms.Form):
    groups = get_groups

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

    def clean_metadata(self):
        data = self.cleaned_data['metadata']
        dct = {}
        for l in json.loads(data):
            dct[l[0]] = l[1]

        ok, errs = get_collection_validator().validate(dct)
        if not ok:
            raise forms.ValidationError([forms.ValidationError(e) for e in errs])
        return data


class ResourceForm(forms.Form):
    groups = get_groups

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

    def clean_metadata(self):
        data = self.cleaned_data['metadata']
        dct = {}
        for l in json.loads(data):
            dct[l[0]] = l[1]

        ok, errs = get_resource_validator().validate(dct)
        if not ok:
            raise forms.ValidationError([forms.ValidationError(e) for e in errs])
        return data


class ResourceNewForm(ResourceForm):
    name = forms.CharField(label='Resource name', max_length=100, required=True)
    file = forms.FileField(required=True)
