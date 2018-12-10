from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, RedirectView, TemplateView
from rolepermissions.checkers import has_permission

from booru.account.decorators import user_is_not_blocked
from booru.core.forms import BannedHashCreateForm, PostFlagCreateForm
from booru.core.models import BannedHash, PostFlag
from booru.models import Comment, Configuration, Implication, Post


class TermsOfServiceView(TemplateView):
    template_name = "booru/core/terms_of_service.html"

    def get_context_data(self, **kwargs):
        context = super(TermsOfServiceView, self).get_context_data(**kwargs)
        context['terms_of_service'] = Configuration.objects.filter(code_name="terms_of_service").first().value
        return context

class PrivacyPolicyView(TemplateView):
    template_name = "booru/core/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super(PrivacyPolicyView, self).get_context_data(**kwargs)
        context['privacy_policy'] = Configuration.objects.filter(code_name="privacy_policy").first().value
        return context


class BannedHashCreateView(CreateView):
    """
    Provides a form for staff members to configure their booru.
    """
    success_url = '.'
    form_class = BannedHashCreateForm
    template_name = "booru/staff_hash_ban.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.save()
        return super().form_valid(form)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user,'booru.ban_hashes'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BannedHashCreateView, self).get_context_data(**kwargs)
        context['banned_hashes'] = BannedHash.objects.all()
        return context

class BannedHashDeleteView(RedirectView):

    permanent = False
    query_string = False
    pattern_name = 'core:hash_ban'

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user,'booru.ban_hashes'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        banned_hash = get_object_or_404(BannedHash.objects.all(), id=kwargs['pk'])
        banned_hash.delete()
        kwargs.pop('pk', None)
        return super().get_redirect_url(*args, **kwargs)

class ModQueueView(TemplateView):
    template_name = "booru/staff_mod_queue.html"

    def get_context_data(self, **kwargs):
        context = super(ModQueueView, self).get_context_data(**kwargs)
        context['pending_posts'] = Post.objects.not_deleted().filter(status=Post.PENDING)
        context['pending_implications'] = Implication.objects.filter(status=Implication.PENDING)
        context['post_flags'] = PostFlag.objects.filter(status=PostFlag.PENDING)
        return context

class PostFlagCreateView(CreateView):
    """
    Provides a form for users to flag posts for deletion.
    """
    success_url = '.'
    form_class = PostFlagCreateForm
    template_name = "booru/post_flag.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.post = Post.objects.get(id=self.kwargs['post_id'])
        form.save()
        return super().form_valid(form)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PostFlagCreateView, self).get_context_data(**kwargs)
        context['post'] = Post.objects.get(id=self.kwargs['post_id'])
        return context

class StaffPostFlagResolveView(RedirectView):

    permanent = False
    query_string = False
    pattern_name = 'core:mod_queue'

    def get(self, request, *args, **kwargs):
        flag = get_object_or_404(PostFlag, id=kwargs['pk'])
        flag.status = PostFlag.RESOLVED
        flag.save()
        return super(StaffPostFlagResolveView, self).get(request, *args, **kwargs)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user,'booru.change_status'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        kwargs.pop('pk', None)
        return super().get_redirect_url(*args, **kwargs)

class StaffCommentToggleHiddenView(RedirectView):

    permanent = False
    query_string = False
    pattern_name = 'booru:post_detail'

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['pk'])
        comment.is_hidden = not comment.is_hidden
        comment.save()
        return super(StaffCommentToggleHiddenView, self).get(request, *args, **kwargs)

    @method_decorator(csrf_protect)
    @user_is_not_blocked
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not has_permission(request.user,'booru.manage_comments'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['pk'])
        kwargs['post_id'] = comment.object_id
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)
