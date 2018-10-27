from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

class Account(AbstractUser):
    avatar          = models.ForeignKey('booru.Post', null=True, blank=True, on_delete=models.SET_NULL)
    slug            = models.SlugField(max_length=250, default="", blank=True)
    email_activated = models.BooleanField(default=False)
    comments_locked = models.BooleanField(default=False)
    about           = models.CharField(max_length=2500, blank=True)
    comments        = GenericRelation('booru.Comment')

    def save(self, *args, **kwargs):
        if self.__is_a_new_user():
            self.slug = slugify(self.username)

        super(Account, self).save(*args, **kwargs)

    def __is_a_new_user(self):
        return not self.id

    def get_absolute_url(self):
        return reverse('booru:profile', kwargs={'account_slug': self.slug})

    def get_posts(self):
        Post = apps.get_model('booru', 'Post')
        return Post.objects.all().filter(uploader=self)

    def get_favorites_count(self):
        return self.account_favorites.count()
