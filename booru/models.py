import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import CommonGenericTaggedItemBase, TaggedItemBase


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

def get_file_path_preview(instance, filename):
    name = get_file_path(instance, filename)
    return os.path.join('data/preview/', name)

def get_file_path_sample(instance, filename):
    name = get_file_path(instance, filename)
    return os.path.join('data/sample/', name)

def get_file_path_image(instance, filename):
    name = get_file_path(instance, filename)
    return os.path.join('data/image/', name)

class Category(models.Model):
    '''Basic model for the content app. It should be inherited from the other models.'''
    label = models.CharField(max_length=100, blank=True)
    title_singular = models.CharField(max_length=100, blank=True)
    title_plural = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.title_singular

class TaggedPost(CommonGenericTaggedItemBase, TaggedItemBase):
    '''Basic model for the content app. It should be inherited from the other models.'''
    object_id = models.CharField(max_length=50, verbose_name=('Object id'), db_index=True)
    label = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=2500, blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    def get_name(self):
        split_name = self.label.replace("_", " ")
        return split_name

class Post(models.Model):
    '''Basic model for the content app. It should be inherited from the other models.'''
    preview = models.ImageField(upload_to=get_file_path_preview, blank=True)
    sample = models.ImageField(upload_to=get_file_path_sample, blank=True)
    image = models.ImageField(upload_to=get_file_path_image, blank=True)
    uploader = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    source = models.URLField(blank=True)
    score = models.IntegerField(default=0)
    favorites = models.IntegerField(default=0)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    locked = models.BooleanField(default=False)
    tags = TaggableManager(through=TaggedPost, related_name="posts") #TODO: Check django-taggit issue #497

    NONE = 0
    SAFE = 1
    QUESTIONABLE = 2
    EXPLICIT = 3
    RATING_CHOICES = (
        (NONE, 'None'),
        (SAFE, 'Safe'),
        (QUESTIONABLE, 'Questionable'),
        (EXPLICIT, 'Explicit')
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=NONE,
    )

    PENDING = 0
    APPROVED = 1
    DELETED = 2
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DELETED, 'Deleted')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PENDING,
    )
