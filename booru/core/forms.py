from django import forms
from booru.core.models import BannedHash, PostFlag


class BannedHashCreateForm(forms.ModelForm):
    '''Form for creating a BannedHash.'''

    class Meta:
        model = BannedHash
        fields = ["content"]

    def __init__(self, *args, **kwargs):
        super(BannedHashCreateForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = forms.TextInput(attrs={'class': 'form-control'})

class PostFlagCreateForm(forms.ModelForm):
    '''Form for creating a flag for post.'''

    class Meta:
        model = PostFlag
        fields = ['reason']

    def __init__(self, *args, **kwargs):
        super(PostFlagCreateForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget = forms.Textarea(attrs={'class': 'form-control', 'cols':15})
