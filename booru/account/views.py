from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.roles import assign_role, clear_roles

from booru.account.decorators import user_is_not_blocked
from booru.models import Comment, Post

from .forms import (StaffUserGroupForm, UserAuthenticationForm,
                    UserRegisterForm, UserSettingsForm)
from .models import Account


class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    success_url = '/post/list'
    form_class = UserAuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "booru/account/login.html"

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/post/list')
        
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, allowed_hosts=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to

class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/account/login/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

class RegisterView(FormView):
    """
    Provides the ability to a visitor to register as new user
    with an username, an email and a password
    """
    success_url = '/post/list'
    form_class = UserRegisterForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "booru/account/register.html"

    @method_decorator(sensitive_post_parameters('password1'))
    @method_decorator(sensitive_post_parameters('password2'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/post/list')

        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')

        user = authenticate(username=username, password=raw_password)
        auth_login(self.request, user)

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(RegisterView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, allowed_hosts=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to

@user_is_not_blocked
def profile(request, account_slug):
    account = get_object_or_404(Account.objects.active(), slug=account_slug)

    can_modify_profile = (request.user == account or has_permission(request.user, "modify_profile"))

    user_group_form = StaffUserGroupForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        newCommentTextarea = request.POST.get("newCommentTextarea")
        aboutUserTextarea = request.POST.get("aboutUserTextarea")
        
        if not request.user.is_authenticated:
            return redirect('account:login')
        elif newCommentTextarea and has_comment_priv: # Comment creating
            comment_content = newCommentTextarea
            Comment.objects.create(content=comment_content, author=request.user, content_object=account)
            return redirect('booru:profile', account_slug=account.slug)
        elif aboutUserTextarea and can_modify_profile: # About myself editing
            account.about = aboutUserTextarea
            account.save()
            return redirect('booru:profile', account_slug=account.slug)

    if request.user.is_authenticated:
        if user_group_form.is_valid() and has_permission(request.user, "change_user_group"):
            group = user_group_form.cleaned_data['group']
            clear_roles(account)
            assign_role(account, group)

            if group in ['administrator','moderator','janitor']:
                account.is_staff = True
                account.save()
        
        has_comment_priv = request.user.has_priv("can_comment")
        can_change_group = has_permission(request.user, "change_user_group")
    else:
        has_comment_priv = False
        can_change_group = False

    # TODO: I don't remember if I can safely pass account as
    # an parameter to the render.
    favorites = Post.objects.filter(favorites__account=account)[:5]
    
    context = {
        'account' : account,
        'recent_favorites' : favorites,
        'recent_uploads' : account.get_posts().not_deleted().order_by('-id'),
        'deleted_posts' : account.get_posts().deleted(),
        'can_modify_profile': request.user.is_authenticated and can_modify_profile,
        'can_comment': has_comment_priv,
        'user_group_form': user_group_form,
        'can_change_group': can_change_group
    }

    return render(request, 'booru/account/profile.html', context)

class SettingsView(FormView):
    """
    Provides the ability to a visitor to register as new user
    with an username, an email and a password.
    """
    success_url = '.'
    form_class = UserSettingsForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "booru/account/settings.html"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        account = self.request.user

        initial['safe_only'] = account.safe_only
        initial['show_comments'] = account.show_comments
        # TODO: implement the tag blacklist
        #initial['tag_blacklist'] = account.tag_blacklist

        return initial

    def form_valid(self, form):
        account = self.request.user

        account.safe_only = form.cleaned_data.get('safe_only')
        account.show_comments = form.cleaned_data.get('show_comments')
        account.tag_blacklist = form.cleaned_data.get('tag_blacklist')
        account.save()

        return super().form_valid(form)
    
    @user_is_not_blocked
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:login')

        return super().dispatch(request, *args, **kwargs)

class DeleteAccountView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/account/logout'

    def get(self, request, *args, **kwargs):
        if kwargs['account_slug'] == self.request.user.slug:
            self.request.user.anonymize()
        
        return super(DeleteAccountView, self).get(request, *args, **kwargs)
