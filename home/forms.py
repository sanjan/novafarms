from django import forms
from .models import Beekeeper, Order, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['bee_keeper', 'unit_price', 'immediate_payment', 'date' ]