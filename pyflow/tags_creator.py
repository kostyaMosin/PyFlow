from pyflow.models import Tag


def tags_creator(data):
    tags = []
    for tag_title in data[1:].replace(' ', '').split('#'):
        tag = Tag.objects.filter(title=tag_title).first()
        if tag:
            tags.append(tag)
        elif tag is None:
            tags.append(Tag.objects.create(title=tag_title))
    return tags
