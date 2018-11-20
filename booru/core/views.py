from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, RedirectView, TemplateView

from booru.account.decorators import user_is_not_blocked
from booru.core.forms import BannedHashCreateForm
from booru.core.models import BannedHash
from booru.models import Configuration


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
        if not request.user.is_authenticated or not request.user.has_perm('booru.core.ban_hashes'):
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
        if not request.user.is_authenticated or not request.user.has_perm('booru.core.ban_hashes'):
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        banned_hash = get_object_or_404(BannedHash.objects.all(), id=kwargs['pk'])
        banned_hash.delete()
        kwargs.pop('pk', None)
        return super().get_redirect_url(*args, **kwargs)
