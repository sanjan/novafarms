from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Beekeeper, Order, OrderItem, Honey

# Create your views here.
@login_required(login_url='/accounts/login-v3/')  
def index(request):
    beekeepers = Beekeeper.objects.all()
    orders = Order.objects.all()
    # Page from the theme 
    # return render(request, 'pages/index.html')
    # return redirect('sample_page')
    context = {
        'beekeepers' : beekeepers,
        'orders' : orders,
    }
    return render(request, 'pages/application/cust_order_list.html', context)