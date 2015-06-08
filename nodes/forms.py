from django import forms


class NodeForm(forms.Form):
    name = forms.CharField(label='Node Name', max_length=100, required=True)
    address = forms.CharField(label='IP Address', max_length=100, required=True)
