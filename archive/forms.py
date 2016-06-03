"""Archive Forms

Copyright 2015 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from django import forms
import json

from indigo.metadata import (
    get_collection_validator,
    get_resource_validator
)

from archive.widgets import JsonPairInputs


def get_groups():
    from indigo.models import Group
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
