from PIL import Image as ImagePIL

sample_max_resolution = (850, 0)
preview_max_resolution = (150, 150)

def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]

def space_joiner(tags):
    return ' '.join(t.name for t in tags)

def get_sample_from_image(image):
    return resize_image_to_maximum_size(image, sample_max_resolution)
    
def get_preview_from_image(image):
    return resize_image_to_maximum_size(image, preview_max_resolution)

def resize_image_to_maximum_size(image, max_resolution):
    ''' Resize image to be less or equal to the maximum resolution allowed. If one of the max_resolution's components is equal to zero, it will be ignored.'''
    image = image.copy()
    original_size = image.size

    max_resolution = list(max_resolution)

    if max_resolution[0] == 0:
        max_resolution[0] = original_size[0]

    if max_resolution[1] == 0:
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