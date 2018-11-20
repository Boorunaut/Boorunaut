from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils import six
from taggit.forms import TagField, TagWidget
from taggit.utils import edit_string_for_tags

from booru import utils
from booru.account.forms import UsernameExistsField
from booru.account.models import Timeout
from booru.core.models import BannedHash
from booru.models import Category, Gallery, Post, PostTag


class TaggitAdminTextareaWidget(AdminTextareaWidget):
    # taken from taggit.forms.TagWidget
    def render(self, name, value, attrs=None, renderer=None):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
        return super(TaggitAdminTextareaWidget, self).render(name, value, attrs, renderer)

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    media = forms.FileField(required=True)
    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    tags = TagField(required=True)
    source = forms.URLField(required=False)
    rating = forms.IntegerField()

    class Meta:
        model = Post
        fields = ["media", "sample", "preview", "rating", "source", "description", "tags"]

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['media'].widget = forms.FileInput(attrs={'class': 'custom-file-input'})
        self.fields['source'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['rating'].widget = forms.Select(attrs={'class': 'form-control'},
                                                    choices=Post.RATING_CHOICES)
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['tags'].widget = forms.TextInput(attrs={'class': 'form-control'})

    def clean( self ): 
        cleaned_data = self.cleaned_data
        media_file = cleaned_data.get( "media" )

        if media_file is None:
            raise forms.ValidationError("Please select a image or video")
        
        if not utils.get_pil_image_if_valid(media_file):
            if not utils.check_video_is_valid(media_file):
                raise forms.ValidationError("Please upload a valid image or video.")

        md5_checksum = utils.get_file_md5(media_file)

        if BannedHash.objects.filter(content=md5_checksum).exists():
            raise forms.ValidationError("This file is not allowed to be uploaded. Contact the staff.")

        return cleaned_data    

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

class BanUserForm(forms.ModelForm):
    username = UsernameExistsField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    expiration = forms.DateTimeField(required=True, input_formats=['%m/%d/%Y'])
    reason = forms.CharField(required=True)

    class Meta:
        model = Timeout
        fields = ["username", "expiration", "reason"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
        self.fields['expiration'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'month/day/year'})
        self.fields['reason'].widget = forms.TextInput(attrs={'class': 'form-control'})

class GalleryCreateForm(forms.ModelForm):
    '''Form for creating an gallery.'''

    name = forms.CharField(required=True)
    description = forms.CharField(required=False)
    posts_ids = forms.CharField(required=False)

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
    site_title = forms.CharField(required=True, help_text="The name of the website to be shown.")
    terms_of_service = forms.CharField(required=False)
    privacy_policy = forms.CharField(required=False)
    announcement = forms.CharField(required=False, help_text="The contents here will be shown on the top of the website for all users. Markdown is enabled.")
    custom_code = forms.CharField(required=False, help_text="WARNING: This executes arbitrary HTML code on the top of the site for all users. Be careful of the contents here.")

    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SiteConfigurationForm, self).__init__(*args, **kwargs)
        self.fields['site_title'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['terms_of_service'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['privacy_policy'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['announcement'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['custom_code'].widget = forms.Textarea(attrs={'class': 'form-control'})
