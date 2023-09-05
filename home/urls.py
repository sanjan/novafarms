from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('batch/list', views.batch_list, name='batch_list'),
    path('batch/create', views.batch_create, name='batch_create'),
    path('batch/<str:batch_number>/details', views.batch_details, name='batch_details'),
    path('batch/<str:batch_number>/edit', views.batch_edit, name='batch_edit'),
    
    path('customer/order/list', views.customer_order_list, name='customer_orders'),
    path('customer/order/create', views.customer_order_create, name='customer_order_create'),
    path('customer/order/<str:order_number>/details', views.customer_order_details, name='customer_order_details'),
    path('customer/order/<str:order_number>/edit', views.customer_order_edit, name='customer_order_edit'),
    
    path('customers', views.customer_list, name='customers'),   
    path('customer/create', views.customer_create, name='customer_create'),
    # path('customer/<int:customer_id>/details', views.customer_details, name='customer_details'),
    path('customer/<int:customer_id>/edit', views.customer_edit, name='customer_edit'),
    
    path('supplier/order/list', views.supplier_order_list, name='supplier_orders'),
    path('supplier/order/create', views.supplier_order_create, name='supplier_order_create'),
    path('supplier/order/<str:order_number>/details', views.supplier_order_details, name='supplier_order_details'),
    path('supplier/order/<str:order_number>/edit', views.supplier_order_edit, name='supplier_order_edit'),
    
    path('suppliers', views.supplier_list, name='suppliers'),   
    path('supplier/create', views.supplier_create, name='supplier_create'),
    # path('supplier/<int:supplier_id>/details', views.supplier_details, name='supplier_details'),
    path('supplier/<int:supplier_id>/edit', views.supplier_edit, name='supplier_edit'),
    
    path('production/list', views.production_list, name='production_list'),
    path('production/create', views.production_create, name='production_create'),
    # path('production/<str:production_code>/details', views.production_details, name='production_details'),
    path('production/<str:production_code>/edit', views.production_edit, name='production_edit'),
    
    path('products', views.product_list, name='products'),
    path('product/create', views.product_create, name='product_create'),
    path('product/<int:product_id>/details', views.product_details, name='product_details'),
    path('product/<int:product_id>/edit', views.product_edit, name='product_edit'),
    
    path('labels', views.label_list, name='labels'),
    path('label/create', views.label_create, name='label_create'),
    path('label/<int:label_id>/edit', views.label_edit, name='label_edit'),
    
    path('lids', views.lid_list, name='lids'),
    path('lid/create', views.lid_create, name='lid_create'),
    path('lid/<int:lid_id>/edit', views.lid_edit, name='lid_edit'),
    
    path('cartons', views.carton_list, name='cartons'),
    path('carton/create', views.carton_create, name='carton_create'),
    path('carton/<int:carton_id>/edit', views.carton_edit, name='carton_edit'),
    
    path('containers', views.container_list, name='containers'),
    path('container/create', views.container_create, name='container_create'),
    path('container/<int:container_id>/edit', views.container_edit, name='container_edit'),
    
    path('top_inserts', views.top_insert_list, name='top_inserts'),
    path('top_insert/create', views.top_insert_create, name='top_insert_create'),
    path('top_insert/<int:top_insert_id>/edit', views.top_insert_edit, name='top_insert_edit'),
    
    path('pallets', views.pallet_list, name='pallets'),
    path('pallet/create', views.pallet_create, name='pallet_create'),
    path('pallet/<int:pallet_id>/edit', views.pallet_edit, name='pallet_edit'),
    
    path('wizard/', views.ProdCreationWizard.as_view(), name='fomr-wizard'),
    
    ######## v3 #########
    path('accounts/login-v3/', views.UserLoginV3View.as_view(), name='login_v3'),
    path('accounts/register-v3/', views.register_v3, name='register_v3'),
    path('accounts/password-reset-v3/', views.UserPasswordResetV3View.as_view(), name='password_reset_v3'),
    path('accounts/password-change-v3/', views.UserPasswordChangeV3View.as_view(), name='password_change_v3'),
    ######## End v3 #########
]
 