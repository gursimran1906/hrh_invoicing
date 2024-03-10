from django import forms

from .models import Client, LocalAuthority, Rate, OneToOne, OneToOneAgency, Invoice, MoneyIn, CreditNote



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'date_left': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LocalAuthorityForm(forms.ModelForm):
    class Meta:
        model = LocalAuthority
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocalAuthorityForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RateForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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
            field.widget.attrs['class'] = 'form-control'

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
        fields = ['client', 'date', 'desc', 'costs', 'units', 'additional_notes']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CreditNoteForm(forms.ModelForm):
    class Meta:
        model = CreditNote
        fields = '__all__'

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class MoneyInForm(forms.ModelForm):
    class Meta:
        model = MoneyIn
        fields = ['date','desc' ,'payment_type', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
