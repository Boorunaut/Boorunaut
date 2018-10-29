import json

import diff_match_patch as dmp_module
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from account.models import Account

from . import utils
from .forms import (CreatePostForm, EditPostForm, ImplicationCreateForm,
                    TagEditForm, TagListSearchForm, MassRenameForm)
from .models import Comment, Implication, Post, PostTag, TaggedPost, Favorite, ScoreVote


def index(request):
    return render(request, 'booru/index.html', {})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = EditPostForm(request.POST or None, request.FILES or None, instance=post)
    
    is_favorited = False
    current_vote = 0

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(account=request.user, post=post).exists()
        current_vote = ScoreVote.objects.filter(account=request.user, post=post)

        if current_vote.exists():
            current_vote = current_vote.first().point
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('account:login')
        
        newCommentTextarea = request.POST.get("newCommentTextarea")

        if form.is_valid(): # Post editting (post_edit)
                post = form.save(commit=False)
                post.tags_mirror = " ".join(form.cleaned_data['tags'])
                post.save()
                form.save_m2m()
                return redirect('booru:post_detail', post_id=post.id)
        elif newCommentTextarea: # Comment creating
            comment_content = newCommentTextarea
            Comment.objects.create(content=comment_content, author=request.user, content_object=post)
            return redirect('booru:post_detail', post_id=post.id)

    previous_post = Post.objects.filter(id__lt=post.id).exclude(status=2).exclude(status=3).last() or None
    next_post = Post.objects.filter(id__gt=post.id).exclude(status=2).exclude(status=3).first() or None

    ordered_tags = post.get_ordered_tags()
    return render(request=request, template_name='booru/post_detail.html',
                context={"post": post, "ordered_tags": ordered_tags, "form": form,
                        "previous_post": previous_post, "next_post": next_post,
                        "is_favorited":is_favorited, "current_vote": current_vote})

def post_history(request, post_id, page_number = 1):
    post = get_object_or_404(Post, id=post_id)
    page_limit = 20

    p = Paginator(post.history.all(), page_limit)
    page = p.page(page_number)

    return render(request, 'booru/post_history.html', {"page": page, "post": post})

@login_required
def upload(request):    
    form = CreatePostForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        post = form.save(commit=False)
        post.uploader = request.user
        post.tags_mirror = " ".join(form.cleaned_data['tags'])
        post.save()
        form.save_m2m()

        return redirect('booru:post_detail', post_id=post.id)

    return render(request, 'booru/upload.html', {"form": form})

def post_list_detail(request, page_number = 1):
    tags = request.GET.get("tags", "")

    posts = utils.parse_and_filter_tags(tags)
    posts = posts.exclude(status=2).exclude(status=3)
    
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

    versions = Version.objects.get_for_object(tag)
    tag_dict = model_to_dict(tag)

    if len(versions) > 0 and versions[0].field_dict["associated_user_id"]:
        associated_user = get_object_or_404(Account, id=versions[0].field_dict["associated_user_id"])
        tag_dict['associated_user_name'] = associated_user.slug

    form = TagEditForm(request.POST or None, instance=tag, initial=tag_dict)
    if form.is_valid() and request.POST:
        tag = form.save(commit=False)
        tag.author = request.user
        if form.cleaned_data['associated_user_name']:
            associated_user = get_object_or_404(Account, slug=form.cleaned_data['associated_user_name'])
            tag.associated_user = associated_user
        tag.save()
        form.save_m2m()
        return redirect('booru:tag_detail', tag.id)
        
    return render(request, 'booru/tag_edit.html', {"tag": tag, "form": form})

def tag_detail(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)
    last_posts = Post.objects.filter(tags__name__in=[tag.name])[:6]
    return render(request, 'booru/tag_detail.html', {"tag": tag, "last_post": last_posts})

def tag_history(request, tag_id, page_number = 1):
    tag = get_object_or_404(PostTag, pk=tag_id)
    page_limit = 20

    p = Paginator(tag.history.all(), page_limit)
    page = p.page(page_number)

    return render(request, 'booru/tag_history.html', {"page": page, "tag": tag})

def tag_revision_diff(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)
    
    old_revision = get_object_or_404(Version, pk=request.GET.get('oldRevision'))
    new_revision = get_object_or_404(Version, pk=request.GET.get('newRevision'))

    description_diff        = utils.get_diff("description", old_revision, new_revision)
    associated_link_diff    = utils.get_diff("associated_link", old_revision, new_revision)

    context = {"tag": tag, "description_diff": description_diff, "associated_link_diff": associated_link_diff,
               "old_revision": old_revision, "new_revision": new_revision}
    
    return render(request, 'booru/tag_revision_diff.html', context)

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
    
    utils.verify_and_perform_implications(implication.from_tag)
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
def implication_disapprove(request, implication_id):
    implication = Implication.objects.get(id=implication_id)
    implication.status = 2
    implication.save()
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
def staff_page(request):
    Account = apps.get_model('account', 'Account')
    accounts = Account.objects.all().order_by("-id")

    context = {
        'accounts': accounts
    }

    return render(request, 'booru/staff_page.html', context)

def tag_search(request):
    term = request.GET.get("term", "")
    operator = ""
    value = term

    if term.startswith("-") or term.startswith("~"):
        operator = term[0]
        value = term[1:]

    tag_results = PostTag.objects.filter(Q(name__istartswith=value) | Q(aliases__name__istartswith=value)).distinct()
    tag_results = tag_results[:10]

    results = []
    for tag in tag_results:
        name = operator + tag.name
        if tag.name.startswith(value):
            results.append({'id': tag.pk, 'label': name, 'value': name})
        else:
            results.append({'id': tag.pk, 'label': "{} ({})".format(name, term), 'value': name})
    return HttpResponse(json.dumps(results), content_type='application/json')

def post_approve(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.user.has_perm("booru.change_status") and post.status != 1:
        post.status = 1
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

def post_hide(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.user.has_perm("booru.change_status") and post.status != 2:
        post.status = 2
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

def post_delete(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.user.has_perm("booru.change_status") and post.status != 3:
        post.status = 3
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

@login_required
def post_favorite(request, post_id):
    post = Post.objects.get(id=post_id)
    favorite = Favorite.objects.filter(post=post, account=request.user).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(post=post, account=request.user)
    
    return redirect('booru:post_detail', post_id=post.id)

@login_required
def post_score_vote(request, post_id):
    post = Post.objects.get(id=post_id)
    score_vote = ScoreVote.objects.filter(post=post, account=request.user).first()

    value = int(request.GET.get("point", 0))
    if value > 1: value = 1
    if value < -1: value = -1

    if score_vote:
        if score_vote.point == value:
            score_vote.point = 0
        else:
            score_vote.point = value

        score_vote.save()
    else:
        score_vote = ScoreVote.objects.create(post=post, account=request.user, point=value)
    
    results = {'value': score_vote.point, "current_points": post.get_score_count()}
    return HttpResponse(json.dumps(results), content_type='application/json')

def staff_mass_rename(request):
    form = MassRenameForm(request.POST or None, request.FILES or None)

    if request.user.has_perm("booru.mass_rename"):
        if form.is_valid():
            filter_by = form.cleaned_data['filter_by']
            when = form.cleaned_data['when']
            replace_with = form.cleaned_data['replace_with']

            posts = utils.parse_and_filter_tags(filter_by)

            when = utils.space_splitter(when)
            replace_with = utils.space_splitter(replace_with)

            posts = posts.filter(tags__name__in=when)

            for post in posts:
                post.tags.remove(*when)
                post.tags.add(*replace_with)
                post.save()
                
            return redirect('booru:staff_mass_rename')
        return render(request, 'booru/staff_mass_rename.html', {"form": form})
    return redirect('booru:index')
