from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account, Timeout

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
            (None, {'fields': ( 'avatar', 'slug', 'email_activated',
                                'comments_locked', 'about', 'safe_only',
                                'show_comments', 'tag_blacklist', 'is_deleted')}),
    )

admin.site.register(Account, UserAdmin)
admin.site.register(Timeout)
