from email_config.utils import send_email
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import shutil
from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice, OneToOne, Client,  LocalAuthority, OneToOneAgency, Attendance, MoneyIn, CreditNote, ContractDocument
from .forms import ClientHalfForm, LocalAuthorityForm,  OneToOneForm, OneToOneAgencyForm, InvoiceForm, MoneyInForm, CreditNoteForm, ContractDocumentForm, ClientFullForm,ClientFullFormToSave
from django.db.models import F, Count, Q, Sum
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
import calendar
from django.utils import formats
from django.urls import reverse
from django.utils.safestring import mark_safe
from datetime import date, datetime, timedelta
from django.core.mail import EmailMessage
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
import csv
from django.utils.encoding import smart_str
from django_tenants.utils import get_tenant_model
import os
from django.http import HttpResponse
from django.core.files import File
from django.http import HttpResponse
from django.core.files.temp import NamedTemporaryFile
from zipfile import ZipFile
import tempfile
from weasyprint import HTML
from django.core import mail
from django.http import HttpResponse
from django.shortcuts import render
import matplotlib
import json
matplotlib.use('Agg')


@login_required
def check_subscription(request):
    # Get the current tenant
    tenant = get_tenant_model().objects.get(schema_name=request.tenant.schema_name)
    if tenant.paid_until:
        current_date = datetime.today()
        one_month_away = current_date + relativedelta(days=21)
        date_one_month_away = datetime.date(one_month_away)
        if tenant.paid_until < date_one_month_away:
            formatted_paid_until = tenant.paid_until.strftime('%d %B %Y')
            return JsonResponse({'status': 'expired', 'paid_until': formatted_paid_until})

    return JsonResponse({'status': 'ok'})


@login_required
def test(request):
    return render(request, 'test.html')


@login_required
def all_clients_view(request):

    clients = Client.objects.all().order_by('-date_joined').values('id', 'name', 'date_of_birth', 'address', 'contact_number',
                                                                   'date_joined', 'date_left', 'email', 'client_type',
                                                                   'rates',
                                                                   'payable_by__name', 'respite', 'notes', 'timestamp')

    for client in clients:
        client_view_url = reverse('client_view', args=[client['id']])
        client_name = client['name']
        rates = json.loads(client['rates']) if type(client['rates']) == type('') else client['rates']
        rates_html = ''
        for rate in rates:  
            rates_html = rates_html + f'Desc: {rate['description']}, Amount: £{rate['amount']}, Status: {rate['status']}<br><br>'
        client['rates'] = mark_safe(rates_html)
        client['name'] = mark_safe(
            f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{client_view_url}">{client_name}</a>')
        edit_client_url = reverse('edit_client', args=[client['id']])
        client['edit'] = mark_safe(f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{edit_client_url}">Edit</a>')

    return render(request, 'all_clients_table.html', {'clients': clients})


@login_required
def download_all_clients_data(request):

    response = HttpResponse(content_type='text/csv')
    today = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="all_clients_including_previous-{
        today}.csv"'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    fields = [
        'id', 'name', 'date_of_birth', 'address', 'contact_number',
        'date_joined', 'date_left', 'email', 'client_type',
        'rates',
        'payable_by', 'respite', 'notes',]

    clients = Client.objects.all().order_by('date_joined').prefetch_related(
        'payable_by')

    writer.writerow([smart_str(field) for field in fields])
    for client in clients:
        data_row = [smart_str(getattr(client, field)) for field in fields]
        writer.writerow(data_row)
    return response


@login_required
def download_current_clients_data(request):

    response = HttpResponse(content_type='text/csv')
    today = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="current_clients_{
        today}.csv"'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    fields = [
        'id', 'name', 'date_of_birth', 'address', 'contact_number',
        'date_joined', 'email', 'client_type',
        'rates',
       
        'payable_by', 'respite', 'notes',]

    clients = Client.objects.filter(date_left__isnull=True).order_by(
        'date_joined').prefetch_related('payable_by')

    writer.writerow([smart_str(field) for field in fields])
    for client in clients:
        data_row = [smart_str(getattr(client, field)) for field in fields]
        writer.writerow(data_row)
    return response


@login_required
def download_all_one_to_ones(request):
    response = HttpResponse(content_type='text/csv')
    today = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="all_one_to_ones_{
        today}.csv"'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    one_to_ones = OneToOne.objects.all().order_by(
        'date').prefetch_related('customer')

    one_to_one_fields = [field.name for field in OneToOne._meta.get_fields()]

    # Write header row
    writer.writerow([smart_str(field) for field in one_to_one_fields])

    # Write data rows
    for one_to_one in one_to_ones:
        data_row = [smart_str(getattr(one_to_one, field))
                    for field in one_to_one_fields]
        writer.writerow(data_row)

    return response


@login_required
def download_this_months_one_to_ones(request):
    response = HttpResponse(content_type='text/csv')
    today = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    month = datetime.now().strftime('%m-%Y')
    response['Content-Disposition'] = f'attachment; filename="{
        month}_one_to_ones_{today}.csv"'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    first_day = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = datetime.now().replace(day=1, month=datetime.now().month +
                                      1, hour=0, minute=0, second=0, microsecond=0)

    one_to_ones = OneToOne.objects.filter(
        date__range=[first_day, last_day]).order_by('date').prefetch_related('customer')

    one_to_one_fields = [field.name for field in OneToOne._meta.get_fields()]

    # Write header row
    writer.writerow([smart_str(field) for field in one_to_one_fields])

    # Write data rows
    for one_to_one in one_to_ones:
        data_row = [smart_str(getattr(one_to_one, field))
                    for field in one_to_one_fields]
        writer.writerow(data_row)

    return response


@login_required
def client_view(request, client_id):

    client = Client.objects.get(pk=client_id)

    # Calculate total invoices for the client
    total_invoices = Invoice.objects.filter(client=client).aggregate(Sum('costs'))[
        'costs__sum'] or Decimal('0.00')
    total_invoices = round(total_invoices, 2)

    # Calculate total monies in for the client
    total_monies_in = MoneyIn.objects.filter(invoices_to_allocate__client=client).aggregate(
        Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_monies_in = round(total_monies_in, 2)

    # Calculate client balance
    client_balance = total_monies_in - total_invoices
    client_balance = round(client_balance, 2)

    context = {
        'client': client,
        'total_invoices': total_invoices,
        'total_monies_in': total_monies_in,
        'client_balance': client_balance,
    }
    if request.user.is_invoice_department:
        return render(request, 'client_home.html', context)
    else:
        messages.error(request, "No contract document saved for this client.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def invoices_view(request):

    invoices = Invoice.objects.all()

    return render(request, 'invoices_list.html', {'invoices': invoices})

def download_contract_document(request, client_id):
    try:
        contract_document = ContractDocument.objects.get(client=client_id)
        file_path = contract_document.document.path
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    except ContractDocument.DoesNotExist:
        
        messages.error(request, "No contract document saved for this client.")
      
        return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def add_client(request):
    if request.method == 'POST':
        form_data = request.POST.copy()
        rate = json.dumps([{'amount':form_data['daily_rate_amount'],'status':'active','description':form_data['daily_rate_desc']}])
      
       
        form_data['rates'] = rate
       
        form = ClientFullFormToSave(form_data)
        if form.is_valid():
            client = form.save()   
            print(client.rates)
            contract_document = request.FILES.get('contract_document')
            if contract_document:
                ContractDocument.objects.create(
                    client=client, document=contract_document)
            messages.success(
                request, f"{form._meta.model.__name__} added successfully.")
            return redirect('add_client')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")

    else:
        form = ClientHalfForm()
        client_objects = Client.objects.filter(date_left__isnull=True).prefetch_related(
        'payable_by'
        ).annotate(
            
            payable_by_name=F('payable_by__name'),
            
            resident_ref=F('resident_name_number')
        ).order_by('date_joined').values('name', 'address', 'rates','payable_by_name', 'client_type','contact_number', 'date_joined', 'email',
                                                'client_type',  
                                                'resident_ref', 'respite', 'id'
        
                                            )
        for client in client_objects:
            client_view_url = reverse('client_view', args=[client['id']])
            download_contract_url = reverse('download_contract', args=[client['id']])
            client_name = client['name']
            
            rates = json.loads(client['rates']) if type(client['rates']) == type('') else client['rates']
            rates_html = ''
            for rate in rates:  
                rates_html = rates_html + f'Desc: {rate['description']}, Amount: £{rate['amount']}, Status: {rate['status']}<br><br>'

            
            client['rates'] = mark_safe(rates_html)
            client['name'] = mark_safe(
                f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{client_view_url}">{client_name}</a>')
            edit_client_url = reverse('edit_client', args=[client['id']])
            client['Contract'] = mark_safe(f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{download_contract_url}">Dowload Contract</a>')
            client['edit'] = mark_safe(f'<a class="font-medium text-blue-600 dark:text-blue-500 hover:underline" href="{edit_client_url}">Edit</a>')

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'Client', 'objects': client_objects})


@login_required
def add_local_authority(request):
    if request.method == 'POST':
        form = LocalAuthorityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{form._meta.model.__name__} added successfully.")
            return redirect('add_local_authority')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = LocalAuthorityForm()

    local_authority_objects = LocalAuthority.objects.values(
        'id', 'name',  'contact_number', 'email', 'address', 'hide_client_deatils')

    for local_authority in local_authority_objects:
        edit_url = reverse('edit_local_authority',
                           args=[local_authority['id']])
        local_authority['edit'] = mark_safe(f'<a href="{edit_url}">Edit</a>')

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'Local Authority', 'objects': local_authority_objects})


# @login_required
# def add_rate(request):
#     if request.method == 'POST':
#         form = RateForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request, f"{form._meta.model.__name__} added successfully.")
#             return redirect('add_rate')
#         else:
#             messages.error(
#                 request, "Form submission failed. Please check the errors.")
#     else:
#         form = RateForm()

#     rate_objects = Rate.objects.values()

#     for rate in rate_objects:
#         edit_url = reverse('edit_rate', args=[rate['id']])
#         rate['edit'] = mark_safe(f'<a href="{edit_url}">Edit</a>')

#     return render(request, 'add_model_display_form.html', {'form': form, 'title': 'Rate', 'objects': rate_objects})


@login_required
def add_one_to_one(request):
    if request.method == 'POST':
        form = OneToOneForm(request.POST)
        if form.is_valid():
            inst = form.save()

            messages.success(
                request, f"{form._meta.model.__name__} added successfully.")
            return redirect('add_one_to_one')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = OneToOneForm()

    one_to_one_objects = OneToOne.objects.select_related('customer').order_by(
        '-date').values('id', 'date', 'hours', 'customer__name')
    for one_to_one in one_to_one_objects:
        edit_url = reverse('edit_one_to_one', args=[one_to_one['id']])
        one_to_one['edit'] = mark_safe(f'<a href="{edit_url}">Edit</a>')

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'One To One', 'objects': one_to_one_objects})


@login_required
def add_one_to_one_agency(request):
    if request.method == 'POST':
        form = OneToOneAgencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{form._meta.model.__name__} added successfully.")
            return redirect('add_one_to_one_agency')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = OneToOneAgencyForm()

    one_to_one_objects = OneToOneAgency.objects.values()

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'One To One', 'objects': one_to_one_objects})


@login_required
def add_money_in(request):
    if request.method == 'POST':
        form = MoneyInForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{form._meta.model.__name__} added successfully.")
            return redirect('add_money_in')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = MoneyInForm()

    one_to_one_objects = MoneyIn.objects.values()

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'Money In', 'objects': one_to_one_objects})


@login_required
def add_credit_note(request):
    if request.method == 'POST':
        form = CreditNoteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, f"{form._meta.model.__name__} added successfully.")
            except Exception as e:
                messages.error(request, str(e))
            return redirect('add_credit_note')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = CreditNoteForm()

    one_to_one_objects = CreditNote.objects.values()

    return render(request, 'add_model_display_form.html', {'form': form, 'title': 'Credit Note', 'objects': one_to_one_objects})


@login_required
def edit_invoice(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, f'Invoice {
                             invoice_number} successfully updated!')
            return redirect('invoices_list')
        else:

            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = InvoiceForm(instance=invoice)

    return render(request, 'edit_models.html', {'form': form, 'title': 'Invoice'})


# @login_required
# def edit_client(request, id):
#     client = get_object_or_404(Client, id=id)

#     if request.method == 'POST':
#         form = ClientHalfForm(request.POST, instance=client)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'Client data successfully updated!')
#             return redirect('add_client')
#         else:
#             messages.error(
#                 request, "Form submission failed. Please check the errors.")
#     else:
#         form = ClientHalfForm(instance=client)

#     return render(request, 'edit_models.html', {'form': form, 'title': 'Client'})

@login_required
def edit_client(request, id):
    client = get_object_or_404(Client, id=id)

    contract_documents = ContractDocument.objects.filter(client=client)

    if request.method == 'POST':
        client_form = ClientFullForm(request.POST, instance=client)
        if contract_documents.exists():
            document = contract_documents.first()
            document_form = ContractDocumentForm(request.FILES, request.POST, instance=document)
        else:
            document_form = ContractDocumentForm(request.FILES, request.POST)

        if client_form.is_valid() and document_form.is_valid():
            client = client_form.save(commit=False)
            document = document_form.save(commit=False)
            document.client = client
            document.save()
            
            rates_prev = json.loads(client.rates) if type(client.rates) == type('ss') else client.rates
            rates_len_prev = len(rates_prev) - 1 
            total_sub_rates_forms = request.POST['form-TOTAL_FORMS']
            rates=[]
            

            for i in range(rates_len_prev, int(total_sub_rates_forms)):
                
                amount = request.POST[f'form-{i}-amount']
                status = request.POST[f'form-{i}-status']
                description = request.POST[f'form-{i}-description']
                
                rates.append({'amount':amount,'status':status, 'description':description})
            for rate in rates_prev:
                rate['status'] = 'inactive'
            rates_prev.extend(rates)
            client.rates = json.dumps(rates_prev)
            client.save()
            messages.success(request, 'Client datasuccessfully updated!')
            return redirect('all_clients_view')
        else:
            messages.error(request, "Form submission failed. Please check the errors.")
    else:
        client_form = ClientFullForm(instance=client)
        if contract_documents.exists():
            
            document = contract_documents.first()
            document_form = ContractDocumentForm(instance=document)
        else:
            document_form = ContractDocumentForm()

    return render(request, 'edit_models.html', {
        'form': client_form,
        'document_form': document_form,
        'contract_documents': contract_documents,
        'title': 'Client'
    })

@login_required
def edit_local_authority(request, id):
    local_authority = get_object_or_404(LocalAuthority, id=id)
    if request.method == 'POST':
        form = LocalAuthorityForm(request.POST, instance=local_authority)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Local authority data successfully updated!')
            return redirect('add_local_authority')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = LocalAuthorityForm(instance=local_authority)

    return render(request, 'edit_models.html', {'form': form, 'title': 'Local Authority'})


# @login_required
# def edit_rate(request, id):
#     rate = get_object_or_404(Rate, id=id)
#     if request.method == 'POST':
#         form = RateForm(request.POST, instance=rate)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'Rate data successfully updated!')
#             return redirect('add_rate')
#         else:
#             messages.error(
#                 request, "Form submission failed. Please check the errors.")
#     else:
#         form = RateForm(instance=rate)

#     return render(request, 'edit_models.html', {'form': form, 'title': 'Rate'})


@login_required
def edit_one_to_one(request, id):
    one_to_one = get_object_or_404(OneToOne, id=id)
    if request.method == 'POST':
        form = OneToOneForm(request.POST, instance=one_to_one)
        if form.is_valid():
            form.save()
            messages.success(request, f'One to One data successfully updated!')
            return redirect('add_one_to_one')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = OneToOneForm(instance=one_to_one)

    return render(request, 'edit_models.html', {'form': form, 'title': 'One to One'})


@login_required
def edit_money_in(request, id):
    money_in = get_object_or_404(MoneyIn, id=id)
    if request.method == 'POST':
        form = MoneyInForm(request.POST, instance=money_in)
        if form.is_valid():
            form.save()
            messages.success(request, f'Money In data successfully updated!')
            return redirect('add_money_in')
        else:
            messages.error(
                request, "Form submission failed. Please check the errors.")
    else:
        form = OneToOneForm(instance=money_in)

    return render(request, 'edit_models.html', {'form': form, 'title': 'Money In'})


@login_required
def unallocated_money_in(request):
    money_in_objects = MoneyIn.objects.filter(balance_left__gt=0)
    invoices_objects = Invoice.objects.filter(
        Q(settled=False) | Q(settled__isnull=True))

    options = []
    for invoice in invoices_objects:
        options.append(f'<option value="{invoice.invoice_number}">{
                       invoice.invoice_number} - ({invoice.client.payable_by}) Client: {invoice.client}</option>')

    # Join the options and mark it as safe
    options_html = mark_safe('\n'.join(options))

    return render(request, 'allocate_monies_in.html', {'money_in_objects': money_in_objects, 'options_html': options_html})


@login_required
def allocate_money_in(request, id):
    selected_invoices = request.POST.getlist('unsettled_invoices')
    money_in_obj = get_object_or_404(MoneyIn, id=id)

    balance_left_money_in = money_in_obj.balance_left
    for inv_num in selected_invoices:
        invoice = get_object_or_404(Invoice, invoice_number=inv_num)

        costs_pending = invoice.costs - invoice.amount_allocated
        invoice.amount_allocated = invoice.amount_allocated + money_in_obj.balance_left
        invoice.save()
        balance_left_money_in = balance_left_money_in - costs_pending
        money_in_obj.invoices_to_allocate.add(invoice)

        if balance_left_money_in < 0:
            money_in_obj.balance_left = 0
            money_in_obj.save()
            break
        elif balance_left_money_in > 0:
            invoice.settled = True
            invoice.save()
        else:
            money_in_obj.balance_left = 0
            money_in_obj.save()
            invoice.settled = True
            invoice.save()
            break

        money_in_obj.balance_left = balance_left_money_in
        money_in_obj.save()

    return redirect('monies_in')


@login_required
def dashboard(request):

    one_month_ago = date.today() - timedelta(days=30)

    unsettled_overdue_invoices = Invoice.objects.filter(
        settled=False,
        date__lte=one_month_ago
    )

    return render(request, 'dashboard.html', {'unsettled_overdue_invoices': unsettled_overdue_invoices})


@login_required
def get_attendance_data(request):
    today = date.today()

    start_date = today.replace(day=1)
    end_date = today.replace(day=monthrange(today.year, today.month)[1])

    all_dates = [start_date + timedelta(days=x)
                 for x in range((end_date - start_date).days + 1)]

    presents_per_day = Attendance.objects.filter(
        date__range=[start_date, end_date],
        present=True
    ).values('date').annotate(count=Count('id'))

    present_data = {entry['date']: entry['count']
                    for entry in presents_per_day}
    data = [present_data.get(d, 0) for d in all_dates]

    labels = [date.strftime('%d-%m-%Y') for date in all_dates],

    return JsonResponse({
        "title": f"Bed Occupancy Chart",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Number of Beds Occupied",
                "borderColor": "rgb(37 99 235)",
                "data": data,
            }]
        },
    })


@login_required
def generate_monthly_attendance_chart(request, month_year):
    month_year_date = datetime.strptime(month_year, '%Y-%m').date()

    start_date = month_year_date.replace(day=1)
    end_date = month_year_date.replace(day=monthrange(
        month_year_date.year, month_year_date.month)[1])

    all_dates = [start_date + timedelta(days=x)
                 for x in range((end_date - start_date).days + 1)]

    presents_per_day = Attendance.objects.filter(
        date__range=[start_date, end_date],
        present=True
    ).values('date').annotate(count=Count('id'))

    present_data = {entry['date']: entry['count']
                    for entry in presents_per_day}

    data = [present_data.get(d, 0) for d in all_dates]

    labels = [date.strftime('%d/%m') for date in all_dates]

    fig, ax = plt.subplots()
    ax.set_title(f"Bed Occupancy Chart for {
                 month_year_date.strftime('%B %Y')}")
    ax.plot(labels, data, label="Number of Beds Occupied", color="#417690")
    ax.legend()

    ax.set_xticks(labels)
    ax.set_xticklabels(labels, rotation=45, ha='right')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=600)
    plt.close()

    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="Bed_Occupancy_Chart_{
        month_year_date.strftime("%B %Y")}.png"'

    return response


@login_required
def generate_monthly_attendance_table(request, month_year):
    month_year_date = datetime.strptime(month_year, '%Y-%m').date()

    start_date = month_year_date.replace(day=1)
    end_date = month_year_date.replace(day=monthrange(
        month_year_date.year, month_year_date.month)[1])

    all_dates = [start_date + timedelta(days=x)
                 for x in range((end_date - start_date).days + 1)]

    year, month = map(int, month_year.split("-"))
    attendances = Attendance.objects.filter(date__year=year, date__month=month)

    clients = Client.objects.values()

    clients = Client.objects.all()

    attendance_data = []
    for client in clients:
        client_attendance = []
        for date in all_dates:
            try:
                attendance = Attendance.objects.get(client=client, date=date)
                client_attendance.append(attendance.present)
            except Attendance.DoesNotExist:
                client_attendance.append('N/A')

        attendance_data.append({
            'client': client,
            'attendance': client_attendance,
        })

    html_content = f"""
    <html>
    <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <style>
        @page {{
            size: A0 landscape;
        }}
        body {{
            font-family:  Arial, sans-serif;
            }}
        </style>
    </head>

    <body class=''>
        <h2>Monthly Attendance Table - {month_year_date.strftime("%B %Y")}</h2>
        <div style="clear:both;"><div>
        <table class='table w-unset'>
            <thead>
                <tr>
                    <th>Client</th>
                    {''.join([f'<th>{date.strftime('%Y-%m-%d')}</th>' for date in all_dates])}
                </tr>
            </thead>
            <tbody>
                {''.join([f'<tr><td>{client['client']}</td>{''.join([f'<td>{status}</td>' for status in client['attendance']])}</tr>' for client in attendance_data])}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Create a response with PDF mime type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=monthly_attendance_{
        month_year_date.strftime("%B_%Y")}.pdf'

    # Generate PDF using WeasyPrint and write it to the response
    HTML(string=html_content).write_pdf(response)

    return response


@login_required
def clients_attendance(request):
    if request.method == 'POST':
        month_year = request.POST.get('month_year')
        context = {}
        try:
            context['selected_month_year'] = month_year
            year, month = map(int, month_year.split("-"))

        except ValueError:
            messages.error(request, "Incorrect Format for Month and Year")

        today = date.today()

        # Check if the selected month is in the past, present, or future
        if (year, month) < (today.year, today.month):
            # For past months, allow all days
            days_in_month = calendar.monthrange(year, month)[1]
            days_of_month = [date(year, month, day)
                             for day in range(1, days_in_month + 1)]
        elif (year, month) == (today.year, today.month):
            # For the current month, limit days to today
            days_of_month = [date(today.year, today.month, day)
                             for day in range(1, today.day+1)]
        else:
            days_of_month = []
            # For future months, return an error message
            messages.error(
                request, "Selected month is in the future. Please select current month or a month in past.")

        context['days'] = days_of_month

        # Calculate the first and last day of the month
        first_day_of_month = datetime(year, month, 1).date()
        last_day_of_month = datetime(
            year, month, monthrange(year, month)[1]).date()

        # Filter attendances for the given year and month
        attendances = Attendance.objects.filter(
            date__year=year, date__month=month)

        # Filter clients who have 'date_left' set and 'date_left' is less than the end of the month
        clients = Client.objects.filter(
            Q(date_joined__lte=last_day_of_month) & (
                Q(date_left__isnull=True) | (
                    Q(date_left__gte=first_day_of_month) & Q(date_left__lte=last_day_of_month)))
        ).values()

        attendance_data = []

        for client in clients:
            client_id = client['id']
            client_name = client['name']
            client_data = {'id': client_id,
                           'name': client_name, 'attendance': {}}

            for day in days_of_month:
                attendance_entry = attendances.filter(
                    client__id=client_id, date=day).first()
                present = attendance_entry.present if attendance_entry else "N/A"
                client_data['attendance'][day] = present

            attendance_data.append(client_data)

        context = {'clients': attendance_data,
                   'days_of_month': days_of_month, "selected_month_year": month_year}

        return render(request, 'attendance.html', context)
    else:
        return render(request, 'attendance.html')


@login_required
def mark_clients_attendance(request):
    try:
        count = 0
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            try:
                client_id, raw_date = key.split('/')

                client = Client.objects.get(pk=client_id)

                date_obj = datetime.strptime(raw_date, "%B %d, %Y").date()

                present = value == 'on'

                existing_attendance = Attendance.objects.filter(
                    client=client, date=date_obj).first()

                if existing_attendance:
                    existing_attendance.present = present
                    existing_attendance.save()
                else:
                    Attendance.objects.create(
                        client=client, date=date_obj, present=present)
                    count += 1
            except ValueError as e:
                messages.error(request, f'Attendance not marked. {
                               key, value}. Error:{str(e)}')

        messages.success(
            request, f'Attendance successfully marked {count} times.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('clients_attendance')

@login_required
def general_invoices(request):
    try:
        action = request.POST.get('action')
        if action == 'generate':
            generate_monthly_invoices(request)
        elif action =='send':
            send_monthly_invoices(request)
        elif action == 'download':
            return download_all_invoices(request)
        else:
            messages.error(
            request, f'Please choose a valid action.')
            return redirect('invoices_list')
    except Exception as e:
        messages.error(
            request, f'An error was encountered. \
                Please contact your adminsistrators and send them a photo of this message. Error: {e}')
    return redirect('invoices_list')

@login_required
def generate_monthly_invoices(request):
    try:
        today = date.today()
        month_year = request.POST.get('month_year')

        month_year_date = datetime.strptime(month_year, '%Y-%m').date()

        first_day_of_month = month_year_date.replace(day=1)
        last_day_of_month = (
            first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        last_day_attendance = Attendance.objects.filter(date=last_day_of_month)

        # if not last_day_attendance.exists():
        #     messages.error(request, f"No attendance recorded on the last day of {month_year_date.strftime('%B %Y')}. Invoices not generated.")
        #     return redirect('invoices_list')

        existing_invoices = Invoice.objects.filter(
            Q(date__range=(first_day_of_month, last_day_of_month))
        )

        # if existing_invoices.exists():
        #     messages.error(request, f"Monthly invoices for {month_year_date.strftime('%B %Y')} already generated.")
        #     return redirect('invoices_list')

        clients_with_attendance = Client.objects.filter(
            attendance__date__range=(first_day_of_month, last_day_of_month)).distinct()

        for client in clients_with_attendance:
            # Calculate attendance count for the current month
            attendance_count = Attendance.objects.filter(
                client=client, date__range=(first_day_of_month, last_day_of_month)).count()
            
            rates = json.loads(client.rates) if type(client.rates) == type('') else client.rates
            active_rate = ''
            for rate in rates: 
                if rate['status'] == 'active':
                    active_rate = rate
            # Calculate total cost based on attendance count and rate
            total_cost = attendance_count * round(Decimal(active_rate['amount']),4)

            invoice = Invoice.objects.create(
                client=client,
                date=last_day_of_month,
                desc=active_rate['description'],
                amount_allocated=0.00,
                costs=total_cost,
                units=attendance_count,
            )

        clients_with_one_to_one = Client.objects.filter(
            onetoone__date__range=(first_day_of_month, last_day_of_month)).distinct()
        one_to_one_rate = 0.00

        for client in clients_with_one_to_one:
            # Calculate total hours for the current month
            total_hours = OneToOne.objects.filter(customer=client, date__range=(
                first_day_of_month, last_day_of_month)).aggregate(Sum('hours'))['hours__sum'] or 0

            # Calculate total cost based on total hours and rate (assuming client has a rate field)
            total_cost = total_hours * one_to_one_rate.amount

            # Create OneToOne Invoice
            invoice = Invoice.objects.create(
                client=client,
                date=last_day_of_month,
                desc=one_to_one_rate,
                costs=total_cost,
                units=total_hours,

            )

        messages.success(request, f'Invoices for {month_year_date.strftime("%B %Y")} successfully generated.')

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('invoices_list')


@login_required
def send_monthly_invoices(request):
    try:
        today = date.today()
        month_year = request.POST.get('month_year')

        month_year_date = datetime.strptime(month_year, '%Y-%m').date()

        first_day_of_month = month_year_date.replace(day=1)
        last_day_of_month = (
            first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        existing_invoices = Invoice.objects.filter(
            Q(date__range=(first_day_of_month, last_day_of_month))
        )
        if not existing_invoices.exists():
            messages.error(request, f'No invoices to send for {
                           month_year_date.strftime("%B %Y")}')
            return redirect('invoices_list')

        all_emails_sent = False
        invoices_failed = []
        connection = mail.get_connection()
        connection.open()
        for invoice in existing_invoices:
            if invoice.sent_to_client == False:
                try:
                    sent = send_invoice_email(
                        invoice.invoice_number, invoice.client.email, month_year_date, request.user, request.tenant)
                    print(sent)
                    if sent == True:
                        invoice.sent_to_client = True
                        all_emails_sent = True
                        invoice.save()
                except Exception as e:
                    messages.error(request, f'Error in sending invoice {
                                   invoice.invoice_number}')
            else:
                all_emails_sent = False
                invoices_failed.append(invoice.invoice_number)
        connection.close()
        if all_emails_sent:
            messages.success(request, f'Invoices for {
                             month_year_date.strftime("%B %Y")} successfully sent.')
        else:
            messages.error(request, f'Invoices {invoices_failed} of month {
                           month_year_date.strftime("%B %Y")} already sent to clients')
    except Exception as e:
        connection.close()
        messages.error(
            request, f'An error was encountered. Please contact your adminsistrators and send them a photo of this message. Error: {e}')

    return redirect('invoices_list')


@login_required
def download_all_invoices(request):

    try:
        today = date.today()
        month_year = request.POST.get('month_year')

        month_year_date = datetime.strptime(month_year, '%Y-%m').date()

        first_day_of_month = month_year_date.replace(day=1)
        last_day_of_month = (
            first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        existing_invoices = Invoice.objects.filter(
            Q(date__range=(first_day_of_month, last_day_of_month))
        )
        if not existing_invoices.exists():
            messages.error(request, f'No invoices to download for {
                           month_year_date.strftime("%B %Y")}')
            return redirect('invoices_list')

        mem_zip = BytesIO()

        with ZipFile(mem_zip, mode="w") as zf:
            invoices_failed = []
            for invoice in existing_invoices:
                try:
                    # Replace with your function to generate PDFs
                    invoice_file = make_pdf_of_invoice(
                        invoice.invoice_number, False, request.user, request.tenant)
                    invoice_file_name = f"Invoice_ {
                        invoice.invoice_number}.pdf"
                    zf.writestr(invoice_file_name, invoice_file)

                except Exception as e:
                    invoices_failed.append(invoice.invoice_number)
                    messages.error(request, f'Error in generating invoice {
                                   invoice.invoice_number}')

            if invoices_failed:
                messages.error(request, f'Error in generating invoices: {
                               invoices_failed}')

        # Prepare the response
        mem_zip.seek(0)
        response = HttpResponse(mem_zip.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="invoices_{
            month_year_date.strftime("%Y-%m")}.zip'

        return response

    except Exception as e:
        messages.error(
            request, f'An error was encountered. Please contact your administrators and send them a photo of this message. Error: {e}')

    return redirect('invoices_list')


def make_pdf_of_invoice(invoice_number, hide_client_details, user, tenant):
    invoice = Invoice.objects.get(invoice_number=invoice_number)
    datetime_now = datetime.now().strftime('%d-%m-%Y @%H:%M')

    html_content = f'''
        <html>
            <head>
                <title>Invoice {invoice.invoice_number}</title>
                <!-- Include Bootstrap CDN links -->
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                <style>

            </style>
             </head>
            <body style="font-family:  Arial, sans-serif;">
                <div class="container">
                    <div class="row mb-5">
                        <div class="col-8">

                            <h1>{tenant.name.upper()}</h1>
                        </div>
                        <div class="col-4 ">
                            <h1 class='float-right'>Invoice</h1>
                        </div>
                    </div>
                    <div class='mt-5 w-25 mb-5'>
                        <table class="table table-bordered">
                            <tr>
                                <td><strong>Invoice To<strong></td>
                            </tr>'''
    if invoice.client.client_type == 'authorities_funded':
        html_content += f'''    <tr>
                                    <td>{invoice.client.payable_by.name}<br>{invoice.client.payable_by.address}</td>
                                </tr> '''
    else:
        html_content += f'''    <tr>
                                    <td>{invoice.client.name}<br>{invoice.client.address}</td>
                                </tr> '''
    html_content += f'''
                        </table>
                    </div>
                    <div class='mt-5 mb-3 row'>
                    '''
    if hide_client_details:
        if invoice.client.payable_by:
            if invoice.client.payable_by.hide_client_deatils:
                html_content += f'''
                                <p class='col'><strong>Client:</strong> - </p>'''
    else:
        html_content += f''' <p class='col'><strong>Client:</strong> {
            invoice.client.name} </p>'''
    rate = invoice.costs / invoice.units
    html_content += f'''
                          <p class='col'><strong>Date:</strong> {invoice.date.strftime("%d/%m/%Y")}</p>
                           <p class='col'><strong>Invoice No:</strong> {invoice.invoice_number}</p>
                           <p class='col'><strong>Resident Ref:</strong> {invoice.client.resident_name_number}</p>

                    </div>
                    <table class="table table-bordered h-50 mb-5">
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>Units</th>
                                <th>Rate</th>
                                <th>Amount(£)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{invoice.desc}</td>
                                <td>{invoice.units}</td>
                                <td>{rate}</td>
                                <td>{invoice.costs}</td>
                            </tr>

                            <tr>
                                <td colspan='3' ><strong>Subtotal</strong></td>
                                <td>£{invoice.costs}</td>
                            </tr>
                            <tr>
                                <td colspan='3' ><strong >VAT Total</strong></td>
                                <td>£0.00</td>
                            </tr>
                            <tr>
                                <td colspan='3'><h3>Total</h3></td>
                                <td><h3>£{invoice.costs}</h3></td>
                            </tr>
                        </tbody>
                    </table>'''
    if invoice.additional_notes:
        html_content += f'''
                        <div><strong>Notes: </strong>{invoice.additional_notes}</div>'''
    html_content += f'''

                    <div class='row fixed-bottom'>
                        <div class='col mb-5 pb-5'>
                            <h4>Paying by Cheque</h4>
                            <table class='table'>
                                <tr>
                                    <td>Payable to:</td>
                                    <td>{tenant.bank_account_name}</td>
                                </tr>

                                <tr>
                                    <td>Post to:</td>
                                    <td>{tenant.address}</td>
                                </tr>
                            </table>

                        </div>
                        <div class='col mb-5 pb-5'>
                            <h4>Paying by BACS</h4>
                            <table class='table' >
                                <tr>
                                    <td>Account Name:</td>
                                    <td>{tenant.bank_account_name}</td>
                                </tr>

                                <tr>
                                    <td>Bank:</td>
                                    <td>{tenant.bank_name}</td>
                                </tr>
                                <tr>
                                    <td>Account no:</td>
                                    <td>{tenant.bank_account_no}</td>
                                </tr>
                                <tr>
                                    <td>Sort Code:</td>
                                    <td>{tenant.bank_sort_code}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-12 text-center">
                                        <p>{tenant.invoice_footer}</p>
                        </div>
                        <div class='col-md-12 text-center' ><small class='fs-6'>Invoice generated by {user} on {datetime_now}hrs</small></div>
                    </div>

                </div>



            <!-- Include Bootstrap CDN scripts -->
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
            </body>
        </html>
    '''

    pdf_content = HTML(string=html_content).write_pdf()

    return pdf_content


def send_invoice_email(invoice_number, recipient_email, month_year, auth_user, tenant):
    try:
        subject = f'{tenant.name.capitalize(
        )} - Invoice for {month_year.strftime("%B %Y")}'
        message = f'Dear Sirs,\n\nPlease find attached our invoice for {
            month_year.strftime("%B %Y")}.\n\nKind regards,\n{tenant.name.capitalize()}'

        pdf_content = make_pdf_of_invoice(
            invoice_number, True, auth_user, tenant)
        send_email(message, recipient_email, subject, pdf_content)
        # Attach the PDF to the email
        # pdf_filename = f'invoice_{invoice_number}.pdf'
        # email.attach(pdf_filename, pdf_content, 'application/pdf')

        # email.send()
    except Exception as e:
        return str(e)

    return True


@login_required
def download_invoice(request, invoice_number):
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{
        invoice_number}.pdf'
    pdf_content = make_pdf_of_invoice(
        invoice_number, False, request.user, request.tenant)

    response.write(pdf_content)

    return response


@login_required
def get_invoices_data(request):
    invoices_paid = Invoice.objects.filter(settled=True).count()
    invoices_unpaid = Invoice.objects.filter(settled=False).count()
    data = [invoices_paid, invoices_unpaid]
    labels = ['Paid Invoices', 'Unpaid Invoices']
    return JsonResponse({
        "title": f"Invoices",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Invoices",
                "backgroundColor": [
                    'rgb(37 99 235)',
                    'rgb(59 130 246)',
                ],
                "data": data,
                "hoverOffset": 4,
            }]
        },
    })


@login_required
def get_one_to_one_service_usage_chart(request):

    data = OneToOne.objects.values(
        'customer__name').annotate(total_hours=Sum('hours'))

    labels = [item['customer__name'] for item in data],
    data = [item['total_hours'] for item in data]

    return JsonResponse({
        "title": "One to One services",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Total hours",
                "backgroundColor": 'rgb(147 197 253)',
                "borderColor": 'rgb(37 99 235)',
                "data": data,
                "borderWidth": 1
            }]
        },
    })


@login_required
def get_revenue_data(request):

    nine_months_ago = date.today() - relativedelta(months=6)

    revenue_by_month = Invoice.objects.filter(
        timestamp__gte=nine_months_ago,
        settled=True
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_revenue=Sum('costs')
    ).order_by('month').values()

    months_revenue = {}

    for rev in revenue_by_month:
        date_rev = rev['month']
        total_revenue = rev['total_revenue']
        month_year = f"{date_rev.month}/{date_rev.year}"

        if month_year in months_revenue:
            months_revenue[month_year] += total_revenue
        else:
            months_revenue[month_year] = total_revenue

    previous_revenue = None
    percentage_increases = []

    for month_year, current_revenue in sorted(months_revenue.items()):
        if previous_revenue is not None:
            percentage_increase = (
                (current_revenue - previous_revenue) / previous_revenue) * 100
            percentage_increases.append(percentage_increase)
        previous_revenue = current_revenue

    # Calculate average percentage increase
    if percentage_increases:
        average_percentage_increase = sum(
            percentage_increases) / len(percentage_increases)
    else:
        average_percentage_increase = 1

    today = date.today()
    next_three_months = [today + relativedelta(months=i) for i in range(1, 7)]

    for month in next_three_months:
        month_year = f"{month.month}/{month.year}"
        if previous_revenue is not None:
            projected_revenue = previous_revenue * \
                (1 + Decimal(str(average_percentage_increase)) / 100)
            months_revenue[month_year] = projected_revenue
            previous_revenue = projected_revenue

    data = [str(x.quantize(Decimal('0.00')))
            for key, x in months_revenue.items()]
    labels = [x for x in months_revenue]

    # Return the data as JSON
    chart_data = {
        'labels': labels,
        'datasets': [{
            'label': 'Revenue Over Time',
            'data': data,
            'fill': 'false',
            'borderColor': 'rgb(37 99 235)',
            'tension': 0.1
        }]
    }

    return JsonResponse(chart_data)


def download_invoice_accountants_csv(request):
    if request.method == 'POST':

        date_from = request.POST.get('from_date')

        invoices = Invoice.objects.filter(date__gte=date_from)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="invoices_from_{
            date_from}.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow(['Invoice Number', 'Client', 'Date', 'Description', 'Costs',
                        'Units', 'Settled', 'Sent to Client', 'Additional Notes', 'Timestamp'])

        for invoice in invoices:
            writer.writerow([
                invoice.invoice_number,
                invoice.client.name,
                invoice.date,
                invoice.desc.description,
                invoice.costs,
                invoice.units,
                invoice.settled,
                invoice.sent_to_client,
                invoice.additional_notes,
                invoice.timestamp,
            ])
        return response
    else:
        return render(request, 'accountants_page.html')


def download_monies_in_accountants_csv(request):
    if request.method == 'POST':

        date_from = request.POST.get('from_date')

        moneyin_entries = MoneyIn.objects.filter(date__gte=date_from)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="moneyin_from_{
            date_from}.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow(['ID', 'Payment Type', 'Amount', 'Balance Left',
                        'Description', 'Date', 'Invoices to Allocate', 'Timestamp'])

        for entry in moneyin_entries:
            writer.writerow([
                entry.id,
                entry.payment_type,
                entry.amount,
                entry.balance_left,
                entry.desc,
                entry.date,
                ', '.join([str(invoice.invoice_number)
                          for invoice in entry.invoices_to_allocate.all()]),
                entry.timestamp,
            ])
        return response
    else:
        return render(request, 'accountants_page.html')


def download_creditnote_accountants_csv(request):

    if request.method == 'POST':

        date_from = request.POST.get('from_date')

        creditnote_entries = CreditNote.objects.filter(
            timestamp__gte=date_from)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="creditnotes_from_{
            date_from}.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow(
            ['ID', 'Amount', 'Invoice to Allocate', 'Notes', 'Timestamp'])

        for entry in creditnote_entries:
            writer.writerow([
                entry.id,
                entry.amount,
                entry.invoice_to_allocate.invoice_number,
                entry.notes,
                entry.timestamp,
            ])
        return response
    else:
        return render(request, 'accountants_page.html')
