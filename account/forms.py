from django import forms
from django.contrib.auth.forms import UserCreationForm
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
