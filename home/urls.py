from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('batch/list', views.batch_list, name='batch_list'),
    path('batch/create', views.batch_create, name='batch_create'),
    path('batch/<str:batch_number>/details', views.batch_details, name='batch_details'),
    path('batch/<str:batch_number>/edit', views.batch_edit, name='batch_edit'),
    
    path('customer/order/list', views.customer_orders, name='customer_orders'),
    path('customer/order/create', views.customer_order_create, name='customer_order_create'),
    path('customer/order/<str:order_number>/details', views.customer_order_details, name='customer_order_details'),
    path('customer/order/<str:order_number>/edit', views.customer_order_edit, name='customer_order_edit'),
    
    path('customers', views.customers, name='customers'),   
    path('customer/create', views.customer_create, name='customer_create'),
    # path('customer/<int:customer_id>/details', views.customer_details, name='customer_details'),
    path('customer/<int:customer_id>/edit', views.customer_edit, name='customer_edit'),
    
    path('supplier/order/list', views.supplier_orders, name='supplier_orders'),
    path('supplier/order/create', views.supplier_order_create, name='supplier_order_create'),
    path('supplier/order/<str:order_number>/details', views.supplier_order_details, name='supplier_order_details'),
    path('supplier/order/<str:order_number>/edit', views.supplier_order_edit, name='supplier_order_edit'),
    
    path('suppliers', views.suppliers, name='suppliers'),   
    path('supplier/create', views.supplier_create, name='supplier_create'),
    # path('supplier/<int:supplier_id>/details', views.supplier_details, name='supplier_details'),
    path('supplier/<int:supplier_id>/edit', views.supplier_edit, name='supplier_edit'),
    
    path('production/list', views.production_list, name='production_list'),
    path('production/create', views.production_create, name='production_create'),
    # path('production/<str:production_code>/details', views.production_details, name='production_details'),
    path('production/<str:production_code>/edit', views.production_edit, name='production_edit'),
    
    path('products', views.products, name='products'),
    path('product/create', views.product_create, name='product_create'),
    path('product/<int:product_id>/details', views.product_details, name='product_details'),
    path('product/<int:product_id>/edit', views.product_edit, name='product_edit'),
    
    path('labels', views.labels, name='labels'),
    path('label/create', views.label_create, name='label_create'),
    path('label/<int:label_id>/edit', views.label_edit, name='label_edit'),
    
    path('lids', views.lids, name='lids'),
    path('lid/create', views.lid_create, name='lid_create'),
    path('lid/<int:lid_id>/edit', views.lid_edit, name='lid_edit'),
    
    path('cartons', views.cartons, name='cartons'),
    path('carton/create', views.carton_create, name='carton_create'),
    path('carton/<int:carton_id>/edit', views.carton_edit, name='carton_edit'),
    
    path('containers', views.containers, name='containers'),
    path('container/create', views.container_create, name='container_create'),
    path('container/<int:container_id>/edit', views.container_edit, name='container_edit'),
]
 