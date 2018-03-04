from io import BytesIO

from django.apps import apps
from django.core.files.base import ContentFile
from PIL import Image as ImagePIL

sample_max_resolution = (850, None)
preview_max_resolution = (150, 150)
jpg_quality = 80

def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]

def space_joiner(tags):
    return ' '.join(t.name for t in tags)

def get_sample(original_pil_image):
    ''' Returns the resized sample image. '''
    pil_image = reduce_image_to_maximum_size(original_pil_image, sample_max_resolution)

    if pil_image == None:
        return None

    pil_image = convert_to_rgb(pil_image)
    pil_image = convert_image_to_jpeg_bytes(pil_image)

    if pil_image:
        return convert_bytes_to_content_file(pil_image)
    else:
        return None

def get_preview(original_pil_image):
    ''' Returns the resized preview image. '''
    pil_image = reduce_image_to_maximum_size(original_pil_image, preview_max_resolution)

    if pil_image == None:
        return None

    pil_image = convert_to_rgb(pil_image)
    pil_image = convert_image_to_jpeg_bytes(pil_image)

    if pil_image:
        return convert_bytes_to_content_file(pil_image)
    else:
        return convert_bytes_to_content_file(original_pil_image)

def reduce_image_to_maximum_size(image, max_resolution):
    ''' Reduce the given image to be equal to the maximum resolution allowed (or None if already lower).
    If one of the max_resolution's components is equal to None, it will be ignored.'''
    original_size = image.size

    max_resolution = list(max_resolution)

    if max_resolution[0] == None:
        max_resolution[0] = original_size[0]

    if max_resolution[1] == None:
        max_resolution[1] = original_size[1]
    
    x_proportion = original_size[0] / max_resolution[0]
    y_proportion = original_size[1] / max_resolution[1]

    if x_proportion > y_proportion:
        proportion = x_proportion
    else:
        proportion = y_proportion

    if proportion <= 1:
        return None
    else:
        new_size = (int(round(original_size[0] / proportion)), int(round(original_size[1] / proportion)))

        return image.resize(new_size, ImagePIL.ANTIALIAS)

def convert_image_to_jpeg_bytes(pil_image):
    ''' Convert an PIL Image to JPEG and returns it as bytes. '''
    f = BytesIO()
    pil_image.save(f, format='JPEG', quality=jpg_quality)

    return f

def convert_bytes_to_content_file(pil_image_bytes):
    ''' Convert the bytes of an Image to a Django ContentFile. '''
    s = pil_image_bytes.getvalue()
    pil_image_bytes.close()

    return ContentFile(s)

def get_pil_image_if_valid(image):
    ''' Returns a PIL Image if the given image file is valid, returns False otherwise. '''
    try:
        return ImagePIL.open(image)
    except:
        return False

def convert_to_rgb(pil_image):
    ''' Converts an image from RGBA to RGB if needed. '''

    # Converting to RBG if RGBA
    if pil_image.mode == 'RGBA':
        pil_image.load()

        rgb_image = ImagePIL.new("RGB", pil_image.size, (255, 255, 255))
        rgb_image.paste(pil_image, mask=pil_image.split()[3]) # 3 is the alpha channel

        return rgb_image
    else:
        return pil_image


def verify_and_perform_aliases_and_implications(tag_name):
    Post = apps.get_model('booru', 'Post')
    Implication = apps.get_model('booru', 'Implication')
    Alias = apps.get_model('booru', 'Alias')
    posts = Post.objects.filter(tags__name__in=[tag_name])
    
    implications = Implication.objects.filter(from_tag__name=tag_name, approved=True)    
    alias = Alias.objects.filter(from_tag__name=tag_name, approved=True).first()

    if alias != None or implications.count() > 0:        
        for post in posts:
            if alias != None:
                post.tags.remove(alias.from_tag)
                post.tags.add(alias.to_tag)
            if implications.count() > 0:
                for implication in implications:
                    post.tags.add(implication.to_tag)

