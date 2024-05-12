from django import forms
from .models import Client

class ClientAmendmentForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'address', 'bank_name', 'bank_account_name', 
                  'bank_account_no', 'bank_sort_code', 'invoice_footer', 'one_to_one_rate_hourly']

    def __init__(self, *args, **kwargs):
        super(ClientAmendmentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
