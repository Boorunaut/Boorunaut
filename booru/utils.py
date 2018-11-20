import hashlib
import tempfile
from io import BytesIO

import diff_match_patch as dmp_module
import ffmpeg
from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from PIL import Image as ImagePIL

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
        image = ImagePIL.open(BytesIO(out))
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
    f = BytesIO()
    pil_image.save(f, format='JPEG', quality=90, optimize=True)

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

    tag_info = {'~': [], '' : [], '-' : []}

    for tag in splitted_tags:
        if tag.startswith('~') or tag.startswith('-'):
            tag_info[tag[0]].append(tag[1:])
        else:
            tag_info[''].append(tag)

    return tag_info

def filter_posts(tag_list):
    from booru.models import Post
    from django.db.models import Q

    filtered_posts = Post.objects.all()

    query = Q()

    for tag in tag_list['~']:
        query = query | Q(tags__name__in=[tag])
    
    filtered_posts = filtered_posts.filter(query)

    for tag in tag_list['']:
        filtered_posts = filtered_posts.filter(Q(tags__name__in=[tag]))

    for tag in tag_list['-']:
        filtered_posts = filtered_posts.exclude(Q(tags__name__in=[tag]))

    return filtered_posts.distinct()

def parse_and_filter_tags(tags):
    return filter_posts(parse_tags(tags))

def get_file_md5(file_data):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file_data.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
