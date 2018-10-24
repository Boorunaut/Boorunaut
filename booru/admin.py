from django.contrib import admin
from .models import Post, Category, PostTag, Implication, Favorite, ScoreVote, Comment

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(PostTag)
admin.site.register(Implication)
admin.site.register(Favorite)
admin.site.register(ScoreVote)
admin.site.register(Comment)
