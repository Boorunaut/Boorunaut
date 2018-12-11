from django.contrib import sitemaps
from django.urls import reverse
from booru.models import Post

class PostSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return Post.objects.approved()

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.update_timestamp

class TagsSitemap(sitemaps.Sitemap):
    priority = 0.5

    def items(self):
        return Post.tags.most_common()[:25]

    def location(self, item):
        return item.get_search_url()

    def lastmod(self, item):
        return item.update_timestamp

class PostListSitemap(sitemaps.Sitemap):
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        return ['posts']

    def location(self, item):
        return reverse('booru:posts')
