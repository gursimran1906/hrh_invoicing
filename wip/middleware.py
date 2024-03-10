from django_tenants.middleware.main import TenantMainMiddleware
from django.http import HttpResponseForbidden
from django_tenants.utils import get_tenant_model
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import logout

class CheckPaidPeriodMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        super().process_request(request)

        if not hasattr(request, 'tenant'):
            return

        # Get the current tenant from the request
        tenant = get_tenant_model().objects.get(schema_name=request.tenant.schema_name)

        if not tenant.paid_until >= timezone.now().date() and not tenant.on_trial:
            return HttpResponseForbidden(f"Client is not in the paid period. Subscription was only valid until {tenant.paid_until}.")

class ValidTenantUserMiddleware(TenantMainMiddleware):
    def process_request(self, request):
        super().process_request(request)

        if not hasattr(request, 'user'):
            print(request.user)
            return
        
        
        
        if request.user.is_authenticated:
            if request.user.is_invoice_department:
                return self.get_response(request)

            current_tenant = request.tenant.schema_name
            user_assigned_tenant = request.user.tenant

            if user_assigned_tenant == current_tenant:
                return self.get_response(request)
           
            logout(request)
            return HttpResponseForbidden("Access is not allowed. Contact administrators")
        else:
            redirect('login')

