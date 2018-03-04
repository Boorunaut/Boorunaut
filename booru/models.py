import os
import uuid

from account.models import Account
from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase
from . import utils
from django.urls import reverse

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

    class Meta:
        verbose_name_plural = 'Categories'

class PostTag(TagBase):
    category = models.ForeignKey(Category, default=1, on_delete=models.SET_DEFAULT)
    
    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")

    def get_count(self):
        return TaggedPost.objects.filter(tag=self).count()

class TaggedPost(GenericTaggedItemBase):
    tag = models.ForeignKey(PostTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)

class Post(models.Model):
    parent = models.IntegerField(null=True)
    preview = models.ImageField(upload_to=get_file_path_preview, blank=True)
    sample = models.ImageField(upload_to=get_file_path_sample, blank=True)
    image = models.ImageField(upload_to=get_file_path_image, blank=True)
    uploader = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    update_timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)
    source = models.URLField(blank=True)
    score = models.IntegerField(default=0)
    favorites = models.IntegerField(default=0)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    locked = models.BooleanField(default=False)
    tags = TaggableManager(through=TaggedPost, related_name="posts")

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

    def save(self, *args, **kwargs):
        pil_image = utils.get_pil_image_if_valid(self.image)

        if pil_image:
            sample = utils.get_sample(pil_image)
            preview = utils.get_preview(pil_image)
            
            if sample:
                self.sample.save(".jpg", sample, save=False)

            self.preview.save(".jpg", preview, save=False)

        super(Post, self).save(*args, **kwargs)

    def get_sample_url(self):
        if self.sample:
            return self.sample.url
        else:
            return self.image.url

    def get_absolute_url(self):
        return reverse('booru:post_detail', kwargs={'post_id': self.id})

    def get_ordered_tags(self):
        ordered_tags = {}
        
        for tag in self.tags.all():
            try:
                ordered_tags[tag.category]
            except:
                ordered_tags[tag.category] = []
            ordered_tags[tag.category].append(tag)
        
        return ordered_tags
