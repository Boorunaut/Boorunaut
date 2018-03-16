import os
import uuid

import reversion
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

from account.models import Account

from . import utils
from .managers import PostManager


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

class Implication(models.Model):
    from_tag = models.ForeignKey('booru.PostTag', blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="from_implications")    
    to_tag = models.ForeignKey('booru.PostTag', blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="to_implications")    
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name="authored_implications")
    approver = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="approved_implications")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    PENDING = 0
    APPROVED = 1
    UNAPPROVED = 2
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (UNAPPROVED, 'Unapproved')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return "{} -> {}".format(self.from_tag, self.to_tag)

class Alias(models.Model):
    from_tag = models.ForeignKey('booru.PostTag', blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="from_aliases")    
    to_tag = models.ForeignKey('booru.PostTag', blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="to_aliases")    
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name="authored_aliases")
    approver = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="approved_aliases")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    PENDING = 0
    APPROVED = 1
    UNAPPROVED = 2
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (UNAPPROVED, 'Unapproved')
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return "{} -> {}".format(self.from_tag, self.to_tag)

    class Meta:
        verbose_name_plural = 'Aliases'

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

@reversion.register()
class PostTag(TagBase):
    category = models.ForeignKey(Category, default=1, on_delete=models.SET_DEFAULT)
    description = models.CharField(max_length=100, blank=True)
    associated_link = models.CharField(max_length=100, blank=True)
    associated_user = models.ForeignKey(Account, null=True, blank=True,
                                                 on_delete=models.SET_NULL, related_name="associated_tags")
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name="authored_tags")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")

    def get_count(self):
        return TaggedPost.objects.filter(tag=self).count()

class TaggedPost(GenericTaggedItemBase):
    tag = models.ForeignKey(PostTag, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(TaggedPost, self).save(*args, **kwargs)

        tag_name = self.tag
        utils.verify_and_perform_aliases_and_implications(tag_name)

class Post(models.Model):
    parent = models.IntegerField(null=True, blank=True)
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

    objects = PostManager()

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
        tags = self.tags.all().order_by('category')
        
        for tag in tags:
            try:
                ordered_tags[tag.category]
            except:
                ordered_tags[tag.category] = []
            ordered_tags[tag.category].append(tag)
        
        return ordered_tags

    def get_score_count(self):
        return self.scorevote_set.count()

    def get_favorites_count(self):
        return self.favorite_set.count()

class Favorite(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('account', 'post',)

class ScoreVote(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    point = models.IntegerField(default=1)

    class Meta:
        unique_together = ('account', 'post',)
