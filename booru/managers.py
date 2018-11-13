# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AbstractUserManager
from django.db import models
from django.db.models import Q


class PostQueryset(models.query.QuerySet):
    def pending(self):
        return self.filter(status=0)

    def approved(self):
        return self.filter(status=1)

    def deleted(self):
        return self.filter(status=2)

    def not_deleted(self):
        return self.filter(~Q(status=2))

class PostManager(models.Manager):
    '''Custom manager for Posts.'''
    def get_queryset(self):
        return PostQueryset(self.model, using=self._db)

    def pending(self):
        '''Returns a QuerySet with only Posts that are pending.'''
        return self.get_queryset().pending()

    def approved(self):
        '''Returns a QuerySet with only Posts that are approved.'''
        return self.get_queryset().approved()

    def deleted(self):
        '''Returns a QuerySet with only Posts that are deleted.'''
        return self.get_queryset().deleted()

    def not_deleted(self):
        '''Returns a QuerySet with only Posts that aren't deleted (pending or approved).'''
        return self.get_queryset().not_deleted()

class UserQueryset(models.query.QuerySet):
    def active(self):
        return self.exclude(is_deleted=True)

class UserManager(AbstractUserManager):
    '''Custom manager for User.'''
    def get_queryset(self):
        return UserQueryset(self.model, using=self._db)

    def active(self):
        '''Returns a QuerySet with only Users that are active.'''
        return self.get_queryset().active()
