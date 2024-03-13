from django.shortcuts import render
from backend.models import Invoice
from django_tenants.utils import schema_context
from .models import Client, Domain
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.

def all_org_clients(request):
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
                    client_info.append({
                            'client_name': mark_safe(f'<a href="{url}">{tenant.name.capitalize()}</a>'),
                            'no_of_available_invoice_users': tenant.no_of_available_invoice_users,
                            'no_of_available_admin_users': tenant.no_of_available_admin_users,
                            'paid_until': tenant.paid_until.strftime('%d-%m-%Y'),
                            'created_on': tenant.created_on,
                            'last_invoice_month': last_invoice_month,
                        })
        else:
            return HttpResponseForbidden('Access not allowed!')

    except Exception as e:
        print(e)

    return render(request, 'display_all_org_clients.html', {'client_info': client_info})