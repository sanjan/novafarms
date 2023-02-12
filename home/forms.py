from django import forms
from .models import Supplier, Customer, HoneyType, Brand


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"