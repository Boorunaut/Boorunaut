from django.contrib.auth.models import AbstractUser
from django.db import models

class Account(AbstractUser):
    avatar          = models.ForeignKey('booru.Post', null=True, on_delete=models.SET_NULL)
    slug            = models.SlugField(max_length=250, default="", blank=True)
    email_activated = models.BooleanField(default=False)
    comments_locked = models.BooleanField(default=False)
