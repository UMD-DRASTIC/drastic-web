"""Archive Forms

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django import forms
import json

from drastic.metadata import (
    get_collection_validator,
    get_resource_validator
)

from archive.widgets import JsonPairInputs


def get_groups():
    from drastic.models import Group
    return [(u'AUTHENTICATED@', 'authenticated@'),
            (u'ANONYMOUS@', 'anonymous@')] + [(g.name,g.name,) for g in Group.objects.all()]

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


class CollectionNewForm(CollectionForm):
    name = forms.CharField(label='Collection name', max_length=100, required=True)

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
    name = forms.CharField(label='Item name', max_length=100, required=True)
    file = forms.FileField(required=True)
