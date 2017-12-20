from django import forms
from .models import Post

class CreatePostForm(forms.ModelForm):
    '''Form for creating an post.'''
    
    def clean(self):
        self.cleaned_data = super(CreatePostForm, self).clean()
        icon = self.cleaned_data.get("image")
        self.cleaned_data['icon'] = None
        
        
        if icon_url and not icon:
            megabyte_limit = sayba.image_utils.get_megabyte_limit()

            image_content = sayba.image_utils.download_external_image(icon_url)

            if image_content == None:
                raise forms.ValidationError(
                    "A imagem inserida é muito pesada (maior que %sMB)." % str(megabyte_limit / 1048576)
                )
            elif image_content == False:
                raise forms.ValidationError(
                    "A imagem inserida é inválida."
                )
            else:
                image_content.name = icon_url
                self.cleaned_data['icon'] = image_content

        return self.cleaned_data

    class Meta:
        model = Post
        fields = ["image", "uploader", "source", "tags"]
