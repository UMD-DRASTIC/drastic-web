from django import forms

class UserForm(forms.Form):

    username = forms.CharField(label='Username', max_length=100, required=True)
    email = forms.CharField(label='Email', max_length=100, required=True)
    active = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    administrator = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)