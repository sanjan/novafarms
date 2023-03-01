from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Supplier, SupplierOrder, Customer, CustomerOrder, CustomerOrderItem, HoneyStock, HoneyType, Batch, Product, Production, Brand, Pallet, Container, Lid, Carton, Label, TopInsert, SUPPLIER_PAYMENT_TERMS, CUSTOMER_PAYMENT_TERMS, PRODUCTION_STATUS, BATCH_STATUS, ORDER_STATUS
from .forms import SupplierForm, CustomerForm
from decimal import Decimal
from datetime import datetime
from django.contrib import messages
import sweetify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from django.db.models import Q

# Create your views here.
# @login_required(login_url='/accounts/login-v3/') 

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

# @login_required(login_url='/accounts/login-v3/')  
def batch_create(request):
    if request.method == 'POST':
        date_format = '%d/%m/%Y'
        batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        honey_stocks = request.POST.get('honey_stock[]')
        
        batch = Batch.objects.create(
            batch_date = batch_date,
            expiry_date = expiry_date,
        )
        
        hs_pks = []
        for i in honey_stocks or []:
            honey_stock = HoneyStock.objects.get(id=int(i))
            hs_pks.append(honey_stock.id)
        batch.honey_stock.add(*hs_pks)
        batch.save()

        new_batch = Batch.objects.get(id=batch.id)     
        new_batch.qr_pointer = f'https://{request.get_host()}/batch/{new_batch.batch_number}/details'
        new_batch.save()
        
        sweetify.success(request, f'New batch #{new_batch.batch_number} created successfully')
        return HttpResponseRedirect(reverse('batch_list'))
        
        
    # production = Production.objects.filter(~Q(status='Complete'))
    honey_stock = HoneyStock.objects.all()
    context = {
        'honey_stock': honey_stock,
        }
    return render(request, 'pages/batch_create.html', context)

def batch_edit(request, batch_number):
    
    if request.method == 'POST':
        print(request.POST)
        date_format = '%d/%m/%Y'
        batch = Batch.objects.get(batch_number=request.POST.get('batch-number'))
        batch.batch_date = datetime.strptime(request.POST.get('batch-date'), date_format) 
        batch.expiry_date = datetime.strptime(request.POST.get('expiry-date'), date_format)
        batch.batch_status = request.POST.get('batch-status')
        batch.save()

        honey_stocks = request.POST.getlist('honey_stock[]')
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
    
    
    for i in honey_stock:
        if i in batch_honey_stock:
            i.selected = True
        else:
            i.selected = False
        print(i,"selected:",i.selected)
    
    context = {
                'batch': batch,
                'honey_stock': honey_stock,
                'batch_status' : [s[0] for s in BATCH_STATUS]
            }
    
    return render(request,'pages/batch_edit.html', context)

def batch_list(request):
    
    batches = Batch.objects.all()
    count = batches.count()
    context = {
        'batches': batches,
        'count': count
    }
    
    return render(request, 'pages/batch_list.html', context)

def batch_details(request, batch_number):
    
    batch = Batch.objects.get(batch_number=batch_number)
    honey_stock = batch.honey_stock.all()
    for h in honey_stock:
        h.ht = ', '.join([a.type for a in h.honey_types.all() ])
    context = {
        'batch': batch,
        'honey_stock' : honey_stock,
    }
    
    return render(request, 'pages/batch_details.html', context)

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
        sweetify.success(request, f'Supplier order #{new_order.order_number} created successfully')
        return HttpResponseRedirect(reverse('supplier_orders'))

    honey_types = HoneyType.objects.all()
    suppliers = Supplier.objects.all()
    context = {
        'honey_types': honey_types,
        'suppliers': suppliers,
        'payment_terms': [p[0] for p in SUPPLIER_PAYMENT_TERMS]
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
        
        HoneyStock.objects.filter(order=order).delete()
        
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

def production_create(request):
    if request.method == 'POST':
        date_format = '%d/%m/%Y'
        packing_date = datetime.strptime(request.POST.get('packing-date'), date_format)
        requested_units = int(request.POST.get('requested-units'))
        order_item_id = request.POST.get('order')
        if order_item_id:
            order_item = CustomerOrderItem.objects.get(id=int(order_item_id))
            if order_item and order_item.quantity < requested_units:
                sweetify.error(request, f'Requested number of units greater than ordered quantity')
                return HttpResponse('form error')
                
        pallet = request.POST.get('pallet')
        top_insert = request.POST.get('top-insert')
        batch_id = request.POST.get('batch')

        
        prd = Production.objects.create(
            packing_date = packing_date,
            pallet = Pallet.objects.get(id=pallet),
            top_insert = TopInsert.objects.get(id=top_insert),
            requested_units = requested_units,
        )
        
        if batch_id:
            prd.batch = Batch.objects.get(id=int(batch_id))
        if order_item_id:
            prd.order_item = CustomerOrderItem.objects.get(id=int(order_item_id))
        prd.save()
        
        sweetify.success(request, f'Daily production set #{prd.production_code} created successfully')
        return HttpResponseRedirect(reverse('production_list'))
         
    order_items = CustomerOrderItem.objects.all()
    pallets = Pallet.objects.all()
    top_inserts = TopInsert.objects.all()
    batches = Batch.objects.filter((~Q(batch_status='Used')))
    
    context = {
        'order_items' : order_items,
        'pallets' : pallets,
        'top_inserts' : top_inserts,
        'batches': batches,
    }
    
    return render(request,'pages/production_create.html', context)

def production_edit(request, production_code):
    
    if request.method == 'POST':
        print(request.POST)
        production = Production.objects.get(production_code=request.POST.get('production-code'))
        date_format = '%d/%m/%Y'
        production.packing_date = datetime.strptime(request.POST.get('packing-date'), date_format)
        production.requested_units = int(request.POST.get('requested-units'))
        production.units_made =  int(request.POST.get('units-made'))
    
        production.save()
        
        order_item_id = request.POST.get('order')
        pallet_id = request.POST.get('pallet')
        top_insert_id = request.POST.get('top-insert')
        batch_id = request.POST.get('batch')
        
        if order_item_id:
            order_item = CustomerOrderItem.objects.get(id=order_item_id)
            if order_item and order_item.quantity < production.requested_units:
                sweetify.error(request, f'Requested number of units greater than ordered quantity')
                return redirect(request.META['HTTP_REFERER'])
            production.order_item = order_item
        if pallet_id:
            production.pallet = Pallet.objects.get(id=pallet_id)
        if top_insert_id:
            production.top_insert = TopInsert.objects.get(id=top_insert_id)
        if batch_id:
            production.batch = Batch.objects.get(id=batch_id)
        
        if production.units_made == 0:
            production.status = 'New'
        elif production.units_made > 0 and production.units_made < production.requested_units:
            production.status = 'Processing'
        elif production.units_made == production.requested_units:
            production.status = 'Complete'
        
        if not request.POST.get('prod-status'):
            production.status = 'Paused'
        
        production.save()
        
        sweetify.success(request, f'Daily production set #{production.production_code} updated successfully')
        return HttpResponseRedirect(reverse('production_list'))
            
        
        
    production = Production.objects.get(production_code=production_code)
    production.packing_date = production.packing_date.strftime("%d/%m/%Y")
    order_items = CustomerOrderItem.objects.all()
    pallets = Pallet.objects.all()
    top_inserts = TopInsert.objects.all()
    batches = Batch.objects.filter((~Q(batch_status='Used')))

    context = {
        'production' : production,
        'order_items' : order_items,
        'pallets' : pallets,
        'top_inserts' : top_inserts,
        'batches': batches,
    }
    
    return render(request,'pages/production_edit.html', context)

def production_list(request):
    productions = Production.objects.all() if Production.objects else []
    
    context = {
        'productions': productions,
    }
    
    return render(request,'pages/production_list.html', context)

def products(request):
    
    products = Product.objects.all() if Product.objects else []
    
    context = {
        'products' : products,
    }
    
    return render(request, 'pages/product_list.html', context)

def product_create(request):
    
    if request.method == 'POST':
        print(request.POST, request.FILES)
        product_name = request.POST.get('product-name')
        brand = request.POST.get('brand')
        container = request.POST.get('container')
        lid  = request.POST.get('lid')
        label = request.POST.get('label')
        carton = request.POST.get('carton')
        unit_weight = request.POST.get('unit-weight') or 0
        image = request.FILES.get('product-image')
        
        product = Product.objects.create(
            name = product_name,
            brand = Brand.objects.get(id=brand),
            container = Container.objects.get(id=container),
            lid = Lid.objects.get(id=lid),
            label = Label.objects.get(id=label),
            carton = Carton.objects.get(id=carton),
            unit_weight = int(unit_weight),
            image = image,
        )
        
        sweetify.success(request, f'Product #{product.id} created successfully')
        return HttpResponseRedirect(reverse('products'))
        
        
    
    brands = Brand.objects.all()
    containers = Container.objects.all()
    lids = Lid.objects.all()
    labels = Label.objects.all()
    cartons = Carton.objects.all()
    
    context = {
        'brands': brands,
        'containers': containers,
        'lids': lids,
        'labels': labels,
        'cartons': cartons,
    }
    return render(request, 'pages/product_create.html', context)

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
        image = request.FILES.get('product-image')

        product = Product.objects.get(id=product_id)
        product.name = product_name
        product.brand = Brand.objects.get(id=brand)
        product.container = Container.objects.get(id=container)
        product.lid = Lid.objects.get(id=lid)
        product.label = Label.objects.get(id=label)
        product.carton = Carton.objects.get(id=carton)
        product.unit_weight = int(unit_weight)
        if image:
            product.image = image
        product.save()
        
        sweetify.success(request, f'Product #{product.id} updated successfully')
        return HttpResponseRedirect(reverse('products'))    
    
    product = Product.objects.get(id=product_id)
    brands = Brand.objects.all()
    containers = Container.objects.all()
    lids = Lid.objects.all()
    labels = Label.objects.all()
    cartons = Carton.objects.all()
    context = {
        'product': product,
        'brands': brands,
        'containers': containers,
        'lids': lids,
        'labels': labels,
        'cartons': cartons,
    }
    return render(request, 'pages/product_edit.html', context)

def product_details(request, product_id):
    context = {}
    return render(request, 'pages/product_details.html', context)

def customer_orders(request):
    customer_orders = CustomerOrder.objects.all()
    
    count = customer_orders.count()
    context = {
        'customer_orders': customer_orders,
        'count': count
    }
    
    return render(request, 'pages/customer_order_list.html', context)

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
    
    return render(request, 'pages/customer_order_create.html', context)


def customer_order_details(request, order_number):
    order = CustomerOrder.objects.get(order_number=order_number)
    order_items = CustomerOrderItem.objects.filter(order=order)

    context = {'order': order,
               'order_items': order_items
          }
    
    return render(request,'pages/customer_order_details.html', context)

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
    
    return render(request,'pages/customer_order_edit.html', context)

def labels(request):
    
    labels = Label.objects.all() if Label.objects else []
    
    context = {
        'labels' : labels,
    }
    
    return render(request, 'pages/label_list.html', context)

def label_create(request):
    pass

def label_edit(request, label_id):
    pass

def containers(request):
    
    containers = Container.objects.all() if Container.objects else []
    
    context = {
        'containers' : containers,
    }
    
    return render(request, 'pages/container_list.html', context)

def container_create(request):
    pass

def container_edit(request, container_id):
    pass


def lids(request):
    
    lids = Lid.objects.all() if Lid.objects else []
    
    context = {
        'lids' : lids,
    }
    
    return render(request, 'pages/lid_list.html', context)

def lid_create(request):
    pass

def lid_edit(request, lid_id):
    pass


def cartons(request):
    
    cartons = Carton.objects.all() if Carton.objects else []
    
    context = {
        'cartons' : cartons,
    }
    
    return render(request, 'pages/carton_list.html', context)

def carton_create(request):
    pass
def carton_edit(request, carton_id):
    pass