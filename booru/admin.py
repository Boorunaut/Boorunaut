from django.contrib import admin

from .models import (Category, Comment, Favorite, Gallery, Implication, Post,
                     PostTag, ScoreVote, Configuration)

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(PostTag)
admin.site.register(Implication)
admin.site.register(Favorite)
admin.site.register(ScoreVote)
admin.site.register(Gallery)
admin.site.register(Comment)
admin.site.register(Configuration)
