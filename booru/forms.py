from django import forms
from .models import Post
from taggit.forms import TagField

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'custom-file-input'}), required=True)
    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    tags = TagField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    source = forms.URLField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Post
        fields = ["image", "sample", "preview", "source", "tags"]
