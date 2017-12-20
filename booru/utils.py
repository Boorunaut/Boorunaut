def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]

def space_joiner(tags):
    return ' '.join(t.name for t in tags)