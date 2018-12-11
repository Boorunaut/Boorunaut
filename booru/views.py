import json

import diff_match_patch as dmp_module
from django.apps import apps
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, Q
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from django.views.generic.edit import DeleteView
from rolepermissions.checkers import has_permission

from booru.account.decorators import user_is_not_blocked
from booru.account.models import Account, Privilege, Timeout

from . import utils
from .forms import (BanUserForm, CreatePostForm, EditPostForm,
                    GalleryCreateForm, GalleryEditForm, GalleryListSearchForm,
                    ImplicationCreateForm, ImplicationFilterForm,
                    MassRenameForm, SiteConfigurationForm, TagEditForm,
                    TagListSearchForm)
from .models import (Comment, Configuration, Favorite, Gallery, Implication,
                     Post, PostTag, ScoreVote, TaggedPost)


@user_is_not_blocked
def index(request):
    post_count = Post.objects.not_deleted().count()
    return render(request, 'booru/index.html', {'post_count': post_count})

@user_is_not_blocked
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = EditPostForm(request.POST or None, request.FILES or None, instance=post)
    
    is_favorited = False
    has_comment_priv = False
    current_vote = 0
    
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(account=request.user, post=post).exists()
        current_vote = ScoreVote.objects.filter(account=request.user, post=post)
        has_comment_priv = request.user.has_priv("can_comment")

        if current_vote.exists():
            current_vote = current_vote.first().point
        else:
            current_vote = 0
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('account:login')
        
        newCommentTextarea = request.POST.get("newCommentTextarea")

        if form.is_valid(): # Post editing (post_edit)
            post = form.save(commit=False)
            form.save_m2m()
            post.check_and_update_implications()
            post.save()
            return redirect('booru:post_detail', post_id=post.id)
        elif newCommentTextarea and has_comment_priv: # Comment creating
            comment_content = newCommentTextarea
            Comment.objects.create(content=comment_content, author=request.user, content_object=post)
            return redirect('booru:post_detail', post_id=post.id)

    previous_post = Post.objects.filter(id__lt=post.id).exclude(status=2).exclude(status=3).last() or None
    next_post = Post.objects.filter(id__gt=post.id).exclude(status=2).exclude(status=3).first() or None

    ordered_tags = post.get_ordered_tags()

    SHOW_ADS = (post.rating == Post.QUESTIONABLE and settings.BOORUNAUT_ADS_ON_QUESTIONABLE or
                post.rating == Post.EXPLICIT and settings.BOORUNAUT_ADS_ON_EXPLICIT or
                post.rating == Post.SAFE)

    return render(  request=request, template_name='booru/post_detail.html',
                    context={"post": post, "ordered_tags": ordered_tags, "form": form,
                        "previous_post": previous_post, "next_post": next_post,
                        "is_favorited":is_favorited, "current_vote": current_vote, 
                        "can_comment": has_comment_priv, "SHOW_ADS": SHOW_ADS})

@user_is_not_blocked
def post_history(request, post_id, page_number = 1):
    post = get_object_or_404(Post, id=post_id)
    page_limit = 20

    p = Paginator(post.history.all(), page_limit)
    page = p.page(page_number)

    return render(request, 'booru/post_history.html', {"page": page, "post": post})

@login_required
@user_is_not_blocked
def upload(request): # post_create
    form = CreatePostForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        post = form.save(commit=False)
        post.uploader = request.user
        post.save_without_historical_record()
        form.save_m2m()
        post.check_and_update_implications()
        post.save()
        return redirect('booru:post_detail', post_id=post.id)

    return render(request, 'booru/upload.html', {"form": form})

@user_is_not_blocked
def post_list_detail(request, page_number = 1):
    tags = request.GET.get("tags", "")
    
    posts = utils.parse_and_filter_tags(tags)
    posts = posts.exclude(status=2).exclude(status=3)

    # Check if user enabled safe only
    # TODO: transform these tag operations into a class
    if request.user.is_authenticated and request.user.safe_only:
        posts = posts.exclude(rating=2).exclude(rating=3)
    
    page_limit = 20
    p = Paginator(posts, page_limit)
    page = p.page(page_number)
    post_list = page.object_list

    tags_list = Post.tags.most_common().filter(post__id__in=post_list)[:25]
    
    return render(request, 'booru/posts.html', {"posts": post_list, "page": page, "tags_list": tags_list, "SHOW_ADS": True})

@user_is_not_blocked
def tags_list(request, page_number = 1):
    searched_tag = request.GET.get("tags", "")
    category = request.GET.get("category", "")

    try:
        category = int(category)
    except:
        category = 0

    form = TagListSearchForm(request.GET or None)

    tags = PostTag.objects.all()

    if searched_tag != "":
        tags = tags.filter(name=searched_tag)

    if category != 0:
        tags = tags.filter(category=category)

    tags = tags.order_by('id')
    
    page_limit = 10
    p = Paginator(tags, page_limit)
    
    try:
        page = p.page(page_number)
    except EmptyPage:
        url = reverse('booru:tags_list') + '?tags={}&category={}'.format(searched_tag, category)
        return redirect(url, page_number=1)
    
    tags_list = page.object_list
    return render(request, 'booru/tag_list.html', {"tags": tags_list, "page": page, "form": form})

@login_required
@user_is_not_blocked
def tag_edit(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)
    tag_dict = model_to_dict(tag)

    if tag.associated_user_id:
        associated_user = get_object_or_404(Account.objects.active(), id=tag.associated_user_id)
        tag_dict['associated_user_name'] = associated_user.slug

    form = TagEditForm(request.POST or None, instance=tag, initial=tag_dict)
    if form.is_valid() and request.POST:
        tag = form.save(commit=False)
        tag.author = request.user
        if form.cleaned_data['associated_user_name']:
            associated_user = get_object_or_404(Account.objects.active(), slug=form.cleaned_data['associated_user_name'])
            tag.associated_user = associated_user
        tag.save()
        form.save_m2m()
        return redirect('booru:tag_detail', tag.id)
        
    return render(request, 'booru/tag_edit.html', {"tag": tag, "form": form})

@user_is_not_blocked
def tag_detail(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)
    last_posts = Post.objects.filter(tags__name__in=[tag.name])[:6]
    return render(request, 'booru/tag_detail.html', {"tag": tag, "last_post": last_posts})

@user_is_not_blocked
def tag_history(request, tag_id, page_number = 1):
    tag = get_object_or_404(PostTag, pk=tag_id)
    page_limit = 20

    p = Paginator(tag.history.all(), page_limit)
    page = p.page(page_number)
    return render(request, 'booru/tag_history.html', {"page": page, "tag": tag})

class TagDelete(DeleteView):
    model = PostTag
    success_url = reverse_lazy('booru:tags_list')
    template_name = 'booru/tag_confirm_delete.html'

    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user, 'booru.manage_tags'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

@user_is_not_blocked
def tag_revision_diff(request, tag_id):
    tag = get_object_or_404(PostTag, pk=tag_id)

    old_version = tag.history.filter(history_id=request.GET.get('oldRevision')).first()
    new_version = tag.history.filter(history_id=request.GET.get('newRevision')).first()

    delta = new_version.diff_against(old_version)

    context = {"tag": tag, "changes": delta.changes,
               "old_version": old_version, "new_version": new_version}
    
    return render(request, 'booru/tag_revision_diff.html', context)

class ImplicationListView(generic.ListView):
    model = Implication
    paginate_by = 20

    def get_queryset(self):
        queryset = Implication.objects.all()

        if self.request.GET.get('name'):
            queryset = queryset.filter( Q(from_tag__name=self.request.GET.get('name'))|
                                        Q(to_tag__name=self.request.GET.get('name')))
        
        status = self.request.GET.get('status')
        if status:
            try:
                status = int(status)
                queryset = queryset.filter(status=status)
            except ValueError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ImplicationListView, self).get_context_data(**kwargs)
        context['form'] = ImplicationFilterForm(self.request.GET)
        return context
    
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class ImplicationDetailView(generic.DetailView):
    model = Implication

    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

@login_required
@user_is_not_blocked
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
@user_is_not_blocked
def implication_approve(request, implication_id):
    implication = Implication.objects.get(id=implication_id)

    if implication.status != 1:
        implication.status = 1
        implication.approver = request.user
        implication.save()
    
    utils.verify_and_perform_implications(implication.from_tag)
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
@user_is_not_blocked
def implication_disapprove(request, implication_id):
    implication = Implication.objects.get(id=implication_id)
    implication.status = 2
    implication.save()
    return redirect('booru:implication-detail', implication.id)

@staff_member_required
@user_is_not_blocked
def staff_page(request):
    Account = apps.get_model('account', 'Account')
    accounts = Account.objects.active().order_by("-id")

    context = {
        'accounts': accounts
    }

    return render(request, 'booru/staff_page.html', context)

@user_is_not_blocked
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

@user_is_not_blocked
def post_approve(request, post_id):
    post = Post.objects.get(id=post_id)

    if has_permission(request.user, "change_status") and post.status != 1:
        post.status = 1
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

@user_is_not_blocked
def post_hide(request, post_id):
    post = Post.objects.get(id=post_id)

    if has_permission(request.user, "change_status") and post.status != 2:
        post.status = 2
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

@user_is_not_blocked
def post_delete(request, post_id):
    post = Post.objects.get(id=post_id)

    if has_permission(request.user, "change_status") and post.status != 3:
        post.status = 3
        post.save()
    return redirect('booru:post_detail', post_id=post.id)

@login_required
@user_is_not_blocked
def post_favorite(request, post_id):
    post = Post.objects.get(id=post_id)
    favorite = Favorite.objects.filter(post=post, account=request.user).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(post=post, account=request.user)
    
    return redirect('booru:post_detail', post_id=post.id)

@login_required
@user_is_not_blocked
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

@user_is_not_blocked
def staff_mass_rename(request):
    form = MassRenameForm(request.POST or None, request.FILES or None)

    if has_permission(request.user, "mass_rename"):
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

@user_is_not_blocked
def gallery_list(request, page_number = 1):
    searched_gallery = request.GET.get("name", "")
    form = GalleryListSearchForm(request.GET or None)

    galleries = Gallery.objects.all().order_by('-id')
    if searched_gallery != "":
        galleries = galleries.filter(name__icontains=searched_gallery)
    
    page_limit = 10
    p = Paginator(galleries, page_limit)
    page = p.page(page_number)
    gallery_list = page.object_list
    
    return render(request, 'booru/gallery_list.html', {"galleries": gallery_list, "page": page, "form": form})

@user_is_not_blocked
def gallery_history(request, gallery_id, page_number = 1):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    page_limit = 20

    p = Paginator(gallery.history.all(), page_limit)
    page = p.page(page_number)

    object_enum = enumerate(page.object_list)

    return render(request, 'booru/gallery_history.html', {"page": page, "gallery": gallery})

@login_required
@user_is_not_blocked
def gallery_edit(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)

    gallery_dict = model_to_dict(gallery)
    gallery_dict['posts_ids'] = '\n'.join([str(post_id['id']) for post_id in gallery.posts.values('id')])
    form = GalleryEditForm(request.POST or None, instance=gallery, initial=gallery_dict)

    if form.is_valid():
        posts_ids = form.cleaned_data['posts_ids'].splitlines()
        gallery = form.save(commit=False)
        gallery.posts.clear()
        gallery.posts_mirror = " ".join(form.cleaned_data['posts_ids'].splitlines())
        gallery.save()
        posts = Post.objects.filter(id__in=posts_ids)
        gallery.posts.add(*posts)
        form.save_m2m()
        return redirect('booru:gallery_detail', gallery_id=gallery.id)
        
    return render(request, 'booru/gallery_edit.html', {"form": form, "gallery": gallery})

@login_required
@user_is_not_blocked
def gallery_create(request):    
    form = GalleryCreateForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        posts_text = form.cleaned_data['posts_ids']
        posts_ids = posts_text.splitlines()
        
        gallery = form.save(commit=False)
        gallery.posts_mirror = " ".join(posts_ids)
        gallery.save()
        posts = Post.objects.filter(id__in=posts_ids)
        gallery.posts.add(*posts)
        form.save_m2m()
        return redirect('booru:gallery_detail', gallery_id=gallery.id)
    return render(request, 'booru/gallery_create.html', {"form": form})

@user_is_not_blocked
def gallery_detail(request, gallery_id):
    page_number = int(request.GET.get('page', '1'))
    page_limit = 20

    gallery = Gallery.objects.get(id=gallery_id)
    posts = gallery.posts.all()

    p = Paginator(posts, page_limit)
    page = p.page(page_number)

    return render(request, 'booru/gallery_detail.html', {"gallery": gallery, "page": page})

class StaffBanUser(FormView):
    """
    Provides a form for staff members to configure their booru.
    """
    success_url = '.'
    form_class = BanUserForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "booru/staff_user_tools.html"

    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        expiration = form.cleaned_data['expiration']
        revoked = Privilege.objects.get(codename="can_login")
        target_user = Account.objects.get(username=form.cleaned_data['username'])
        author = self.request.user

        if not has_role(target_user, 'administrator'): # Can't ban admins
            if (has_role(target_user, 'moderator') and has_permission(request.user, 'booru.ban_mod')
                or not has_role(target_user, 'moderator')):
                instance = Timeout.objects.create(  author=author, target_user=target_user, 
                                                    expiration=expiration, reason=reason)
                instance.revoked.add(revoked)
        return super().form_valid(form)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user, 'booru.ban_user'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

class SiteConfigurationView(FormView):
    """
    Provides a form for staff members to configure their booru.
    """
    success_url = '.'
    form_class = SiteConfigurationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "booru/staff_site_configuration.html"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()

        initial['site_title'] = Configuration.objects.get(code_name='site_title').value
        initial['terms_of_service'] = Configuration.objects.get(code_name='terms_of_service').value
        initial['privacy_policy'] = Configuration.objects.get(code_name='privacy_policy').value
        initial['announcement'] = Configuration.objects.get(code_name='announcement').value
        return initial

    def form_valid(self, form):
        site_title = Configuration.objects.get(code_name='site_title')
        site_title.value = form.cleaned_data.get('site_title')
        site_title.save()

        terms_of_service = Configuration.objects.get(code_name='terms_of_service')
        terms_of_service.value = form.cleaned_data.get('terms_of_service')
        terms_of_service.save()

        privacy_policy = Configuration.objects.get(code_name='privacy_policy')
        privacy_policy.value = form.cleaned_data.get('privacy_policy')
        privacy_policy.save()

        announcement = Configuration.objects.get(code_name='announcement')
        announcement.value = form.cleaned_data.get('announcement')
        announcement.save()
        return super().form_valid(form)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user,'change_configurations'):
            return redirect('account:login')

        return super().dispatch(request, *args, **kwargs)
