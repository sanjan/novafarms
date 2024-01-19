from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import (Config, Supplier, SupplierOrder, Customer, CustomerOrder, 
                     CustomerOrderItem, HoneyStock, HoneyType, Batch, Product, 
                     Production, Brand, Pallet, Container, Lid, Carton, Label, 
                     TopInsert, SUPPLIER_PAYMENT_TERMS, CUSTOMER_PAYMENT_TERMS,
                     BATCH_STATUS, ORDER_STATUS, HONEY_CONTAINER_TYPES, LID_TYPES,
                     LID_CONTAINER_COLORS, TANK_NUMBERS)
from .forms import SupplierForm, CustomerForm
from decimal import Decimal
from datetime import datetime, timedelta
from django.contrib import messages
import sweetify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from django.db.models import Q
import math
from formtools.wizard.views import SessionWizardView
from .forms import DailyProdFormStepOne, DailyProdFormStepTwo
from django.db.models import Sum
from django.conf import settings

from admin_berry_pro.forms import LoginForm, RegistrationForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views

# Create your views here.
@login_required(login_url='/accounts/login-v3/')
def index(request):
    orders = SupplierOrder.objects.all()
    batches = Batch.objects.all()
    # Page from the theme 
    # return render(request, 'pages/index.html')
    # return redirect('sample_page')
    this_week_units = 0
            
    context = {
        'orders' : orders,
        'batches' : batches,
        'this_week_units': this_week_units,
    }
    return render(request, 'pages/index.html', context)


def increment_supplier_order_invoice_number():
    last_invoice = SupplierOrder.objects.all().order_by('id').last()
    print("last invoice: ", last_invoice)
    date_str = datetime.now().strftime('%d%m%y')
    if not last_invoice:
        print("return default")
        return f"{date_str}001"
    print(last_invoice)
    invoice_no = int(last_invoice.order_number[-3:]) + 1
    new_invoice_no = date_str + str(invoice_no).zfill(3)
    return new_invoice_no

# Supplier
@login_required(login_url='/accounts/login-v3/')
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

    return render(request, 'pages/supplier/supplier_create.html', context)

@login_required(login_url='/accounts/login-v3/')
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
    return render(request, 'pages/supplier/supplier_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def supplier_list(request):

    suppliers = Supplier.objects.all()
    count = suppliers.count()
            
    context = {
        'suppliers' : suppliers,
        'count' : count,
    }
    return render(request, 'pages/supplier/supplier_list.html', context)
 
# Supplier Order
@login_required(login_url='/accounts/login-v3/')
def supplier_order_create(request):
    if request.method == 'POST':
        
        supplier = Supplier.objects.get(id=int(request.POST.get('supplier')))
        unit_price = Decimal(request.POST.get('unit_price'))
        payment_term = request.POST.get('payment_term')
        order = SupplierOrder.objects.create(
            order_number = increment_supplier_order_invoice_number(),
            payment_due_date = datetime.now() if payment_term == 'Immediate' else datetime.now() + timedelta(days=30),
            supplier = supplier,
            unit_price = unit_price,
            payment_term=payment_term,
        )
        
        # print(request.POST)
        ibc_numbers = request.POST.getlist('ibc_numbers[]')
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
                ibc_number = ibc_numbers[i],
                ibc_weight = Decimal(container_weights[i]),
                gross_weight = Decimal(gross_weights[i]),
            )
            honey_stock_item.honey_types.add(*ht_pks)
            honey_stock_item.save()
        
        order.save()
        new_order = SupplierOrder.objects.get(id=order.id)        
        new_order.qr_pointer = f'https://{request.get_host()}/supplier/order/{new_order.order_number}/details'
        new_order.save()
        sweetify.success(request, f'Supplier order #{new_order.order_number} created successfully')
        return HttpResponseRedirect(reverse('supplier_orders'))

    honey_types = HoneyType.objects.all()
    suppliers = Supplier.objects.all()
    context = {
        'honey_types': honey_types,
        'suppliers': suppliers,
        'payment_terms': [p[0] for p in SUPPLIER_PAYMENT_TERMS]
        }
    
    return render(request, 'pages/supplier_order/supplier_order_create.html', context)

@login_required(login_url='/accounts/login-v3/')
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
        order.payment_due_date = datetime.strptime(request.POST.get('due-date'), date_format)
        order.save()
        
        HoneyStock.objects.filter(order=order).delete()
        
        ibc_numbers = request.POST.getlist('ibc_numbers[]')
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
                ibc_number = ibc_numbers[i],
                ibc_weight = Decimal(container_weights[i]),
                gross_weight = Decimal(gross_weights[i]),
            )
            honey_stock_item.honey_types.add(*ht_pks)
            honey_stock_item.save()
        
        order.save()
        
        sweetify.success(request, f'Supplier order #{order.order_number} successfully updated!')
        return HttpResponseRedirect(reverse('supplier_orders'))
        

    order = SupplierOrder.objects.get(order_number=order_number)
    order_items = HoneyStock.objects.filter(order=order)
    for i in order_items:
        i.ht = [h.type for h in i.honey_types.all()]
    order.date = order.date.strftime("%d/%m/%Y")
    honey_types = HoneyType.objects.all()
    suppliers = Supplier.objects.all()
    context = {
                'order': order,
                'order_items': order_items,
                'honey_types': honey_types,
                'suppliers': suppliers,
                'payment_terms': [p[0] for p in SUPPLIER_PAYMENT_TERMS]
            }
    
    return render(request,'pages/supplier_order/supplier_order_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def supplier_order_list(request):
    
    supplier_orders = SupplierOrder.objects.all()
    count = supplier_orders.count()
    context = {
        'supplier_orders': supplier_orders,
        'count': count
    }
    
    return render(request, 'pages/supplier_order/supplier_order_list.html', context)

@login_required(login_url='/accounts/login-v3/')
def supplier_order_details(request, order_number):
    order = SupplierOrder.objects.get(order_number=order_number)
    honey_stock = HoneyStock.objects.filter(order=order.id)    
    for i in honey_stock:
        i.net_weight = i.gross_weight - i.ibc_weight
        i.ht = ', '.join([h.type for h in i.honey_types.all()])
    
    
    
    order.save()
    order.honey_levy = round(order.honey_levy,2)
    config = {config.name: config.value for config in Config.objects.all()}
    context = {'order': order,
            'config' : config,
            'honey_stock': honey_stock,
            'multiplier': settings.HONEY_LEVY_MULTIPLIER,
            }
    
    return render(request,'pages/supplier_order/supplier_order_details.html', context)

# Customer
@login_required(login_url='/accounts/login-v3/')
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
        

    return render(request, 'pages/customer/customer_create.html', context)

@login_required(login_url='/accounts/login-v3/')
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
    return render(request, 'pages/customer/customer_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def customer_list(request):

    customers = Customer.objects.all()
    count = customers.count()
            
    context = {
        'customers' : customers,
        'count' : count,
    }
    return render(request, 'pages/customer/customer_list.html', context)

# Customer Order
@login_required(login_url='/accounts/login-v3/')
def customer_order_create(request):
    if request.method == 'POST':
        customer = Customer.objects.get(id=request.POST.get('customer'))
        payment_term = request.POST.get('payment-term')        
        date_format = '%d/%m/%Y'
        date = datetime.strptime(request.POST.get('order-date'), date_format)
        
        order = CustomerOrder.objects.create(
            customer = customer,
            payment_term = payment_term,
            date = date,
        )
        
        product_ids = request.POST.getlist('product-ids[]')
        quantities = request.POST.getlist('quantities[]')
        unit_prices = request.POST.getlist('unit-prices[]')
        
        for i in range(len(product_ids)):
            customer_order_item = CustomerOrderItem.objects.create(
                order = order,
                product = Product.objects.get(id=product_ids[i]),
                quantity = int(quantities[i]),
                unit_price = Decimal(unit_prices[i]),
                sub_total_price = Decimal( int(quantities[i]) * Decimal(unit_prices[i]))
            )

            customer_order_item.save()
        
        order.save()
        new_order = CustomerOrder.objects.get(id=order.id)        
        new_order.qr_pointer = f'https://{request.get_host()}/customer/order/{new_order.order_number}/details'
        new_order.save()
        sweetify.success(request, f'Customer order #{new_order.order_number} created successfully')
        return HttpResponseRedirect(reverse('customer_orders'))

    products = Product.objects.all()
    customers = Customer.objects.all()

    context = {
        'products': products,
        'customers': customers,
        'payment_terms': [p[0] for p in CUSTOMER_PAYMENT_TERMS]
        }
    
    return render(request, 'pages/customer_order/customer_order_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def customer_order_edit(request, order_number):
    
    if request.method == 'POST':
        order = CustomerOrder.objects.get(order_number=request.POST.get('order-number'))
        order.customer = Customer.objects.get(id=request.POST.get('customer'))
        order.payment_term = request.POST.get('payment-term')        
        date_format = '%d/%m/%Y'
        order.date = datetime.strptime(request.POST.get('order-date'), date_format)
        order.status = request.POST.get('order-status')
        order.save()
        
        CustomerOrderItem.objects.filter(order=order).delete()
        
        product_ids = request.POST.getlist('product-ids[]')
        quantities = request.POST.getlist('quantities[]')
        unit_prices = request.POST.getlist('unit-prices[]')
        
        for i in range(len(product_ids)):
            customer_order_item = CustomerOrderItem.objects.create(
                order = order,
                product = Product.objects.get(id=product_ids[i]),
                quantity = int(quantities[i]),
                unit_price = Decimal(unit_prices[i]),
                sub_total_price = Decimal( int(quantities[i]) * Decimal(unit_prices[i]))
            )

            customer_order_item.save()
        
        order.save()
        
        
        
        sweetify.success(request, f'Customer order #{order.order_number} updated successfully')
        return HttpResponseRedirect(reverse('customer_orders'))
        
        
    order = CustomerOrder.objects.get(order_number=order_number)
    order.date = order.date.strftime("%d/%m/%Y")
    order_items = CustomerOrderItem.objects.filter(order=order)
    products = Product.objects.all()
    customers = Customer.objects.all()
    context = {'order': order,
               'order_items': order_items,
               'products': products,
                'customers': customers,
                'payment_terms': [p[0] for p in CUSTOMER_PAYMENT_TERMS],
                'order_status': [p[0] for p in ORDER_STATUS],
          }
    
    return render(request,'pages/customer_order/customer_order_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def customer_order_list(request):
    customer_orders = CustomerOrder.objects.all()
    
    count = customer_orders.count()
    context = {
        'customer_orders': customer_orders,
        'count': count
    }
    
    return render(request, 'pages/customer_order/customer_order_list.html', context)

@login_required(login_url='/accounts/login-v3/')
def customer_order_details(request, order_number):
    order = CustomerOrder.objects.get(order_number=order_number)
    order_items = CustomerOrderItem.objects.filter(order=order)

    context = {'order': order,
               'order_items': order_items
          }
    
    return render(request,'pages/customer_order/customer_order_details.html', context)

# Batch
@login_required(login_url='/accounts/login-v3/') 
def batch_create(request):
    if request.method == 'POST':
        date_format = '%d/%m/%Y'
        batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        previous_batch = None
        if type(request.POST.get('previous-batch')) == 'int':
            previous_batch = Batch.objects.get(id=request.POST.get('previous-batch'))
        honey_type = request.POST.get('honey-type')
        tank_number =  request.POST.get('tank-number')
        honey_stocks = request.POST.get('honey-stock[]')
        
        batch = Batch.objects.create(
            batch_number = batch_date.strftime('%d%m%y'),
            batch_date = batch_date,
            expiry_date = expiry_date,
            previous_batch = previous_batch,
            honey_type = honey_type,
            tank_number = tank_number,
            weight = 0,
            packed_weight = 0,
            remaining_weight = 0            
        )
        
        hs_pks = []
        total_weight = 0
        for i in honey_stocks or []:
            honey_stock = HoneyStock.objects.get(id=int(i))
            hs_pks.append(honey_stock.id)
            total_weight += honey_stock.net_weight
        if previous_batch:
            total_weight += previous_batch.remaining_weight
        batch.weight = total_weight
        batch.honey_stock.add(*hs_pks)
        batch.save()

        new_batch = Batch.objects.get(id=batch.id)     
        new_batch.qr_pointer = f'https://{request.get_host()}/batch/{new_batch.batch_number}/details'
        new_batch.save()
        
        sweetify.success(request, f'New batch #{new_batch.batch_number} created successfully')
        return HttpResponseRedirect(reverse('batch_list'))
        
        
    # production = Production.objects.filter(~Q(status='Complete'))
    honey_stock = HoneyStock.objects.all()
    previous_batches = Batch.objects.filter(remaining_weight__gt = Decimal(0)).values()
    honey_types = HoneyType.objects.all()
    context = {
        'honey_stock': honey_stock,
        'honey_types': honey_types,
        'tank_numbers': [p[0] for p in TANK_NUMBERS],
        'previous_batches' : previous_batches,
        }
    return render(request, 'pages/batch/batch_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def batch_edit(request, batch_number):
    
    if request.method == 'POST':
        print(request.POST)
        date_format = '%d/%m/%Y'
        batch = Batch.objects.get(batch_number=request.POST.get('batch-number'))
        batch.batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        batch.expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        if request.POST.get('previous-batch'):
            batch.previous_batch = Batch.objects.get(id=request.POST.get('previous-batch'))
        batch.honey_type = request.POST.get('honey-type')
        batch.tank_number =  request.POST.get('tank-number')
        batch.batch_status = request.POST.get('batch-status')
        batch.save()

        honey_stocks = request.POST.getlist('honey-stock[]')
        hs = []
        for i in honey_stocks:
            honey_stock = HoneyStock.objects.get(id=int(i))
            hs.append(honey_stock)
        batch.honey_stock.set(hs)
        batch.save()
        
        sweetify.success(request, f'Batch #{batch.batch_number} updated successfully')
        return HttpResponseRedirect(reverse('batch_list'))
 
    batch = Batch.objects.get(batch_number=batch_number)
    
    batch.batch_date = batch.batch_date.strftime("%d/%m/%Y")
    batch.expiry_date = batch.expiry_date.strftime("%d/%m/%Y")
    batch_honey_stock = batch.honey_stock.all()
    honey_stock = HoneyStock.objects.all()
    previous_batches = Batch.objects.filter(remaining_weight__gt = Decimal(0)).exclude(id=batch.id).values()
    
    honey_types = HoneyType.objects.all()
    
    for i in honey_stock:
        if i in batch_honey_stock:
            i.selected = True
        else:
            i.selected = False
        # print(i,"selected:",i.selected)

    context = {
                'batch': batch,
                'honey_stock': honey_stock,
                'batch_status' : [s[0] for s in BATCH_STATUS],
                'honey_types': honey_types,
                'tank_numbers': [p[0] for p in TANK_NUMBERS],
                'previous_batches' : previous_batches,
            }
    
    return render(request,'pages/batch/batch_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def batch_list(request):
    
    batches = Batch.objects.all()
    count = batches.count()
    context = {
        'batches': batches,
        'count': count
    }
    
    return render(request, 'pages/batch/batch_list.html', context)

@login_required(login_url='/accounts/login-v3/')
def batch_details(request, batch_number):
    
    batch = Batch.objects.get(batch_number=batch_number)
    honey_stock = batch.honey_stock.all()
    production = Production.objects.filter(batch=batch.id)
        
    for h in honey_stock:
        h.ht = ', '.join([a.type for a in h.honey_types.all() ])
    context = {
        'batch': batch,
        'honey_stock' : honey_stock,
        'production' :  production,
    }
    
    return render(request, 'pages/batch/batch_details.html', context)

# Production
@login_required(login_url='/accounts/login-v3/')
def production_create(request):
    if request.method == 'POST':
        date_format = '%d/%m/%Y'
        packing_date = datetime.strptime(request.POST.get('packing_date'), date_format)
        requested_units = int(request.POST.get('requested_units'))
        product = request.POST.get('product')
        batch_id = request.POST.get('batch')
        print(f"product: {product}, batch: {batch_id}")
        if not product:
            return HttpResponseRedirect(reverse('production_create'))
        elif not batch_id:
            return HttpResponseRedirect(reverse('production_create'))

        product = Product.objects.get(id=product)
        
        prd = Production.objects.create(
            packing_date = packing_date,
            production_code =  'p' + packing_date.strftime('%d%m%y') + product.id,
            product = Product.objects.get(id=product),
            requested_units = requested_units,
        )
        
        if batch_id:
            prd.batch = Batch.objects.get(id=int(batch_id))
        prd.save()
        
        sweetify.success(request, f'Daily production set #{prd.production_code} created successfully')
        return HttpResponseRedirect(reverse('production_list'))
         
    products = Product.objects.all()
    pallets = Pallet.objects.all()
    top_inserts = TopInsert.objects.all()
    batches = Batch.objects.filter((~Q(batch_status='Used')))
    
    context = {
        'products' : products,
        'pallets' : pallets,
        'top_inserts' : top_inserts,
        'batches': batches,
    }
    
    return render(request,'pages/production/production_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def production_edit(request, production_code):
    
    if request.method == 'POST':
        print(request.POST)
        production = Production.objects.get(production_code=request.POST.get('production-code'))
        date_format = '%d/%m/%Y'
        production.packing_date = datetime.strptime(request.POST.get('packing-date'), date_format)
        requested_units = int(request.POST.get('requested-units'))
        units_made =  int(request.POST.get('units-made'))
        product_id = request.POST.get('product')

        batch_id = request.POST.get('batch')
        
                

        production.units_made = units_made
        if units_made == 0:
            production.status = 'New'
        elif units_made > 0 and units_made < requested_units and request.POST.get('prod-status'):
            production.status = 'Processing'
        elif production.units_made == requested_units:
            production.status = 'Complete'
        elif not request.POST.get('prod-status') and production.status != 'Complete':
            production.status = 'Paused'
        if requested_units:
            production.requested_units = requested_units
        if product_id:
            product = Product.objects.get(id=product_id)
            production.product = product
        if batch_id:
            production.batch = Batch.objects.get(id=batch_id)
            production.batch.save()
        
        production.save()
        
        sweetify.success(request, f'Daily production set #{production.production_code} updated successfully')
        return HttpResponseRedirect(reverse('production_list'))
            
        
        
    production = Production.objects.get(production_code=production_code)
    production.packing_date = production.packing_date.strftime("%d/%m/%Y")
    products = Product.objects.all() if Product.objects else []
    batches = Batch.objects.filter((~Q(batch_status='Used')))

    context = {
        'production' : production,
        'products' : products,
        'batches': batches,
    }
    
    return render(request,'pages/production/production_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def production_list(request):
    productions = Production.objects.all().order_by("-packing_date") if Production.objects else []
    
    count = 0
    for p in productions:
        count += p.units_made
        
    context = {
        'count': count,
        'productions': productions,
    }
    
    return render(request,'pages/production/production_list.html', context)

@login_required(login_url='/accounts/login-v3/')
def production_details(request, production_code):
    
    production = Production.objects.get(production_code=production_code)
    context = {'production': production,}
    return render(request, 'pages/product/product_details.html', context)

# Product
@login_required(login_url='/accounts/login-v3/')
def product_create(request):
    
    if request.method == 'POST':
        print(request.POST, request.FILES)
        product_name = request.POST.get('product-name')
        brand = request.POST.get('brand')
        container = request.POST.get('container')
        lid  = request.POST.get('lid')
        label = request.POST.get('label')
        carton = request.POST.get('carton')
        pallet = request.POST.get('pallet')
        top_insert = request.POST.get('top-insert')
        unit_weight = request.POST.get('unit-weight') or 0
        cartons_per_layer = request.POST.get('cartons-per-layer') or 0
        layers_per_pallet = request.POST.get('layers-per-pallet') or 0
        image = request.FILES.get('product-image')
        
        product = Product.objects.create(
            name = product_name,
            brand = Brand.objects.get(id=brand),
            container = Container.objects.get(id=container),
            lid = Lid.objects.get(id=lid),
            label = Label.objects.get(id=label),
            unit_weight = int(unit_weight),
            cartons_per_layer = int(cartons_per_layer),
            layers_per_pallet = int(layers_per_pallet),
            image = image,
        )
        
        if carton:
            product.carton = Carton.objects.get(id=carton)
        if pallet:
            product.pallet = Pallet.objects.get(id=pallet)
        if top_insert:    
            product.top_insert = TopInsert.objects.get(id=top_insert)

        product.save()
        
        sweetify.success(request, f'Product #{product.id} created successfully')
        return HttpResponseRedirect(reverse('products'))
        
        
    
    brands = Brand.objects.all()
    containers = Container.objects.all()
    lids = Lid.objects.all()
    labels = Label.objects.all()
    cartons = Carton.objects.all()
    pallets = Pallet.objects.all()
    top_inserts = TopInsert.objects.all()
    
    context = {
        'brands': brands,
        'containers': containers,
        'lids': lids,
        'labels': labels,
        'cartons': cartons,
        'pallets' : pallets,
        'top_inserts' : top_inserts,
    }
    return render(request, 'pages/product/product_create.html', context)
 
@login_required(login_url='/accounts/login-v3/')
def product_edit(request, product_id):
    
    if request.method == 'POST':
        print(request.POST, request.FILES)
        product_id=request.POST.get('product-id')
        product_name = request.POST.get('product-name')
        brand = request.POST.get('brand')
        container = request.POST.get('container')
        lid  = request.POST.get('lid')
        label = request.POST.get('label')
        carton = request.POST.get('carton')
        unit_weight = request.POST.get('unit-weight') or 0
        cartons_per_layer = request.POST.get('cartons-per-layer') or 0
        layers_per_pallet = request.POST.get('layers-per-pallet') or 0
        image = request.FILES.get('product-image')
        pallet = request.POST.get('pallet')
        top_insert = request.POST.get('top-insert')

        product = Product.objects.get(id=product_id)
        product.name = product_name
        product.brand = Brand.objects.get(id=brand)
        product.container = Container.objects.get(id=container)
        product.lid = Lid.objects.get(id=lid)
        product.label = Label.objects.get(id=label)
        product.carton = Carton.objects.get(id=carton)
        product.unit_weight = int(unit_weight)
        product.cartons_per_layer = int(cartons_per_layer)
        product.layers_per_pallet = int(layers_per_pallet)
        product.top_insert = TopInsert.objects.get(id=top_insert) if top_insert else None
        product.pallet =  Pallet.objects.get(id=pallet) if pallet else None
        
        
        if image:
            product.image = image
        product.save()
        
        sweetify.success(request, f'Product #{product.id} updated successfully')
        return HttpResponseRedirect(reverse('products'))    
    
    product = Product.objects.get(id=product_id)
    # maxman = min(product.lid.quantity, product.label.quantity, product.container.quantity)
    # cartons_required = math.ceil(maxman/product.carton.capacity)
    # max_with_cartons = min(product.lid.quantity, product.label.quantity, product.container.quantity, product.carton.capacity * product.carton.quantity)
    brands = Brand.objects.all()
    containers = Container.objects.all()
    lids = Lid.objects.all()
    labels = Label.objects.all()
    cartons = Carton.objects.all()
    pallets = Pallet.objects.all()
    top_inserts = TopInsert.objects.all()
    
    context = {
        'product': product,
        'brands': brands,
        'containers': containers,
        'lids': lids,
        'labels': labels,
        'cartons': cartons,
        'pallets' : pallets,
        'top_inserts' : top_inserts,
        # 'maxman' : maxman,
        # 'max_with_cartons': max_with_cartons,
        # 'cartons_required': cartons_required,
    }
    return render(request, 'pages/product/product_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def product_list(request):
    
    products = Product.objects.all() if Product.objects else []
    
    context = {
        'products' : products,
    }
    
    return render(request, 'pages/product/product_list.html', context)

@login_required(login_url='/accounts/login-v3/')
def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    # maxman = min(product.lid.quantity, product.label.quantity, product.container.quantity)
    # cartons_required = math.ceil(maxman/product.carton.capacity)
    # max_with_cartons = min(product.lid.quantity, product.label.quantity, product.container.quantity, product.carton.capacity * product.carton.quantity)
    
    context = {'product': product,
        # 'maxman' : maxman,
        # 'max_with_cartons': max_with_cartons,
        # 'cartons_required': cartons_required,
        }
    return render(request, 'pages/product/product_details.html', context)

# Carton
@login_required(login_url='/accounts/login-v3/')
def carton_create(request):
    if request.method == 'POST':
        print(request.POST)
        carton = Carton.objects.create(
        name = request.POST.get('carton-name'),
        quantity = int(request.POST.get('quantity')),
        capacity = int(request.POST.get('capacity')),
        image = request.FILES.get('carton-image'),
        )
        
        sweetify.success(request, f'Carton {carton.name} created successfully')
        return HttpResponseRedirect(reverse('cartons'))

    context = {

    }
    
    return render(request, 'pages/carton/carton_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def carton_edit(request, carton_id):
    if request.method == 'POST':
        print(request.POST)
        carton = Carton.objects.get(id=request.POST.get('carton-id'))
        carton.name = request.POST.get('carton-name')
        carton.quantity = int(request.POST.get('quantity'))
        carton.capacity = int(request.POST.get('capacity'))
        image = request.FILES.get('carton-image')
        if image:
            carton.image = image
        carton.save()
        
        sweetify.success(request, f'Carton {carton.name} updated successfully')
        return HttpResponseRedirect(reverse('cartons'))
        
        
    carton = Carton.objects.get(id=carton_id)

    context = {
        'carton' : carton,
    }
    
    return render(request, 'pages/carton/carton_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def carton_list(request):
    
    cartons = Carton.objects.all() if Carton.objects else []
    
    context = {
        'cartons' : cartons,
    }
    
    return render(request, 'pages/carton/carton_list.html', context)

# Container
@login_required(login_url='/accounts/login-v3/')
def container_create(request):
    if request.method == 'POST':
        print(request.POST)
        container = Container.objects.create(
            name = request.POST.get('container-name'),
            quantity = int(request.POST.get('quantity')),
            color = request.POST.get('container-color'),
            type = request.POST.get('container-type'),
            capacity = int(request.POST.get('capacity')),
            image = request.FILES.get('container-image')
            )

        
        sweetify.success(request, f'Container {container.name} created successfully')
        return HttpResponseRedirect(reverse('containers'))
        


    context = {
        'container_colors': [p[0] for p in LID_CONTAINER_COLORS],
        'container_types': [p[0] for p in HONEY_CONTAINER_TYPES],
    }
    
    return render(request, 'pages/container/container_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def container_edit(request, container_id):
    if request.method == 'POST':
        print(request.POST)
        container = Container.objects.get(id=request.POST.get('container-id'))
        container.name = request.POST.get('container-name')
        container.quantity = int(request.POST.get('quantity'))
        container.color = request.POST.get('container-color')
        container.type = request.POST.get('container-type')
        container.capacity = int(request.POST.get('capacity'))
        image = request.FILES.get('container-image')
        if image:
            container.image = image
        container.save()
        
        sweetify.success(request, f'Container {container.name} updated successfully')
        return HttpResponseRedirect(reverse('containers'))
        
        
    container = Container.objects.get(id=container_id)

    context = {
        'container_colors': [p[0] for p in LID_CONTAINER_COLORS],
        'container_types': [p[0] for p in HONEY_CONTAINER_TYPES],
        'container' : container,
    }
    
    return render(request, 'pages/container/container_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def container_list(request):
    
    containers = Container.objects.all() if Container.objects else []
    count = containers.count()
    context = {
        'containers' : containers,
        'count' :count,
    }
    
    return render(request, 'pages/container/container_list.html', context)

# Label
@login_required(login_url='/accounts/login-v3/')
def label_create(request):
    if request.method == 'POST':
        print(request.POST)
        label = Label.objects.create(
            name = request.POST.get('label-name'),
            quantity = int(request.POST.get('quantity')),
            brand = Brand.objects.get(id=request.POST.get('brand')),
            image = request.FILES.get('label-image'),
        )
        
        sweetify.success(request, f'Label {label.name} created successfully')
        return HttpResponseRedirect(reverse('labels'))
        
    brands = Brand.objects.all()
    context = {
        'brands': brands,
    }
    
    return render(request, 'pages/label/label_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def label_edit(request, label_id):
    if request.method == 'POST':
        print(request.POST)
        label = Label.objects.get(id=request.POST.get('label-id'))
        label.name = request.POST.get('label-name')
        label.quantity = int(request.POST.get('quantity'))
        label.brand = Brand.objects.get(id=request.POST.get('brand'))
        image = request.FILES.get('label-image')
        if image:
            label.image = image
        label.save()
        
        sweetify.success(request, f'Label {label.name} updated successfully')
        return HttpResponseRedirect(reverse('labels'))
        
        
    label = Label.objects.get(id=label_id)
    brands = Brand.objects.all()
    context = {
        'brands': brands,
        'label' : label,
    }
    
    return render(request, 'pages/label/label_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def label_list(request):
    
    labels = Label.objects.all() if Label.objects else []
    
    context = {
        'labels' : labels,
    }
    
    return render(request, 'pages/label/label_list.html', context)

# Lid
@login_required(login_url='/accounts/login-v3/')
def lid_create(request):
    if request.method == 'POST':
        print(request.POST)
        lid = Lid.objects.create(
        name = request.POST.get('lid-name'),
        quantity = int(request.POST.get('quantity')),
        color = request.POST.get('lid-color'),
        type = request.POST.get('lid-type'),
        image = request.FILES.get('lid-image'),
        )
  
        
        sweetify.success(request, f'Lid {lid.name} created successfully')
        return HttpResponseRedirect(reverse('lids'))

    context = {
        'lid_colors': [p[0] for p in LID_CONTAINER_COLORS],
        'lid_types': [p[0] for p in LID_TYPES],
    }
    
    return render(request, 'pages/lid/lid_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def lid_edit(request, lid_id):
    if request.method == 'POST':
        print(request.POST)
        lid = Lid.objects.get(id=request.POST.get('lid-id'))
        lid.name = request.POST.get('lid-name')
        lid.quantity = int(request.POST.get('quantity'))
        lid.color = request.POST.get('lid-color')
        lid.type = request.POST.get('lid-type')
        image = request.FILES.get('lid-image')
        if image:
            lid.image = image
        lid.save()
        
        sweetify.success(request, f'Lid {lid.name} updated successfully')
        return HttpResponseRedirect(reverse('lids'))
        
        
    lid = Lid.objects.get(id=lid_id)

    context = {
        'lid_colors': [p[0] for p in LID_CONTAINER_COLORS],
        'lid_types': [p[0] for p in LID_TYPES],
        'lid' : lid,
    }
    
    return render(request, 'pages/lid/lid_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def lid_list(request):
    
    lids = Lid.objects.all() if Lid.objects else []
    
    context = {
        'lids' : lids,
    }
    
    return render(request, 'pages/lid/lid_list.html', context)

# Pallet
@login_required(login_url='/accounts/login-v3/')
def pallet_create(request):
    if request.method == 'POST':
        print(request.POST)
        pallet = Pallet.objects.create(
            name = request.POST.get('pallet-name'),
            pallet_number = request.POST.get('pallet-number'),
            quantity = int(request.POST.get('quantity')),
            length = request.POST.get('pallet-length'),
            width = request.POST.get('pallet-width'),
            capacity_cartons = int(request.POST.get('pallet-cartons')),
            layout = request.FILES.get('pallet-layout'),
        )
  
        sweetify.success(request, f'Pallet: {pallet.name} created successfully')
        return HttpResponseRedirect(reverse('pallets'))

    context = {

    }
    
    return render(request, 'pages/pallet/pallet_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def pallet_edit(request, pallet_id):
    if request.method == 'POST':
        print(request.POST)
        pallet = Lid.objects.get(id=request.POST.get('pallet-id'))
        pallet.name = request.POST.get('pallet-name')
        pallet.quantity = int(request.POST.get('quantity'))
        pallet.length = request.POST.get('pallet-length')
        pallet.width = request.POST.get('pallet-width')
        pallet.capacity_cartons = int(request.POST.get('pallet-cartons')),
        layout = request.FILES.get('pallet-layout')
        if layout:
            pallet.layout = layout
        pallet.save()
        
        sweetify.success(request, f'Pallet {pallet.name} updated successfully')
        return HttpResponseRedirect(reverse('pallets'))
        
        
    pallet = Pallet.objects.get(id=pallet_id)

    context = {
        'pallet' : pallet,
    }
    
    return render(request, 'pages/pallet/pallet_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def pallet_list(request):
    pallets = Pallet.objects.all() if Pallet.objects else []
    
    context = {
        'pallets' : pallets,
    }
    
    return render(request, 'pages/pallet/pallet_list.html', context)

# Top Insert
@login_required(login_url='/accounts/login-v3/')
def top_insert_create(request):
    if request.method == 'POST':
        print(request.POST)
        top_insert = TopInsert.objects.create(
        name = request.POST.get('topinsert-name'),
        length = request.POST.get('topinsert-length'),
        width = request.POST.get('topinsert-width'),
        quantity = int(request.POST.get('quantity')),
        image = request.FILES.get('topinsert-image'),
        )
  
        
        sweetify.success(request, f'Top Insert: {top_insert.name} created successfully')
        return HttpResponseRedirect(reverse('top_inserts'))

    context = {
    }
    
    return render(request, 'pages/top_insert/top_insert_create.html', context)

@login_required(login_url='/accounts/login-v3/')
def top_insert_edit(request, top_insert_id):
    if request.method == 'POST':
        print(request.POST)
        top_insert = TopInsert.objects.get(id=request.POST.get('topinsert-id'))
        top_insert.name = request.POST.get('topinsert-name')
        top_insert.quantity = int(request.POST.get('quantity'))
        top_insert.length = request.POST.get('topinsert-length')
        top_insert.width = request.POST.get('topinsert-width')
        image = request.FILES.get('topinsert-image')
        if image:
            top_insert.image = image
        top_insert.save()
    
        sweetify.success(request, f'Top Insert: {top_insert.name} updated successfully')
        return HttpResponseRedirect(reverse('top_inserts'))
        
        
    top_insert = TopInsert.objects.get(id=top_insert_id)

    context = {
        'top_insert' : top_insert,
    }
    
    return render(request, 'pages/top_insert/top_insert_edit.html', context)

@login_required(login_url='/accounts/login-v3/')
def top_insert_list(request):
    top_inserts = TopInsert.objects.all() if TopInsert.objects else []
    
    context = {
        'top_inserts' : top_inserts,
    }
    
    return render(request, 'pages/top_insert/top_insert_list.html', context)



######## Start v3 #########
def register_v3(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      print('Account created successfully!')
      return redirect('/accounts/login-v3/')
    else:
      print("Registration failed!")
  else:
    form = RegistrationForm()
  
  context = {'form': form}
  return render(request, 'accounts/register-v3.html', context)

class UserLoginV3View(auth_views.LoginView):
  template_name = 'accounts/login-v3.html'
  form_class = LoginForm
  success_url = '/'

class UserPasswordChangeV3View(auth_views.PasswordChangeView):
  template_name = 'accounts/password-change-v3.html'
  form_class = UserPasswordChangeForm

class UserPasswordResetV3View(auth_views.PasswordResetView):
  template_name = 'accounts/forgot-password-v3.html'
  form_class = UserPasswordResetForm

######## End v3 #########


######## Common #########
class UserPasswordResetConfirmV1View(auth_views.PasswordResetConfirmView):
  template_name = 'accounts/reset-password-v3.html'
  form_class = UserSetPasswordForm

def user_logout_view(request):
  logout(request)
  return redirect('/accounts/login-v3/')

######## End Common #########

# Additional Stuff
class ProdCreationWizard(SessionWizardView):
    
    template_name = "forms/production_wizard.html"
    form_list = [DailyProdFormStepOne, DailyProdFormStepTwo]
    
    def done(self, form_list, **kwargs):
        
        return render(self.request, 'forms/production_complete.html', {'form_data': [form.cleaned_data for form in form_list]} )