from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from account.models import Account

class UniqueUserEmailField(forms.EmailField):
    """
    An EmailField which only is valid if no Account has that email.
    """

    def validate(self, value):
        super(forms.EmailField, self).validate(value)
        try:
            Account.objects.get(email=value)
            raise forms.ValidationError("A user with that email already exists.")
        except Account.MultipleObjectsReturned:
            raise forms.ValidationError("A user with that email already exists.")
        except Account.DoesNotExist:
            pass

class UniqueUsernameField(UsernameField):
    """
    An UsernameField which raises error when the name is 
    already in use.
    """

    def validate(self, value):
        super(UsernameField, self).validate(value)
        try:
            Account.objects.get(username=value)
        except Account.DoesNotExist:
            raise forms.ValidationError("There's no user registered with that username.")

class UserRegisterForm(UserCreationForm):
    """
    Extends the built in UserCreationForm to include the Account email 
    and the form-control class in each widget.
    """

    email = UniqueUserEmailField(required=True, label='Email address')

    class Meta:
        model = Account
        fields = ("username", "email")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control'})

class UserAuthenticationForm(AuthenticationForm):
    """
    Extends the built in AuthenticationForm to add 
    the form-control class in each widget.
    """

    username = UniqueUsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)
        #self.fields['username'].widget = forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
