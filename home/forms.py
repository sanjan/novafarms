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
        
        
class DailyProdFormStepOne(forms.Form):
    name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=False)
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        required=False
    )

class DailyProdFormStepTwo(forms.Form):
    product_name = forms.CharField(max_length=30, required=False)
    honey_type = forms.CharField(max_length=50, required=False)