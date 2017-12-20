from django.shortcuts import render
from .models import Post
from django.shortcuts import get_object_or_404

def index(request):
    return render(request, 'booru/index.html', {})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    """
        categories_list

        for tag in post.tags.all()

        a = {}
        b= []
        a.append(post.category, b.insert(post))

    a ["meta"]
    > blablabla
    """

    return render(request, 'booru/post_detail.html', {"post": post})