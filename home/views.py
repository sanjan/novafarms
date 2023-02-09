from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Beekeeper, Order, OrderItem, HoneyType, Batch, PAYMENT_TERMS, BATCH_STATE
from decimal import Decimal
from datetime import datetime
import qrcode
from django.conf import settings
from django.contrib import messages
# Create your views here.
# @login_required(login_url='/accounts/login-v3/') 

brands =  ['Aldi', 'Costco', 'Fairprice', 'Panda Honey']
bottle_types = ['Squeeze', 'Jar', 'Pail']

def index(request):
    orders = Order.objects.all()
    batches = Batch.objects.all()
    # Page from the theme 
    # return render(request, 'pages/index.html')
    # return redirect('sample_page')
    this_week_units = 0
    for b in batches:
        if b.number_made:
            this_week_units += b.number_made
            
    context = {
        'orders' : orders,
        'batches' : batches,
        'this_week_units': this_week_units,
    }
    return render(request, 'pages/index.html', context)

def order_details(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order_items = OrderItem.objects.filter(order=order.id)    
    for i in order_items:
        i.net_weight = i.gross_weight - i.ibc_weight
        i.ht = ', '.join([h.type for h in i.honey_types.all()])
    
    order.save()
    
    context = {'order': order,
            'order_items': order_items}
    
    return render(request,'pages/order_details.html', context)

def batch_details(request, batch_number):
    batch = Batch.objects.get(batch_number=batch_number)
    
    order_items = batch.source_containers.all()
    
    for i in order_items:
        i.net_weight = i.gross_weight - i.ibc_weight
        i.ht = ', '.join([h.type for h in i.honey_types.all()])
    
    context = {'batch': batch,
               'order_items': order_items,
            }
    
    return render(request,'pages/batch_details.html', context)

def edit_order(request, order_number):
    
    if request.method == 'POST':
        print(request.POST)
        date_format = '%d/%m/%Y'
        order = Order.objects.get(order_number=request.POST.get('order-number'))
        order.date = datetime.strptime(request.POST.get('order-date'), date_format)
        order.bee_keeper = Beekeeper.objects.get(supplier_name=request.POST.get('beekeeper'))
        order.unit_price = Decimal(request.POST.get('unit-price'))
        order.payment_term = request.POST.get('payment-term')
        order.save()

    order = Order.objects.get(order_number=order_number)
    order.date = order.date.strftime("%d/%m/%Y")
    honey_types = HoneyType.objects.all()
    bee_keepers = Beekeeper.objects.all()
    context = {
                'order': order,
                'honey_types': honey_types,
                'bee_keepers': bee_keepers,
                'payment_terms': [p[0] for p in PAYMENT_TERMS]
            }
    
    return render(request,'pages/edit_order.html', context)

def edit_batch(request, batch_number):
    
    if request.method == 'POST':
        print(request.POST)
        date_format = '%d/%m/%Y'
        batch = Batch.objects.get(batch_number=request.POST.get('batch-number'))
        batch.batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        batch.expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        src_containers = request.POST.getlist('source_containers[]')
        batch.brand = request.POST.get('brand')
        batch.bottle_type = request.POST.get('bottle-type')
        batch.unit_weight = int(request.POST.get('unit-weight'))
        batch.product_name = request.POST.get('product-name')
        batch.number_made  = request.POST.get('number-made')
        batch.batch_status = request.POST.get('batch-status')
        batch.max_possible = (batch.total_weight * 1000) // batch.unit_weight
        batch.save()
        
 
    batch = Batch.objects.get(batch_number=batch_number)
    batch.number_made = batch.number_made if batch.number_made else 0
    
    batch.batch_date = batch.batch_date.strftime("%d/%m/%Y")
    batch.expiry_date = batch.expiry_date.strftime("%d/%m/%Y")
    order_items = batch.source_containers.all()
    source_containers = OrderItem.objects.all()
    
    for i in source_containers:
        if i in order_items:
            i.selected = True
        else:
            i.selected = False
    
    context = {
                'batch': batch,
                'source_containers': source_containers,
                'brands': brands,
                'bottle_types': bottle_types,
                'batch_status' : [s[0] for s in BATCH_STATE]
            }
    
    return render(request,'pages/edit_batch.html', context)

# @login_required(login_url='/accounts/login-v3/')  
def new_order(request):
    if request.method == 'POST':
        
        bee_keeper = Beekeeper.objects.get(supplier_name=request.POST.get('bee_keeper'))
        unit_price = Decimal(request.POST.get('unit_price'))
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
        
        order.save()
        new_order = Order.objects.get(id=order.id)        
        new_order.qr_pointer = f'https://{request.get_host()}/order-details/{new_order.order_number}/'
        new_order.save()
        messages.success(request, f'Order #{new_order.order_number} created successfully', extra_tags=new_order.order_number)

    honey_types = HoneyType.objects.all()
    bee_keepers = Beekeeper.objects.all()
    context = {
        'honey_types': honey_types,
        'bee_keepers': bee_keepers,
        'payment_terms': [p[0] for p in PAYMENT_TERMS]
        }
    return render(request, 'pages/new_order.html', context)


# @login_required(login_url='/accounts/login-v3/')  
def new_batch(request):
    if request.method == 'POST':
        date_format = '%d/%m/%Y'
        batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        src_containers = request.POST.getlist('source_containers[]')
        brand = request.POST.get('brand')
        bottle_type = request.POST.get('bottle-type')
        unit_weight = int(request.POST.get('unit-weight'))
        product_name = request.POST.get('product-name')
        
        batch = Batch.objects.create(
            batch_date = batch_date,
            expiry_date = expiry_date,
            brand = brand,
            bottle_type = bottle_type,
            unit_weight = unit_weight,
            product_name = product_name
        )
        
        container_pks = []
        total_weight = 0
        for c in src_containers:
            container = OrderItem.objects.get(id=c)
            container.used = True
            total_weight += container.net_weight
            container.save()
            container_pks.append(container.pk)
        batch.source_containers.add(*container_pks)
        batch.total_weight = total_weight
        batch.max_possible = (total_weight * 1000) // unit_weight
        batch.save()
        
        new_batch = Batch.objects.get(id=batch.id)     
        new_batch.qr_pointer = f'https://{request.get_host()}/batch-details/{new_batch.batch_number}/'
        new_batch.save()
        
        messages.success(request, f'New batch #{new_batch.batch_number} created successfully', extra_tags=new_batch.batch_number)
            
        
    source_containers = OrderItem.objects.filter(used=False)
    context = {
        'source_containers': source_containers,
        'brands': brands,
        'bottle_types': bottle_types,
       
        }
    return render(request, 'pages/new_batch.html', context)
