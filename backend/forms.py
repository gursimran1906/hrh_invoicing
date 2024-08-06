from django import forms
from django.forms import formset_factory
from .models import Client, LocalAuthority,  OneToOne, OneToOneAgency, Invoice, MoneyIn, CreditNote, ContractDocument
import json

class RateSubForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    description = forms.CharField(max_length=100, required=False)
    status = forms.ChoiceField(choices=[('active', 'Active'), ('inactive', 'Inactive')], required=False)

    def __init__(self, *args, **kwargs):
        super(RateSubForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
    
class ClientFullFormToSave(forms.ModelForm):
   

    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_left': forms.DateInput(attrs={'type': 'date'}),
        }
class ClientFullForm(forms.ModelForm):
   

    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_left': forms.DateInput(attrs={'type': 'date'}),
        }
        

    def __init__(self, *args, **kwargs):
        super(ClientFullForm, self).__init__(*args, **kwargs)

        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        if 'rates' in self.fields:
            del self.fields['rates']

        if self.instance.pk:
            rates_data = self.instance.rates
           
            if rates_data:
                rates_dicts = json.loads(rates_data) if type(rates_data) == type('ss') else rates_data
                
                RateFormSet = formset_factory(RateSubForm, extra=0)
                
                self.rates_formset = RateFormSet(initial=rates_dicts)
                for idx, rate_data in enumerate(rates_dicts):
                    if rate_data.get('status') == 'inactive':
                        for field_name, field in self.rates_formset.forms[idx].fields.items():
                            value = self.rates_formset.forms[idx].initial.get(field_name, field.initial)
                            field.widget = forms.TextInput(attrs={'readonly': 'readonly'})

                          
        # if self.instance.pk:
        #     rates_data = self.instance.rates
        #     if rates_data:
        #         print(type(rates_data))
        #         rates = json.loads(rates_data) 
        #         for rate in rates:
        #             self.initial['amount'] = rate.get('amount')
        #             self.initial['status'] = rate.get('status')
        #             self.initial['description'] = rate.get('description')

    # def clean_rates(self):
    #     data = self.cleaned_data['rates']
    #     try:
    #         # Parse the JSON data
    #         rates_dict = json.loads(data)
    #     except json.JSONDecodeError:
    #         raise forms.ValidationError("Invalid JSON format")
        
    #     # Check if all required keys are present
    #     if not all(key in rates_dict for key in ['amount', 'status', 'description']):
    #         raise forms.ValidationError("JSON data must contain keys: amount, status, description")
        
    #     return rates_dict

# class ClientFullForm(forms.ModelForm):
#     class Meta:
#         model = Client
       
#         fields = '__all__'
#         widgets = {
#             'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
#             'date_joined': forms.DateInput(attrs={'type': 'date'}),
#             'date_left': forms.DateInput(attrs={'type': 'date'}),
#         }
        

#     def __init__(self, *args, **kwargs):
#         super(ClientFullForm, self).__init__(*args, **kwargs)

#         # Add Bootstrap classes to form fields
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'


class ClientHalfForm(forms.ModelForm):
    class Meta:
        model = Client
       
        fields = ['name','date_of_birth', 'address', 'contact_number','email','date_joined', 'client_type','payable_by','resident_name_number', 'respite','notes']

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_left': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Name'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter Address'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter Contact Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
            'client_type': forms.Select(attrs={'placeholder': 'Select Client Type'}),
            # 'payable_by': forms.TextInput(attrs={'placeholder': 'If privately funded leave blank'}),
            'resident_name_number': forms.TextInput(attrs={'placeholder': 'Enter Resident Name/Number provided by authority'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Enter notes'}),
        }

    def __init__(self, *args, **kwargs):
        super(ClientHalfForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'

class LocalAuthorityForm(forms.ModelForm):
    class Meta:
        model = LocalAuthority
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocalAuthorityForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'


# class RateForm(forms.ModelForm):
#     class Meta:
#         model = Rate
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super(RateForm, self).__init__(*args, **kwargs)

#         # Add Bootstrap classes to form fields
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'


class OneToOneForm(forms.ModelForm):
    class Meta:
        model = OneToOne
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(OneToOneForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'


class OneToOneAgencyForm(forms.ModelForm):
    class Meta:
        model = OneToOneAgency
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OneToOneAgencyForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'date', 'desc',
                  'costs', 'units','rate', 'additional_notes']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'



class CreditNoteForm(forms.ModelForm):
    class Meta:
        model = CreditNote
        fields = '__all__'

        widgets = {
            'notes': forms.TextInput(attrs={'placeholder':'Reason(s) to issue a credit note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'


class MoneyInForm(forms.ModelForm):
    class Meta:
        model = MoneyIn
        fields = ['date', 'desc', 'payment_type', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'desc': forms.TextInput(attrs={'placeholder':'Payment from '}),
            'payment_type':forms.TextInput(attrs={'placeholder': 'Bank Transfer, Cash, Cheque or etc...'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'shadow-sm mb-2 mt-1 border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-100 focus:border-blue-100 block w-full p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
    


class ContractDocumentForm(forms.ModelForm):
    class Meta:
        model = ContractDocument
        fields = ['document']
    document = forms.FileField(required=False)
