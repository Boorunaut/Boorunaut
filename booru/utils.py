from io import BytesIO

import diff_match_patch as dmp_module
from django.apps import apps
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from PIL import Image as ImagePIL
from reversion.models import Version
from django.db.models import Q

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
    
    implications = Implication.objects.filter(from_tag__name=tag_name, status=1)    
    alias = Alias.objects.filter(from_tag__name=tag_name, status=1).first()

    if alias != None or implications.count() > 0:        
        for post in posts:
            if alias != None:
                post.tags.remove(alias.from_tag)
                post.tags.add(alias.to_tag)
            if implications.count() > 0:
                for implication in implications:
                    post.tags.add(implication.to_tag)

def get_diff(field_name, old_revision, new_revision):
    old_revision_field = old_revision.field_dict[field_name]
    new_revision_field = new_revision.field_dict[field_name]
    
def verify_and_substitute_alias(tag_string):
    Alias = apps.get_model('booru', 'Alias')
    verified_tags = []

    for tag in space_splitter(tag_string):
        raw_tag, operator = separate_tag_from_operator(tag)

        tag_alias = Alias.objects.filter(from_tag__slug=raw_tag)

        if tag_alias.exists():
            verified_tag = tag_alias.first().to_tag.slug
        else:
            verified_tag = raw_tag

        verified_tags.append(join_tag_and_operator(verified_tag, operator))
    
    return verified_tags

def compare_strings(old_string, new_string):
    """Splits a string by spaces, and compares the lists. Then, returns a dictionary containing the following results:

    `equal` is a list of words in common.

    `removed` is a list of words that ARE in old_string, but ARE NOT in new_string.

    `added` is a list of words that ARE NOT in old_string, but ARE in new_string.
    """
    old_string = old_string.split(" ")
    new_string = new_string.split(" ")

    equal_words = list(set(old_string).intersection(new_string))
    removed_words = list(set(old_string) - set(new_string))
    added_words = list(set(new_string) - set(old_string))

    return {"equal": equal_words, "removed": removed_words, "added": added_words}

'''def get_posts_from_tag_list(tag_list):
    Post = apps.get_model('booru', 'Post')

    queryset = Post.objects.all()

    for tag in tag_list:
        raw_tag, operator = separate_tag_from_operator(tag)

        queryset = queryset.filter(tags__slug__in=[tag])

    return queryset'''

def get_posts_from_tag_list(tag_list):
    Post = apps.get_model('booru', 'Post')

    queryset = Post.objects.all()

    q_object_and_or = Q()
    q_object_not = Q()

    for tag in tag_list:
        raw_tag, operator = separate_tag_from_operator(tag)

        q_template = Q(**{"tags__slug" : raw_tag})

        if operator == "":
            q_object_and_or.add(q_template, Q.AND)
        if operator == "~":
            q_object_and_or.add(q_template, Q.OR)
        if operator == "-":
            q_object_not.add(q_template, Q.OR)

    return queryset.filter(q_object_and_or).exclude(q_object_not)

'''def get_posts_with_any_tag_in_list(tag_list):
    Post = apps.get_model('booru', 'Post')

    for tag in tag_list:
        if PostTag.objects.filter(tags__slug__in=[tag]) == []:
            return Post.objects.none()

    return Post.objects.filter(tags__slug__in=tag_list)'''

def separate_tag_from_operator(tag):
    if tag[0] == "~" or tag[0] == "-" or tag[0] == "*":
        operator = tag[0]
        tag = tag[1:]
    else:
        operator = ''

    return tag, operator

def join_tag_and_operator(tag, operator):
    return operator + tag
    
