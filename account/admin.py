from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
            (None, {'fields': ('avatar', 'slug', 'email_activated', 'comments_locked')}),
    )

admin.site.register(Account, UserAdmin)
