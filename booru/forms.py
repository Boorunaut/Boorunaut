from django import forms
from .models import Post, Category, PostTag
from taggit.forms import TagField, TagWidget

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    image = forms.ImageField(required=True)
    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    tags = TagField(required=True)
    source = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ["image", "sample", "preview", "source", "tags"]

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget = forms.FileInput(attrs={'class': 'custom-file-input'})
        self.fields['source'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['tags'].widget = forms.TextInput(attrs={'class': 'form-control'})

class EditPostForm(forms.ModelForm):
    '''Form for editing an post.'''    
    rating = forms.ChoiceField(choices=Post.RATING_CHOICES)
    parent = forms.IntegerField(required=False)
    source = forms.URLField(required=False)
    tags = TagField(required=False)

    class Meta:
        model = Post
        fields = ["rating", "parent", "source", "tags"]
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.NumberInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={'class': 'form-control'}),
        }

class TagListSearchForm(forms.Form):
    '''Form for creating an post.'''

    tags = forms.CharField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
                                    required=False, empty_label=None)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TagListSearchForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = forms.TextInput(attrs={'class': 'form-control form-control-sm'})

class TagEditForm(forms.ModelForm):
    '''Form for creating an post.'''

    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                    required=False, empty_label=None)

    class Meta:
        model = PostTag
        fields = ["category"]

class AliasCreateForm(forms.Form):
    from_tag = forms.CharField(required=True)
    to_tag = forms.CharField(required=True)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AliasCreateForm, self).__init__(*args, **kwargs)
        self.fields['from_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['to_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})

class ImplicationCreateForm(forms.Form):
    from_tag = forms.CharField(required=True)
    to_tag = forms.CharField(required=True)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ImplicationCreateForm, self).__init__(*args, **kwargs)
        self.fields['from_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['to_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})
