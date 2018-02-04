from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreatePostForm
from .models import Post, TaggedPost
from .utils import space_splitter


def index(request):
    return render(request, 'booru/index.html', {})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    ordered_tags = post.get_ordered_tags()
    return render(request, 'booru/post_detail.html', {"post": post, "ordered_tags": ordered_tags})

def upload(request):
    form = CreatePostForm(request.POST or None, request.FILES or None)

    if request.user.is_active:
        if form.is_valid():
            post = form.save(commit=False)
            post.uploader = request.user
            post.save()
            form.save_m2m()

            return redirect('booru:post_detail', post_id=post.id)
    else:
        pass

    return render(request, 'booru/upload.html', {"form": form})

def post_list_detail(request, page_number = 1):
    tags = request.GET.get("tags", "")
    tags = space_splitter(tags)

    print (tags)

    posts = Post.objects.all()
    if len(tags) > 0:
        for tag in tags:
            posts = posts.filter(tags__name__in=[tag])

    page_limit = 4
    p = Paginator(posts, page_limit)
    page = p.page(page_number)
    post_list = page.object_list
    
    return render(request, 'booru/posts.html', {"posts": post_list, "page": page})
