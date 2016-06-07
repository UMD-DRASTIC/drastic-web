from django import forms

class GroupForm(forms.Form):

    name = forms.CharField(label='Username', max_length=100, required=True)
 
class GroupAddForm(forms.Form):
 
    def __init__(self, users, *args, **kwargs):
        super(GroupAddForm, self).__init__(*args, **kwargs)
        self.fields['users'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                         choices=users)