from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Beekeeper, Order, OrderItem, HoneyType, PAYMENT_TERMS
from decimal import Decimal

# Create your views here.
# @login_required(login_url='/accounts/login-v3/')  
def index(request):
    beekeepers = Beekeeper.objects.all()
    orders = Order.objects.all()
    # Page from the theme 
    # return render(request, 'pages/index.html')
    # return redirect('sample_page')
    context = {
        'orders' : orders,
    }
    return render(request, 'pages/application/cust_order_list.html', context)

def order_view(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order.id)
    context = {'order': order,
               'order_items': order_items}
    return render(request,'pages/order_details.html', context)

# @login_required(login_url='/accounts/login-v3/')  
def new_order(request):
    if request.method == 'POST':
        
        bee_keeper = Beekeeper.objects.get(supplier_name=request.POST.get('bee_keeper'))
        unit_price = float(request.POST.get('unit_price'))
        payment_term = request.POST.get('payment_term')
        order = Order.objects.create(
            bee_keeper = bee_keeper,
            unit_price = unit_price,
            payment_term=payment_term,
        )
        
        # print(request.POST)
        order_items = []
        container_weights = request.POST.getlist('container_weights[]')
        gross_weights = request.POST.getlist('gross_weights[]')
        for i in range(len(container_weights)):
            ht_pks = []
            honey_types = request.POST.getlist(f'honey_types_{i+1}[]')
            for ht in honey_types:
                honey_type = HoneyType.objects.get(type=ht)
                ht_pks.append(honey_type.pk)
            order_item = OrderItem.objects.create(
                order = order,
                ibc_weight = Decimal(container_weights[i]),
                gross_weight = Decimal(gross_weights[i]),
            )
            order_item.honey_types.add(*ht_pks)
            order_items.append(order_item.pk)
        

        print(order)
        # order.order_items.add(*order_items)

        

        
    honey_types = HoneyType.objects.all()
    bee_keepers = Beekeeper.objects.all()
    context = {
        'honey_types': honey_types,
        'bee_keepers': bee_keepers,
        'payment_terms': [p[0] for p in PAYMENT_TERMS]
        }
    return render(request, 'pages/new_order.html', context)