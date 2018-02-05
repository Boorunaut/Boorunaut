from django import forms
from .models import Post, Category, PostTag
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

class TagListSearchForm(forms.Form):
    '''Form for creating an post.'''

    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
                                    required=False, empty_label=None)

    class Meta:
        fields = "__all__"

class TagEditForm(forms.ModelForm):
    '''Form for creating an post.'''

    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                    required=False, empty_label=None)

    class Meta:
        model = PostTag
        fields = ["category"]
