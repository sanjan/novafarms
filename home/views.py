from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Supplier, SupplierOrder, Customer, HoneyStock, HoneyType, Batch, PAYMENT_TERMS, PRODUCTION_STATUS
from .forms import SupplierForm, CustomerForm
from decimal import Decimal
from datetime import datetime
from django.contrib import messages
import sweetify
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms.models import model_to_dict

# Create your views here.
# @login_required(login_url='/accounts/login-v3/') 

brands =  ['Aldi', 'Costco', 'Fairprice', 'Panda Honey']
bottle_types = ['Squeeze', 'Jar', 'Pail']

def index(request):
    orders = SupplierOrder.objects.all()
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


# # @login_required(login_url='/accounts/login-v3/')  
# def batch_create(request):
#     if request.method == 'POST':
#         date_format = '%d/%m/%Y'
#         batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
#         expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
#         src_containers = request.POST.getlist('source_containers[]')
#         brand = request.POST.get('brand')
#         bottle_type = request.POST.get('bottle-type')
#         unit_weight = int(request.POST.get('unit-weight'))
#         product_name = request.POST.get('product-name')
        
#         batch = Batch.objects.create(
#             batch_date = batch_date,
#             expiry_date = expiry_date,
#             brand = brand,
#             bottle_type = bottle_type,
#             unit_weight = unit_weight,
#             product_name = product_name
#         )
        
#         container_pks = []
#         total_weight = 0
#         for c in src_containers:
#             container = HoneyStock.objects.get(id=c)
#             total_weight += container.net_weight
#             container_pks.append(container.pk)
#         batch.source_containers.add(*container_pks)
#         batch.total_weight = total_weight
#         batch.max_possible = (total_weight * 1000) // unit_weight
#         batch.save()
        
#         new_batch = Batch.objects.get(id=batch.id)     
#         new_batch.qr_pointer = f'https://{request.get_host()}/batch/{new_batch.batch_number}/details'
#         new_batch.save()
        
#         messages.success(request, f'New batch #{new_batch.batch_number} created successfully', extra_tags=new_batch.batch_number)
            
        
#     source_containers = HoneyStock.objects.all()
#     context = {
#         'source_containers': source_containers,
#         'brands': brands,
#         'bottle_types': bottle_types,
#         }
#     return render(request, 'pages/batch_create.html', context)


# def batch_details(request, batch_number):
#     batch = Batch.objects.get(batch_number=batch_number)
    
#     honey_stock = batch.source_containers.all()
    
#     for i in honey_stock:
#         i.net_weight = i.gross_weight - i.ibc_weight
#         i.ht = ', '.join([h.type for h in i.honey_types.all()])
    
#     context = {'batch': batch,
#                'honey_stock': honey_stock,
#             }   
#     return render(request,'pages/batch_details.html', context)


# def batch_edit(request, batch_number):
    
#     if request.method == 'POST':
#         print(request.POST)
#         date_format = '%d/%m/%Y'
#         batch = Batch.objects.get(batch_number=request.POST.get('batch-number'))
#         batch.batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
#         batch.expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
#         src_containers = request.POST.getlist('source_containers[]')
#         batch.brand = request.POST.get('brand')
#         batch.bottle_type = request.POST.get('bottle-type')
#         batch.unit_weight = int(request.POST.get('unit-weight'))
#         batch.product_name = request.POST.get('product-name')
#         batch.number_made  = request.POST.get('number-made')
#         batch.batch_status = request.POST.get('batch-status')
#         batch.max_possible = (batch.total_weight * 1000) // batch.unit_weight
#         batch.save()
        
 
#     batch = Batch.objects.get(batch_number=batch_number)
#     batch.number_made = batch.number_made if batch.number_made else 0
    
#     batch.batch_date = batch.batch_date.strftime("%d/%m/%Y")
#     batch.expiry_date = batch.expiry_date.strftime("%d/%m/%Y")
#     honey_stock = batch.source_containers.all()
#     source_containers = HoneyStock.objects.all()
    
#     for i in source_containers:
#         if i in honey_stock:
#             i.selected = True
#         else:
#             i.selected = False
    
#     context = {
#                 'batch': batch,
#                 'source_containers': source_containers,
#                 'brands': brands,
#                 'bottle_types': bottle_types,
#                 'batch_status' : [s[0] for s in BATCH_STATE]
#             }
    
#     return render(request,'pages/batch_edit.html', context)


# # @login_required(login_url='/accounts/login-v3/')  
def supplier_order_create(request):
    if request.method == 'POST':
        
        supplier = Supplier.objects.get(id=int(request.POST.get('supplier')))
        unit_price = Decimal(request.POST.get('unit_price'))
        payment_term = request.POST.get('payment_term')
        order = SupplierOrder.objects.create(
            supplier = supplier,
            unit_price = unit_price,
            payment_term=payment_term,
        )
        
        # print(request.POST)
        container_weights = request.POST.getlist('container_weights[]')
        gross_weights = request.POST.getlist('gross_weights[]')
        for i in range(len(container_weights)):
            ht_pks = []
            honey_types = request.POST.getlist(f'honey_types_{i+1}[]')
            for ht in honey_types:
                honey_type = HoneyType.objects.get(type=ht)
                ht_pks.append(honey_type.id)
            honey_stock_item = HoneyStock.objects.create(
                order = order,
                ibc_weight = Decimal(container_weights[i]),
                gross_weight = Decimal(gross_weights[i]),
            )
            honey_stock_item.honey_types.add(*ht_pks)
            honey_stock_item.save()
        
        order.save()
        new_order = SupplierOrder.objects.get(id=order.id)        
        new_order.qr_pointer = f'https://{request.get_host()}/supplier/order/{new_order.order_number}/details'
        new_order.save()
        sweetify.success(request, f'Supplier order #{new_order.order_number} created successfully', extra_tags=new_order.order_number)
        return HttpResponseRedirect(reverse('supplier_orders'))

    honey_types = HoneyType.objects.all()
    suppliers = Supplier.objects.all()
    context = {
        'honey_types': honey_types,
        'suppliers': suppliers,
        'payment_terms': [p[0] for p in PAYMENT_TERMS]
        }
    
    return render(request, 'pages/supplier_order_create.html', context)

def supplier_orders(request):
    
    supplier_orders = SupplierOrder.objects.all()
    count = supplier_orders.count()
    context = {
        'supplier_orders': supplier_orders,
        'count': count
    }
    
    return render(request, 'pages/supplier_order_list.html', context)

def supplier_order_details(request, order_number):
    order = SupplierOrder.objects.get(order_number=order_number)
    honey_stock = HoneyStock.objects.filter(order=order.id)    
    for i in honey_stock:
        i.net_weight = i.gross_weight - i.ibc_weight
        i.ht = ', '.join([h.type for h in i.honey_types.all()])
    
    order.save()
    
    context = {'order': order,
            'honey_stock': honey_stock}
    
    return render(request,'pages/supplier_order_details.html', context)

def supplier_order_edit(request, order_number):
    
    if request.method == 'POST':
        print(request.POST)
        date_format = '%d/%m/%Y'
        order_number = request.POST.get('order-number')
        order = SupplierOrder.objects.get(order_number=order_number)
        order.date = datetime.strptime(request.POST.get('order-date'), date_format)
        order.supplier = Supplier.objects.get(id=request.POST.get('supplier'))
        order.unit_price = Decimal(request.POST.get('unit-price'))
        order.payment_term = request.POST.get('payment-term')
        order.save()
        sweetify.success(request, 'Order successfully updated!')
        return HttpResponseRedirect(reverse('supplier_orders'))
        

    order = SupplierOrder.objects.get(order_number=order_number)
    order.date = order.date.strftime("%d/%m/%Y")
    honey_types = HoneyType.objects.all()
    suppliers = Supplier.objects.all()
    context = {
                'order': order,
                'honey_types': honey_types,
                'suppliers': suppliers,
                'payment_terms': [p[0] for p in PAYMENT_TERMS]
            }
    
    return render(request,'pages/supplier_order_edit.html', context)

def suppliers(request):

    suppliers = Supplier.objects.all()
    count = suppliers.count()
            
    context = {
        'suppliers' : suppliers,
        'count' : count,
    }
    return render(request, 'pages/supplier_list.html', context)

    
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    context = {
        'form' : form,
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Supplier was successfully added!')
            return HttpResponseRedirect(reverse('suppliers'))

        else:
            sweetify.error(request, 'Error saving new supplier data')

    return render(request, 'pages/supplier_create.html', context)


def supplier_edit(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            sweetify.success(request, f'Supplier was successfully updated!')
            return HttpResponseRedirect(reverse('suppliers'))

        else:
            sweetify.error(request, 'Error updating supplier data')

    form = SupplierForm(instance=supplier)
    context = {
        'form' : form,
    }
    return render(request, 'pages/supplier_edit.html', context)

def customers(request):

    customers = Customer.objects.all()
    count = customers.count()
            
    context = {
        'customers' : customers,
        'count' : count,
    }
    return render(request, 'pages/customer_list.html', context)

    
def customer_create(request):
    form = CustomerForm(request.POST or None)
    context = {
        'form' : form,
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            sweetify.success(request, ('Customer was successfully added!'))
            return HttpResponseRedirect(reverse('customers'))
        else:
            sweetify.error(request, 'Error saving new customer data')
        

    return render(request, 'pages/customer_create.html', context)


def customer_edit(request, customer_id):
    customer = Customer.objects.get(id=customer_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            sweetify.success(request, f'Customer was successfully updated!')
            return HttpResponseRedirect(reverse('customers'))

        else:
            sweetify.error(request, 'Error updating customer data')

    form = CustomerForm(instance=customer)
    context = {
        'form' : form,
    }
    return render(request, 'pages/customer_edit.html', context)