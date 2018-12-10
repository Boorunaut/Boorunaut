from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       UsernameField)
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template.defaultfilters import slugify

import booru.utils
from booru.account.models import Account


class UniqueUserEmailField(forms.EmailField):
    """
    An EmailField which only is valid if no Account has that email.
    """

    def validate(self, value):
        super().validate(value)
        try:
            Account.objects.get(email=value)
            raise forms.ValidationError("A user with that email already exists.")
        except Account.MultipleObjectsReturned:
            raise forms.ValidationError("A user with that email already exists.")
        except Account.DoesNotExist:
            pass

class UsernameExistsField(UsernameField):
    """
    An UsernameField that raises an error when the name is 
    not registered on the database.
    """

    def validate(self, value):
        super().validate(value)
        try:
            Account.objects.get(username=value)
        except Account.DoesNotExist:
            raise forms.ValidationError("There's no user registered with that username.")

class UsernameNotBlockedField(UsernameExistsField):
    """
    An UsernameExistsField that raises an error when the account 
    is banned from the website.
    """

    def validate(self, value):
        super().validate(value)
        account = Account.objects.get(slug=slugify(value))
        priv_timeout = account.get_priv_timeout("can_login")
        if priv_timeout.exists(): # is banned
            raise forms.ValidationError("This user is currently banned until {}.".format(priv_timeout.first().expiration))


class UniqueUsernameField(UsernameField):
    """
    An UsernameField that raises an error when the 
    name is already in use.
    """

    def validate(self, value):
        super().validate(value)
        try:
            Account.objects.get(slug=slugify(value))
            raise forms.ValidationError("There's already an user registered with that username.")
        except Account.MultipleObjectsReturned:
            raise forms.ValidationError("There's already an user registered with that username.")
        except Account.DoesNotExist:
            pass

class UserRegisterForm(UserCreationForm):
    """
    Extends the built in UserCreationForm to include the Account email 
    and the form-control class in each widget.
    """

    email = UniqueUserEmailField(required=True, label='Email address')
    username = UniqueUsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    class Meta:
        model = Account
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})

class UserAuthenticationForm(AuthenticationForm):
    """
    Extends the built in AuthenticationForm to add 
    the form-control class in each widget.
    """

    username = UsernameNotBlockedField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

class UserSettingsForm(forms.ModelForm):
    """
    Form for modifying the user settings.
    """

    class Meta:
        model = Account
        fields = ["safe_only", "show_comments", "tag_blacklist"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['safe_only'].widget = forms.CheckboxInput(attrs={'class': 'form-control', 'data-toggle': 'toggle'})
        self.fields['show_comments'].widget = forms.CheckboxInput(attrs={'class': 'form-control', 'data-toggle': 'toggle'})
        # TODO: implement the tag blacklist
        #self.fields['tag_blacklist'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': 'Ex.: wall rating:explicit user:girugamesh'})
        self.fields['tag_blacklist'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': "This feature wasn't implemented yet.", "disabled": ""})

class StaffUserGroupForm(forms.Form):
    group = forms.ChoiceField()
    
    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StaffUserGroupForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['group'].choices = booru.utils.get_all_roles()
