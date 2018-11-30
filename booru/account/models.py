from django.apps import apps
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from rolepermissions.roles import assign_role

from booru.managers import UserManager


class Privilege(models.Model):
    name = models.CharField(_('name'), max_length=255)
    codename = models.CharField(_('codename'), max_length=100)

    class Meta:
        verbose_name = _('privilege')
        verbose_name_plural = _('privileges')
        ordering = ['codename']

    def __str__(self):
        return "{} | {}".format(self.codename, self.name)

class Timeout(models.Model):
    reason      = models.CharField(max_length=2500)
    expiration  = models.DateTimeField()
    revoked     = models.ManyToManyField(
        Privilege,
        verbose_name=_('privileges'),
        blank=True,
        help_text=_('Privileges revoked from this user.'),
        related_name="revoked_privs",
        related_query_name="user",
    )
    target_user = models.ForeignKey('account.Account', related_name="user_timedout", on_delete=models.CASCADE)
    author      = models.ForeignKey('account.Account', related_name="timeout_creator", on_delete=models.CASCADE)


class Account(AbstractUser):
    avatar          = models.ForeignKey('booru.Post', null=True, blank=True, on_delete=models.SET_NULL)
    slug            = models.SlugField(max_length=250, default="", blank=True)
    email_activated = models.BooleanField(default=False)
    comments_locked = models.BooleanField(default=False)
    about           = models.CharField(max_length=2500, blank=True)
    comments        = GenericRelation('booru.Comment')
    # Account settings
    safe_only       = models.BooleanField(default=True)
    show_comments   = models.BooleanField(default=True)
    tag_blacklist   = models.CharField(max_length=2500, blank=True)

    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    def save(self, *args, **kwargs):
        give_role = False
        if self.__is_a_new_user():
            give_role = True
            self.slug = slugify(self.username)
        super(Account, self).save(*args, **kwargs)

        if give_role:
            if self.is_staff:
                assign_role(self, 'administrator')
            else:
                assign_role(self, 'user')

    def __is_a_new_user(self):
        return not self.id

    def get_absolute_url(self):
        if self.is_deleted == False:
            return reverse('booru:profile', kwargs={'account_slug': self.slug})
        else:
            return "#"

    def get_name(self):
        if self.is_deleted == False:
            return self.username
        else:
            return "Anonymous User"

    def get_posts(self):
        Post = apps.get_model('booru', 'Post')
        return Post.objects.all().filter(uploader=self)

    def get_favorites_count(self):
        return self.account_favorites.count()

    def get_comments_count(self):
        Comment = apps.get_model('booru', 'Comment')
        return Comment.objects.filter(author=self, content_type__model="post").count()

    def get_priv_timeout(self, codename):
        timeouts = Timeout.objects.filter(target_user=self, revoked__in=Privilege.objects.filter(codename=codename))
        timeouts.filter(expiration__lt=timezone.now()).delete() # deleting timeouts if already expired
        return timeouts

    def has_priv(self, codename):
        return not self.get_priv_timeout(codename=codename).exists()

    def anonymize(self):
        self.email = ""
        self.is_deleted = True
        self.save()

    class Meta:
        permissions = (
            ("modify_profile", "Can change values from all profiles."),
            ("change_user_group", "Can set the group of a user."),
            ("ban_user", "Can ban users."),
            ("ban_mod", "Can ban moderators."),
        )
