from django.contrib.auth.models import AbstractUser
from django.db import models

class Account(AbstractUser):
    pass
    '''avatar          = models.ImageField(blank=True, upload_to='avatars/', default='avatars/avatar_default.svg')
    slug            = models.SlugField(max_length=250, default="", blank=True)
    email_activated = models.BooleanField(default=False)
    comments_locked = models.BooleanField(default=False)'''
