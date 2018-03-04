from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .forms import CreatePostForm, EditPostForm, TagEditForm, TagListSearchForm
from .models import Alias, Implication, Post, PostTag, TaggedPost
from .utils import space_splitter


def index(request):
    return render(request, 'booru/index.html', {})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = EditPostForm(request.POST or None, request.FILES or None, instance=post)

    if request.method == "POST" and form.is_valid():
        post = form.save()

    ordered_tags = post.get_ordered_tags()
    return render(request, 'booru/post_detail.html', {"post": post, "ordered_tags": ordered_tags, "form": form})

@login_required
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

    posts = Post.objects.all()
    if len(tags) > 0:
        for tag in tags:
            posts = posts.filter(tags__name__in=[tag])

    page_limit = 4
    posts = Post.objects.all().order_by('id')
    p = Paginator(posts, page_limit)
    page = p.page(page_number)
    post_list = page.object_list
    
    return render(request, 'booru/posts.html', {"posts": post_list, "page": page})

def tags_list(request, page_number = 1):
    searched_tag = request.GET.get("tags", "")
    category = request.GET.get("category", "")
    form = TagListSearchForm(request.GET or None)

    tags = PostTag.objects.all()
    if searched_tag != "":
        tags = tags.filter(name=searched_tag)

    if category != "":
        try:
            tags = tags.filter(category=int(category))
        except:
            pass
    
    page_limit = 10
    p = Paginator(tags, page_limit)
    page = p.page(page_number)
    tags_list = page.object_list
    
    return render(request, 'booru/tag_list.html', {"tags": tags_list, "page": page, "form": form})

@login_required
def tag_edit(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)
    form = TagEditForm(request.POST or None, instance=tag)

    if form.is_valid() and request.POST:
        tag = form.save()
        
    return render(request, 'booru/tag_edit.html', {"tag": tag, "form": form})

class ImplicationListView(generic.ListView):
    model = Implication
    paginate_by = 20

    def get_queryset(self):
        queryset = Implication.objects.all()

        if self.request.GET.get('name'):
            queryset = queryset.filter(Q(from_tag__name=self.request.GET.get('name'))|
                                        Q(to_tag__name=self.request.GET.get('name')))
        return queryset

class AliasListView(generic.ListView):
    model = Alias
    paginate_by = 20

    def get_queryset(self):
        queryset = Alias.objects.all()

        if self.request.GET.get('name'):
            queryset = queryset.filter(Q(from_tag__name=self.request.GET.get('name'))|
                                        Q(to_tag__name=self.request.GET.get('name')))
        return queryset

