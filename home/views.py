from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Beekeeper, Order, OrderItem, Honey
from .forms import OrderForm

# Create your views here.
@login_required(login_url='/accounts/login-v3/')  
def index(request):
    beekeepers = Beekeeper.objects.all()
    orders = Order.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
    else:
        form = OrderForm()
    # Page from the theme 
    # return render(request, 'pages/index.html')
    # return redirect('sample_page')
    context = {
        'beekeepers' : beekeepers,
        'orders' : orders,
        'form': form,
    }
    return render(request, 'pages/application/cust_order_list.html', context)