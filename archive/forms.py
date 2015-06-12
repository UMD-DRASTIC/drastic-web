from django import forms


class CollectionForm(forms.Form):
    name = forms.CharField(label='Collection name', max_length=100, required=True)
