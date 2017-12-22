from PIL import Image as ImagePIL

from io import BytesIO
from django.core.files.base import ContentFile

sample_max_resolution = (850, None)
preview_max_resolution = (150, 150)
jpg_quality = 90

def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]

def space_joiner(tags):
    return ' '.join(t.name for t in tags)

def get_sample(original_pil_image):
    ''' Returns the resized sample image. '''
    pil_image = reduce_image_to_maximum_size(original_pil_image, sample_max_resolution)

    if pil_image:
        return get_converted_image(pil_image)
    else:
        return None

def get_preview(original_pil_image):
    ''' Returns the resized preview image. '''
    pil_image = reduce_image_to_maximum_size(original_pil_image, preview_max_resolution)

    if pil_image:
        return get_converted_image(pil_image)
    else:
        return get_converted_image(original_pil_image)

def get_converted_image(pil_image):
    ''' Convert the PIL Image to ImageContent in RGB mode and returns it. '''
    # Converting to RBG if RGBA
    if pil_image.mode == 'RGBA':
        pil_image = convert_to_rgb(pil_image)

    return convert_to_content_file(pil_image, 'JPEG')

def reduce_image_to_maximum_size(image, max_resolution):
    ''' Reduce image to be equal to the maximum resolution allowed (if less, it returns None). If one of the max_resolution's components is equal to None, it will be ignored.'''
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

        return image.resize(new_size)

def convert_to_content_file(pil_image, img_format):
    ''' Returns a ContentFile from a PIL Image. '''    
    if pil_image == None:
        return None

    f = BytesIO()
    pil_image.save(f, img_format, quality=jpg_quality)

    s = f.getvalue()
    f.close()

    return ContentFile(s)

def get_pil_image_if_valid(image):
    ''' Returns a PIL Image if the image is valid, return False otherwise. '''
    try:
        return ImagePIL.open(image)
    except:
        return False

def convert_to_rgb(pil_image):
    ''' Converts a RGBA image to RGB. '''
    pil_image.load()

    rgb_image = ImagePIL.new("RGB", pil_image.size, (255, 255, 255))
    rgb_image.paste(pil_image, mask=pil_image.split()[3]) # 3 is the alpha channel

    return rgb_image