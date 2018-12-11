import copy
import hashlib
import io
import tempfile
import time
import urllib.request

import diff_match_patch as dmp_module
import ffmpeg
import requests
from django import forms
from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from PIL import Image as ImagePIL
from rolepermissions.roles import RolesManager

sample_max_resolution = (850, None)
preview_max_resolution = (150, 150)

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

def get_video_preview(video):
    ''' Returns the resized preview image. '''
    in_filename = video.url[1:]
    frame_num = 1

    try:
        out, err = (
                ffmpeg
                .input(in_filename)
                .filter('select', 'gte(n,{})'.format(frame_num))
                .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
                .run(capture_stdout=True)
        )
        image = ImagePIL.open(io.BytesIO(out))
        return get_preview(image)
    except ffmpeg.Error as e:
        print(e.stderr)

    return None

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
    f = io.BytesIO()
    pil_image.convert('RGB').save(f, format='JPEG', quality=90, optimize=True)

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

def check_video_is_valid(video):
    ''' Returns True if it is a valid video file. Returns False otherwise. '''
    result = False
    try:
        with tempfile.NamedTemporaryFile() as f:
            f.write(video.file.getbuffer())
            f.seek(0)
            probe_result = ffmpeg.probe(f.name)

            if probe_result['format']['probe_score'] == 100:
                result = True
    except:
        pass    
    return result

def get_video_dimensions(video):
    result = ffmpeg.probe(video.url[1:])
    video_stream = next((stream for stream in result['streams'] if stream['codec_type'] == 'video'), None)
    return (video_stream['width'], video_stream['height'])

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


def verify_and_perform_implications(tag_name):
    Post = apps.get_model('booru', 'Post')
    Implication = apps.get_model('booru', 'Implication')
    
    implication = Implication.objects.filter(from_tag__name=tag_name, status=1).first()

    if implication is not None:
        from_tag = implication.from_tag
        to_tag = implication.to_tag

        missing_posts = Post.objects.filter(tags__name__in=[from_tag]).exclude(tags__name__in=[to_tag])

        if missing_posts.exists():
            for post in missing_posts:
                post.check_and_update_implications()

def get_diff(field_name, old_revision, new_revision):
    old_revision_field = old_revision.field_dict[field_name]
    new_revision_field = new_revision.field_dict[field_name]

    dmp = dmp_module.diff_match_patch()
    diff_field = dmp.diff_main(old_revision_field, new_revision_field)
    dmp.diff_cleanupSemantic(diff_field)
    diff_html = dmp.diff_prettyHtml(diff_field).replace('&para;', '') # Removes paragraph character 
                                                                      # added by the library.

    return diff_html

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

def parse_tags(tag_string):
    splitted_tags = space_splitter(tag_string)

    tag_info = {'~': [], '' : [], '-' : [], 'meta': []}

    for tag in splitted_tags:
        if tag.startswith('~') or tag.startswith('-'):
            tag_info[tag[0]].append(tag[1:])
        elif ':' in tag:
            tag_info['meta'].append(tag)
        else:
            tag_info[''].append(tag)

    return tag_info

def filter_posts(tag_list):
    from booru.models import Post
    from django.db.models import Q
    import re

    filtered_posts = Post.objects.all()
    filtered_posts = filtered_posts.order_by('-id')

    query = Q()

    for tag in tag_list['~']:
        query = query | Q(tags__name__in=[tag])
    
    filtered_posts = filtered_posts.filter(query)

    for tag in tag_list['']:
        filtered_posts = filtered_posts.filter(Q(tags__name__in=[tag]))

    for tag in tag_list['-']:
        filtered_posts = filtered_posts.exclude(Q(tags__name__in=[tag]))
    
    for tag in tag_list['meta']:
        score_match = re.match('score:(>|<|>=|<=|)((?:\+|-|)\d+)', tag)
        if tag == 'status:pending':
            filtered_posts = filtered_posts.filter(status=Post.PENDING)
        elif tag == 'status:approved':
            filtered_posts = filtered_posts.filter(status=Post.APPROVED)
        elif tag == 'status:hidden':
            filtered_posts = filtered_posts.filter(status=Post.HIDDEN)
        elif tag == 'status:deleted':
            filtered_posts = filtered_posts.filter(status=Post.DELETED)
        elif tag == 'rating:safe' or tag == 'rating:s':
            filtered_posts = filtered_posts.filter(rating=Post.SAFE)
        elif tag == 'rating:questionable' or tag == 'rating:q':
            filtered_posts = filtered_posts.filter(rating=Post.QUESTIONABLE)
        elif tag == 'rating:explicit' or tag == 'rating:e':
            filtered_posts = filtered_posts.filter(rating=Post.EXPLICIT)
        elif tag == 'rating:none' or tag == 'rating:n':
            filtered_posts = filtered_posts.filter(rating=Post.NONE)
        elif score_match:
            inequality = score_match[1]
            value = score_match[2]
            if inequality == '>':
                filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .filter(score_sum__gt=value)
            elif inequality == '>=':
                filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .filter(score_sum__gte=value)
            elif inequality == '<':
                filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .filter(score_sum__lt=value)
            elif inequality == '<=':
                filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .filter(score_sum__lte=value)
            else:
                if value == '0':
                    filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                .annotate(scorevote_count=Count('scorevote'))\
                                                .filter(Q(score_sum=value) | Q(scorevote_count=0))
                else:
                    filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .filter(score_sum=value)
        elif tag == 'order:score':
            filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .order_by('-score_sum')
        elif tag == 'order:score_asc':
            filtered_posts = filtered_posts.annotate(score_sum=Sum('scorevote__point'))\
                                                    .order_by('score_sum')
        elif tag == 'order:random':
            filtered_posts = filtered_posts.order_by('?')
    return filtered_posts.distinct()

def parse_and_filter_tags(tags):
    return filter_posts(parse_tags(tags))

def get_file_md5(file_data):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file_data.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_all_roles():
    roles_list = enumerate(list(RolesManager.get_roles_names()))
    roles = []
    for key, role in roles_list:
        roles.append((role, role.title()))
    return tuple(roles)

# Image utils
def download_and_return_BytesIO(url):
    r = requests.get(url, stream=True, timeout=settings.BOORUNAUT_INITIAL_UPLOAD_TIMEOUT)
    r.raise_for_status()

    if int(r.headers.get('Content-Length')) > settings.BOORUNAUT_MAX_SIZE_FILE:
        max_size_mb = settings.BOORUNAUT_MAX_SIZE_FILE / 1024 / 1024
        raise forms.ValidationError("Please upload a file with less than {} MB.".format(max_size_mb))

    size = 0
    start = time.time()

    img_bytesio = io.BytesIO()

    for chunk in r.iter_content(1024):
        if time.time() - start > settings.BOORUNAUT_MAXIMUM_UPLOAD_TIMEOUT:
            raise forms.ValidationError("Timeout of connection was reached.")

        size += len(chunk)
        if size > settings.BOORUNAUT_MAX_SIZE_FILE:
            raise forms.ValidationError("Please upload a file with less than {} MB.".format(max_size_mb))
        
        img_bytesio.write(chunk)
    return img_bytesio

def BytesIO_to_InMemoryUploadedFile(img_bytesio):
    img_size = img_bytesio.getbuffer().nbytes
    img_format = BytesIO_to_PIL(img_bytesio).format.lower()
    img_name = "tempfile." + img_format
    img_content_type = "image/" + img_format
    
    return InMemoryUploadedFile(
        img_bytesio,
        field_name='tempfile',
        name=img_name,
        content_type=img_content_type,
        size=img_size,
        charset='utf-8',
    )

def get_remote_image_as_InMemoryUploadedFile(url):
    image_bytesio = download_and_return_BytesIO(url)
    return BytesIO_to_InMemoryUploadedFile(image_bytesio)

def BytesIO_to_PIL(img_bytesio):
    img_copy = copy.copy(img_bytesio)
    return ImagePIL.open(img_copy)
