from base64 import urlsafe_b64encode
from click import get_current_context
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import CustomUser


class CustomPasswordResetForm(PasswordResetForm):
    user = None

    def get_users(self, email):
        """
        Instead of getting all users in an email,
        just sent the user that we want to reset password for.
        """
        return [self.user]


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'is_invoice_department',
                  'email',) + UserCreationForm.Meta.fields

    def save(self, commit=True, tenant=None):
        user = super().save(commit=False)

        if tenant:
            user.tenant = tenant

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
