from django import forms
from .models import Post
from . import utils

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''

    sample = forms.ImageField(required=False)
    preview = forms.ImageField(required=False)
    
    def clean(self):
        self.cleaned_data = super(CreatePostForm, self).clean()

        image = self.cleaned_data.get("image")

        self.cleaned_data['sample'] = utils.get_resized_image(image, utils.sample_max_resolution)
        self.cleaned_data['preview'] = utils.get_resized_image(image, utils.preview_max_resolution)
        
        return self.cleaned_data

    class Meta:
        model = Post
        fields = ["image", "sample", "preview", "uploader", "source", "tags"]
