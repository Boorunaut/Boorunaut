from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from . import utils
from .forms import (AliasCreateForm, CreatePostForm, EditPostForm,
                    ImplicationCreateForm, TagEditForm, TagListSearchForm)
from .models import Alias, Implication, Post, PostTag, TaggedPost


def index(request):
    return render(request, 'booru/index.html', {})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = EditPostForm(request.POST or None, request.FILES or None, instance=post)

    if request.method == "POST" and form.is_valid():
        post = form.save()
        return redirect('booru:post_detail', post_id=post.id)

    previous_post = Post.objects.filter(id=post.id - 1).first() or None
    next_post = Post.objects.filter(id=post.id + 1).first() or None

    ordered_tags = post.get_ordered_tags()
    return render(request, 'booru/post_detail.html', {"post": post, "ordered_tags": ordered_tags, "form": form,
                                                      "previous_post": previous_post, "next_post": next_post})

@login_required
def upload(request):    
    form = CreatePostForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        post = form.save(commit=False)
        post.uploader = request.user
        post.save()
        form.save_m2m()

        return redirect('booru:post_detail', post_id=post.id)

    return render(request, 'booru/upload.html', {"form": form})

def post_list_detail(request, page_number = 1):
    tags = request.GET.get("tags", "")
    tags = utils.space_splitter(tags)

    posts = Post.objects.all()
    if len(tags) > 0:
        for tag in tags:
            posts = posts.filter(tags__name__in=[tag])

    page_limit = 4
    posts = posts.order_by('id')
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

class ImplicationDetailView(generic.DetailView):
    model = Implication

class AliasListView(generic.ListView):
    model = Alias
    paginate_by = 20

    def get_queryset(self):
        queryset = Alias.objects.all()

        if self.request.GET.get('name'):
            queryset = queryset.filter(Q(from_tag__name=self.request.GET.get('name'))|
                                        Q(to_tag__name=self.request.GET.get('name')))
        return queryset

class AliasDetailView(generic.DetailView):
    model = Alias

@login_required
def alias_create(request):    
    form = AliasCreateForm(data=request.POST)
    
    if form.is_valid():
        from_tag_name = form.cleaned_data['from_tag']
        to_tag_name = form.cleaned_data['to_tag']

        from_tag, from_tag_created = PostTag.objects.get_or_create(name=from_tag_name)
        to_tag, from_tag_created = PostTag.objects.get_or_create(name=to_tag_name)

        alias, alias_created = Alias.objects.get_or_create(from_tag=from_tag, to_tag=to_tag)
        alias.author = request.user
        alias.save()
        return redirect('booru:alias-detail', alias.id)

    return render(request, 'booru/alias_create.html', { "form": form })

@login_required
def implication_create(request):    
    form = ImplicationCreateForm(data=request.POST)
    
    if form.is_valid():
        from_tag_name = form.cleaned_data['from_tag']
        to_tag_name = form.cleaned_data['to_tag']

        from_tag, from_tag_created = PostTag.objects.get_or_create(name=from_tag_name)
        to_tag, from_tag_created = PostTag.objects.get_or_create(name=to_tag_name)

        implication, implication_created = Implication.objects.get_or_create(from_tag=from_tag, to_tag=to_tag)
        implication.author = request.user
        implication.save()
        return redirect('booru:implication-detail', implication.id)

    return render(request, 'booru/implication_create.html', { "form": form })

@staff_member_required
def implication_approve(request, implication_id):
    implication = Implication.objects.get(id=implication_id)

    if implication.status == 0:
        implication.status = 1
        implication.approver = request.user
        implication.save()
    
    utils.verify_and_perform_aliases_and_implications(implication.from_tag)
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
def alias_approve(request, alias_id):
    alias = Alias.objects.get(id=alias_id)

    if alias.status == 0:
        alias.status = 1
        alias.approver = request.user
        alias.save()
    
    utils.verify_and_perform_aliases_and_implications(alias.from_tag)    
    return redirect('booru:alias-detail', alias.id)

@staff_member_required
def implication_disapprove(request, implication_id):
    implication = Implication.objects.get(id=implication_id)
    implication.status = 2
    implication.save()
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
def alias_disapprove(request, alias_id):
    alias = Alias.objects.get(id=alias_id)
    alias.status = 2
    alias.save()    
    return redirect('booru:alias-detail', alias.id)
