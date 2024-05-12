from django.contrib import admin
from django.urls import path
from .views import test, invoices_view, add_client, add_local_authority,  add_one_to_one, add_one_to_one_agency, dashboard, clients_attendance, mark_clients_attendance, get_attendance_data
from .views import generate_monthly_attendance_chart, generate_monthly_invoices, edit_invoice, edit_client,edit_local_authority, edit_one_to_one, download_invoice
from .views import send_monthly_invoices, generate_monthly_attendance_table, client_view, add_money_in, edit_money_in, unallocated_money_in, allocate_money_in, get_invoices_data, get_one_to_one_service_usage_chart
from .views import get_revenue_data, all_clients_view, download_all_clients_data, download_all_one_to_ones, download_current_clients_data, download_this_months_one_to_ones, add_credit_note, download_invoice_accountants_csv
from .views import download_monies_in_accountants_csv, download_creditnote_accountants_csv, check_subscription, download_all_invoices, general_invoices, download_contract_document


urlpatterns = [

    path("check_subscription/",check_subscription, name='check_subscription'),

    path("accountants/invoices/",download_invoice_accountants_csv, name='download_accountants_invoices_csv'),
    path("accountants/monies_in/",download_monies_in_accountants_csv, name='download_accountants_monies_in_csv'),
    path("accountants/credit_notes/",download_creditnote_accountants_csv, name='download_accountants_credit_notes_csv'),
    path("invoices/",invoices_view, name='invoices_list'),
    
    path("invoices/actions/",general_invoices, name='invoices_actions'),

    path('invoices/generate_monthly/',generate_monthly_invoices, name='generate_monthly_invoices'),
    path('invoices/send_monthly/',send_monthly_invoices, name='send_monthly_invoices'),
    path("invoice/edit/<int:invoice_number>/",edit_invoice, name='edit_invoice'),

    path("invoice/download/<int:invoice_number>/",download_invoice, name='download_invoice'),
    path("invoice/download/all/",download_all_invoices, name='download_all_invoices'),
    path("credit_note/add/",add_credit_note, name='add_credit_note'),


    
    path('client/<int:client_id>/', client_view, name='client_view'),
    path('clients/', all_clients_view , name='all_clients_view'),
    path('client/add/', add_client, name='add_client' ),
    path('client/edit/<int:id>/', edit_client, name='edit_client' ),
    path('clients/all/download/', download_all_clients_data , name='download_all_clients' ),
    path('clients/current/download/', download_current_clients_data , name='download_current_clients'),

    path('download-contract/<int:client_id>/', download_contract_document, name='download_contract'),


    # path('rate/add/', add_rate, name='add_rate' ),
    # path('rate/edit/<int:id>/', edit_rate, name='edit_rate'),

    path('local_authority/add/', add_local_authority, name='add_local_authority'),
    path('local_authority/edit/<int:id>/', edit_local_authority, name='edit_local_authority'),

    path('one_to_one/add/', add_one_to_one, name='add_one_to_one'),
    path('one_to_one/edit/<int:id>/', edit_one_to_one, name='edit_one_to_one'),
    path('one_to_one/all/download/',download_all_one_to_ones,name='download_all_one_to_ones'),
    path('one_to_one/current/download/',download_this_months_one_to_ones,name='download_this_months_one_to_ones'),


    path('money_in/add/', add_money_in, name='add_money_in'),
    path('money_in/edit/<int:id>/', edit_money_in, name='edit_money_in'),
    path('monies_in/', unallocated_money_in, name='monies_in'),
    path('money_in/allocate/<int:id>/', allocate_money_in, name='allocate_money_in'),

    path('one_to_one_agency/add/', add_one_to_one_agency, name='add_one_to_one_agency'),
    path('clients/attendance/', clients_attendance, name='clients_attendance' ),
    path('clients/attendance/mark/', mark_clients_attendance, name='mark_clients_attendance' ),
   
    path('attendance/data/', get_attendance_data, name='dashboard_attendance_data' ),
    path('invoices/data/', get_invoices_data, name='dashboard_invoices_data' ),
    path('one_to_ones/data/', get_one_to_one_service_usage_chart, name='dashboard_one_to_one_data'),
    path('revenue/data/', get_revenue_data, name='dashboard_revenue_data'),
    
    path('attendance/chart/download/<str:month_year>/',generate_monthly_attendance_chart, name='generate_monthly_attendance_chart' ),
    path('attendance/table/download/<str:month_year>/',generate_monthly_attendance_table, name='generate_monthly_attendance_table' ),

    path("", dashboard, name='index_dashboard'),
 ]