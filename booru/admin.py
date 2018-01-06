from django.contrib import admin
from .models import Post, Category, PostTag

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(PostTag)
