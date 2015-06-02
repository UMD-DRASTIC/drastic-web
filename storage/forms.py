from django import forms

STORAGE_TYPE_CHOICES = [
    (1, "Hard Drive"),
    (2, "Cassandra Node"),
    (3, "Ceph"),
]

class StorageForm(forms.Form):
    name = forms.CharField(label='Storage Name', max_length=100, required=True)
    storage_type = forms.ChoiceField(label='Type', choices=STORAGE_TYPE_CHOICES)
    notes = forms.CharField(label='Notes', max_length=2048, widget=forms.Textarea, required=False)