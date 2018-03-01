from django.contrib import admin
from .models import Post, Category, PostTag, Implication, Alias

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(PostTag)
admin.site.register(Implication)
admin.site.register(Alias)
