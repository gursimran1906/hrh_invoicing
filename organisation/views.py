from django.shortcuts import render
from backend.models import Invoice
from django_tenants.utils import schema_context
from .models import Client, Domain
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClientAmendmentForm
from django.contrib import messages
# Create your views here.
@login_required
def amend_client_details(request, id):
    if request.user.is_invoice_department != True:
        messages.error(request, 'Access to page requested not allowed! Please speak to your administrator.')
        return redirect('index_dashboard')
    client = get_object_or_404(Client, pk=id)
    if request.method == 'POST':
        form = ClientAmendmentForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Care home details successfully updated')
            return redirect('index_dashboard') 
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = ClientAmendmentForm(instance=client)
    return render(request, 'amend_client_details.html', {'form': form, 'id':client.id})

@login_required
def all_org_clients(request):
    if request.user.is_invoice_department != True:
        messages.error(request, 'Access to page requested not allowed! Please speak to your administrator.')
        return redirect('index_dashboard')
    client_info = []
    try:
        if request.user.is_invoice_department:
            for tenant in Client.objects.all():  
                with schema_context(tenant.schema_name):
                    
                    url = 'https://' if request.is_secure() else 'http://'
                    url += str(tenant.schema_name) + '.'
                    url += get_current_site(request).domain.split('.',1)[-1]
                    
                    last_invoice_month = Invoice.objects.order_by('-date').first()
                    if not last_invoice_month == None:
                        last_invoice_month = last_invoice_month.date.strftime('%B %Y')
                    else:
                        last_invoice_month = '-'
                    all_users_url = reverse('all_users')
                    amende_care_home_url = reverse('amend_care_home',kwargs={'id': tenant.id})
                    '''
                    name = models.CharField(max_length=100)
                    address = models.TextField()
                    no_of_available_invoice_users = models.IntegerField() 
                    no_of_available_admin_users = models.IntegerField()
                    paid_until =  models.DateField()
                    on_trial = models.BooleanField()
                    bank_name=models.CharField(max_length=100)
                    bank_account_name = models.CharField(max_length=100)
                    bank_account_no=models.IntegerField() 
                    bank_sort_code=models.CharField(max_length=100)
                    invoice_footer = models.TextField()
                    one_to_one_rate_hourly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
                    created_on = models.DateField(auto_now_add=True)
                    auto_create_schema = True
                    '''
                    client_info.append({
                            'client_name': mark_safe(f'<a href="{url}">{tenant.name.capitalize()}</a>'),
                            'address':tenant.address,
                            'bank_name':tenant.bank_name,
                            'bank_account_name':tenant.bank_account_name,
                            'bank_account_no':tenant.bank_account_no,
                            'bank_sort_code':tenant.bank_sort_code,
                            'invoice_footer' : tenant.invoice_footer,
                            'one_to_one_rate_hourly' : tenant.one_to_one_rate_hourly,
                            'no_of_available_invoice_users': tenant.no_of_available_invoice_users,
                            'no_of_available_admin_users': tenant.no_of_available_admin_users,
                            'paid_until': tenant.paid_until.strftime('%d/%m/%Y'),
                            'created_on': tenant.created_on,
                            'last_invoiced_month': last_invoice_month,
                            'edit':mark_safe(f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{amende_care_home_url}">Edit Details</a>'),
                            'all_users': mark_safe(f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{all_users_url}">All Users</a>')
                        })
        else:
            return HttpResponseForbidden('Access not allowed!')

    except Exception as e:
        print(e)

    return render(request, 'display_all_org_clients.html', {'client_info': client_info})