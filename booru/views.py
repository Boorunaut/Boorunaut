from django.shortcuts import render
from .models import Post
from django.shortcuts import get_object_or_404, redirect
from .forms import CreatePostForm

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

def upload(request):
    form = CreatePostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save()
        return redirect('booru:post_detail', post_id=post.id)

    return render(request, 'booru/upload.html', {"form": form})

def posts(request):
    last_ten_posts = Post.objects.all()[:10]

    return render(request, 'booru/posts.html', {"posts": last_ten_posts})