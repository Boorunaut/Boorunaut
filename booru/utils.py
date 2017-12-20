from PIL import Image as ImagePIL

from io import StringIO
from django.core.files.base import ContentFile

sample_max_resolution = (850, None)
preview_max_resolution = (150, 150)

def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]

def space_joiner(tags):
    return ' '.join(t.name for t in tags)

def get_resized_image(image, max_resolution):
    pil_image = resize_image_to_maximum_size(image, max_resolution)
    return get_image_content_file_from_pil(pil_image, "JPEG")

def resize_image_to_maximum_size(image, max_resolution):
    ''' Resize image to be equal to the maximum resolution allowed (if less, it returns None). If one of the max_resolution's components is equal to None, it will be ignored.'''
    image = ImagePIL.open(image)
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

    if proportion == 1:
        return None
    else:
        new_size = (int(round(original_size[0] / proportion)), int(round(original_size[1] / proportion)))

        return image.resize(new_size)

def get_image_content_file_from_pil(pil_image, format):
    ''' Returns a ContentFile from the PIL.Image. '''
    f = StringIO()
    try:
        pil_image.save(f, format=format)
        s = f.getvalue()
    finally:
        f.close()

    return ContentFile(s)