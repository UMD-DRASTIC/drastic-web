"""Node Forms
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django import forms


class NodeForm(forms.Form):
    name = forms.CharField(label='Node Name', max_length=100, required=True)
    address = forms.CharField(label='IP Address', max_length=100, required=True)
