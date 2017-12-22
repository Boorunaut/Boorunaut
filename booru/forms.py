from django import forms
from .models import Post

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'custom-file-input'}), required=True)
    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = Post
        fields = ["image", "sample", "preview", "source", "tags"]
