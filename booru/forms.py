from django import forms
from .models import Post
from taggit.forms import TagField, TagWidget

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

class EditPostForm(forms.ModelForm):
    '''Form for editing an post.'''    
    rating = forms.ChoiceField(choices=Post.RATING_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    parent = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    source = forms.URLField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    tags = TagField(widget=TagWidget(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Post
        fields = ["rating", "parent", "source", "tags"]