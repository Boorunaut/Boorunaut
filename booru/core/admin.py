from django.contrib import admin
from booru.core.models import BannedHash, PostFlag

admin.site.register(BannedHash)
admin.site.register(PostFlag)
