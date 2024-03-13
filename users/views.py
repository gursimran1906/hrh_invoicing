from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from urllib.parse import unquote
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.contrib.auth.decorators import login_required


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
                tenant.no_of_available_normal_users -= 1
                messages.success(request, f'Successfully signed up {user} as an admin user.')
                return redirect('login')
            else:
                messages.error(request, 'No available users for the chosen Care Home. Contact administrator.')
            
    else:
        form = CustomUserCreationForm()

    return render(request, 'register_user.html', {'form': form})

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