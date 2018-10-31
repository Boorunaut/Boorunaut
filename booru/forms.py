from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils import six
from taggit.forms import TagField, TagWidget
from taggit.utils import edit_string_for_tags

from .models import Category, Post, PostTag, Gallery


class TaggitAdminTextareaWidget(AdminTextareaWidget):
    # taken from taggit.forms.TagWidget
    def render(self, name, value, attrs=None, renderer=None):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
        return super(TaggitAdminTextareaWidget, self).render(name, value, attrs, renderer)

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    image = forms.ImageField(required=True)
    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    tags = TagField(required=True)
    source = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ["image", "sample", "preview", "source", "description", "tags"]

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget = forms.FileInput(attrs={'class': 'custom-file-input'})
        self.fields['source'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['tags'].widget = forms.TextInput(attrs={'class': 'form-control'})

class EditPostForm(forms.ModelForm):
    '''Form for editing an post.'''    
    rating = forms.IntegerField()
    parent = forms.IntegerField(required=False)
    source = forms.URLField(required=False)
    tags = TagField(required=False)

    class Meta:
        model = Post
        fields = ["rating", "parent", "source", "tags", "description"]

    def __init__(self, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.Select(attrs={'class': 'form-control'},
                                                    choices=Post.RATING_CHOICES)
        self.fields['parent'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        self.fields['source'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15})
        self.fields['tags'].widget = TaggitAdminTextareaWidget(attrs={'class': 'form-control'})

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
    associated_user_name = forms.CharField(required=False)
    aliases = TagField(required=False)

    def __init__(self, *args, **kwargs):
        super(TagEditForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['associated_link'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['associated_user_name'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['aliases'].widget = TaggitAdminTextareaWidget(attrs={'class': 'form-control',
                                                                        'data-role': 'tagsinput'})

    class Meta:
        model = PostTag
        fields = ["category", "description", "associated_link", "associated_user_name", "aliases"]

class ImplicationCreateForm(forms.Form):
    from_tag = forms.CharField(required=True)
    to_tag = forms.CharField(required=True)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ImplicationCreateForm, self).__init__(*args, **kwargs)
        self.fields['from_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['to_tag'].widget = forms.TextInput(attrs={'class': 'form-control'})

class MassRenameForm(forms.Form):
    filter_by = forms.CharField(required=False)
    when = forms.CharField(required=True)
    replace_with = forms.CharField(required=True)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MassRenameForm, self).__init__(*args, **kwargs)
        self.fields['filter_by'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['when'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['replace_with'].widget = forms.TextInput(attrs={'class': 'form-control'})

class GalleryCreateForm(forms.ModelForm):
    '''Form for creating an gallery.'''

    name = forms.CharField(required=True)
    description = forms.CharField(required=True)
    posts_ids = forms.CharField(required=True)

    class Meta:
        model = Gallery
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super(GalleryCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['posts_ids'].widget = forms.Textarea(attrs={'class': 'form-control'})

class GalleryEditForm(forms.ModelForm):
    '''Form for creating an gallery.'''

    name = forms.CharField(required=True)
    description = forms.CharField(required=True)
    posts_ids = forms.CharField(required=True)

    class Meta:
        model = Gallery
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super(GalleryEditForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['posts_ids'].widget = forms.Textarea(attrs={'class': 'form-control'})

class GalleryListSearchForm(forms.Form):
    '''Form searching galleries in the Gallery List.'''

    name = forms.CharField(required=False)    

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(GalleryListSearchForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control form-control-sm'})

class SiteConfigurationForm(forms.Form):
    site_title = forms.CharField(required=True)

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SiteConfigurationForm, self).__init__(*args, **kwargs)
        self.fields['site_title'].widget = forms.TextInput(attrs={'class': 'form-control'})
