from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse, reverse_lazy
from urllib.parse import unquote
from .forms import CustomUserCreationForm, CustomPasswordResetForm
from .models import CustomUser
from django.contrib import messages
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model

from django.contrib.auth.views import PasswordResetConfirmView


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm_custom.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password reset successful. You can now log in.')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Password reset failed. Please try again.')
        return response

    def get_success_url(self):
        # Customize the success URL here
        return reverse_lazy('login')


def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Get the current tenant
            
            tenant = get_tenant_model().objects.get(schema_name=request.tenant.schema_name)
            is_invoice_department = form.cleaned_data.get('is_invoice_department')  
            
            if is_invoice_department and tenant.no_of_available_invoice_users > 0:
                user = form.save(commit=True, tenant=tenant.name)
                tenant.no_of_available_invoice_users -= 1
                messages.success(request, f'Successfully signed up {user} as an invoice user.')
                return redirect('login')
            elif tenant.no_of_available_admin_users > 0:
                user = form.save(commit=True, tenant=tenant.name)
                tenant.no_of_available_admin_users -= 1
                messages.success(request, f'Successfully signed up {user} as an admin user.')
                return redirect('login')
            else:
                messages.error(request, 'No available users for the chosen Care Home. Contact administrator.')
            
    else:
        form = CustomUserCreationForm()

    return render(request, 'register_user.html', {'form': form})

@login_required
def all_users(request):
    if request.user.is_invoice_department:
        all_users = CustomUser.objects.all().order_by('id')
    else:
        all_users = CustomUser.objects.filter(tenant=request.tenant.name).order_by('id')
    
    return render(request, 'all_users.html', {'users': all_users})  

@login_required
def send_password_reset(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    form = CustomPasswordResetForm({'email':user.email})
    
    if form.is_valid():
        form.user = user
        form.save(
            request=request,
            use_https=request.is_secure(),
            from_email=None,
        )
        messages.success(request, f"Password reset link sent to {user.email}")
    else:
        messages.error(request, f"Failed to send password reset link to {user.email}")
    return redirect('all_users')

@login_required
def remove_or_restrict_user(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"User {user.username} deactivated successfully.")
    return redirect('all_users')

@login_required
def activate_user(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} activate successfully.")
    return redirect('all_users')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            # Redirect to the next page if 'next' parameter exists, else redirect to a default page
            next_param = request.GET.get('next', '')
            next_page = unquote(next_param) if next_param else reverse('index_dashboard')
            return redirect(next_page)
        else:
            # Handle invalid login credentials
            return render(request, 'login_form.html', {'error_message': 'Invalid login credentials, Please check username or password'})
    else:
        return render(request, 'login_form.html')
    
def logout_view(request):
    username = str(request.user)  # Get the username
    logout(request)
    log_out_msg = 'Successfully Logged ' + username + ' out!!'
    return render(request, 'login_form.html', {'message': log_out_msg})   