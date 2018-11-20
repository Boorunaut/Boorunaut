from django import forms
from booru.core.models import BannedHash


class BannedHashCreateForm(forms.ModelForm):
    '''Form for creating an BannedHash.'''

    class Meta:
        model = BannedHash
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(BannedHashCreateForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.TextInput(attrs={'class': 'form-control'})
