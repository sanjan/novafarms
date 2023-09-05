from django import forms
from .models import Supplier, Customer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg', 
            'placeholder': 'Password'
        }),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg', 
            'placeholder': 'Password Confirmation'
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', )

        widgets = {
        'username': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        'email': forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Username"
    }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password", 
            "class": "form-control",
            "placeholder": "Password"
        }),
    )

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Email"
    }))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "New Password"
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Confirm New Password"
    }), label="Confirm New Password")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Old Password"
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "New Password"
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        "placeholder": "Confirm New Password"
    }), label="Confirm New Password")

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        
        
class DailyProdFormStepOne(forms.Form):
    name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=False)
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )

class DailyProdFormStepTwo(forms.Form):
    product_name = forms.CharField(max_length=30, required=False)
    honey_type = forms.CharField(max_length=50, required=False)
