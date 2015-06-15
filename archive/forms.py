from django import forms

from archive.widgets import JsonPairInputs

class CollectionForm(forms.Form):
    name = forms.CharField(label='Collection name', max_length=100, required=True)
    metadata = forms.CharField(label="Metadata", required=False,
                               widget=JsonPairInputs())